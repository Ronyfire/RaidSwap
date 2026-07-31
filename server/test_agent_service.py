import json
from types import SimpleNamespace
from unittest.mock import patch

from services.agent_service import run_agent_turn


def _tool_call(call_id, name, arguments):
    return SimpleNamespace(
        id=call_id, function=SimpleNamespace(name=name, arguments=json.dumps(arguments))
    )


def _response(content=None, tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _fake_client(*responses, captured_calls=None):
    """A stand-in for the OpenAI client: returns each response in sequence."""
    remaining = list(responses)

    def create(**kwargs):
        if captured_calls is not None:
            captured_calls.append(kwargs)
        return remaining.pop(0)

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


@patch("services.agent_service._get_client")
def test_run_agent_turn_direct_reply_no_tools(mock_get_client):
    mock_get_client.return_value = _fake_client(_response(content="Hey there!"))

    result = run_agent_turn([{"role": "user", "content": "hi"}])

    assert result == {"message": "Hey there!", "proposal": None}


@patch("services.agent_service._get_client")
def test_run_agent_turn_calls_get_roster_then_replies(mock_get_client, client):
    client.post(
        "/api/raiders", json={"name": "Rob", "wow_class": "Warrior", "spec": "Arms", "role": "DPS"}
    )
    mock_get_client.return_value = _fake_client(
        _response(tool_calls=[_tool_call("call_1", "get_roster", {})]),
        _response(content="You have Rob, a DPS Warrior."),
    )

    result = run_agent_turn([{"role": "user", "content": "who's on the roster?"}])

    assert result == {"message": "You have Rob, a DPS Warrior.", "proposal": None}


@patch("services.agent_service._get_client")
def test_run_agent_turn_captures_pending_proposal(mock_get_client, client):
    boss = client.post(
        "/api/bosses", json={"name": "Test Boss", "raid": "The Venomous Abyss", "order": 1}
    ).get_json()
    resp = client.post("/api/responsibilities", json={"name": "Interrupt"}).get_json()
    client.post(
        "/api/positions",
        json={"x": 1, "y": 1, "boss_id": boss["id"], "responsibility_id": resp["id"]},
    )
    client.post(
        "/api/raiders", json={"name": "New", "wow_class": "Mage", "spec": "Frost", "role": "DPS"}
    )

    mock_get_client.return_value = _fake_client(
        _response(
            tool_calls=[
                _tool_call(
                    "call_1",
                    "propose_reassignment",
                    {
                        "boss_name": "Test Boss",
                        "responsibility_name": "Interrupt",
                        "new_raider_name": "New",
                    },
                )
            ]
        ),
        _response(content="I'd put New on Interrupt — want me to apply it?"),
    )

    result = run_agent_turn([{"role": "user", "content": "put New on interrupt"}])

    assert result["message"] == "I'd put New on Interrupt — want me to apply it?"
    assert result["proposal"]["to_raider_name"] == "New"
    assert result["proposal"]["responsibility_name"] == "Interrupt"


@patch("services.agent_service._get_client")
def test_run_agent_turn_injects_boss_context_when_boss_id_given(mock_get_client, client):
    boss = client.post(
        "/api/bosses", json={"name": "Test Boss", "raid": "The Venomous Abyss", "order": 1}
    ).get_json()
    resp = client.post("/api/responsibilities", json={"name": "Interrupt"}).get_json()
    client.post(
        "/api/positions",
        json={"x": 1, "y": 1, "boss_id": boss["id"], "responsibility_id": resp["id"]},
    )

    calls = []
    mock_get_client.return_value = _fake_client(
        _response(content="Sure thing"), captured_calls=calls
    )

    run_agent_turn([{"role": "user", "content": "hi"}], boss_id=boss["id"])

    system_messages = [m["content"] for m in calls[0]["messages"] if m["role"] == "system"]
    assert len(system_messages) == 2
    assert "Test Boss" in system_messages[1]
    assert "Interrupt" in system_messages[1]


@patch("services.agent_service._get_client")
def test_run_agent_turn_without_boss_id_has_no_context_message(mock_get_client):
    calls = []
    mock_get_client.return_value = _fake_client(
        _response(content="Sure thing"), captured_calls=calls
    )

    run_agent_turn([{"role": "user", "content": "hi"}])

    system_messages = [m["content"] for m in calls[0]["messages"] if m["role"] == "system"]
    assert len(system_messages) == 1


@patch("services.agent_service._get_client")
def test_run_agent_turn_unknown_boss_id_skips_context_silently(mock_get_client, client):
    calls = []
    mock_get_client.return_value = _fake_client(
        _response(content="Sure thing"), captured_calls=calls
    )

    result = run_agent_turn([{"role": "user", "content": "hi"}], boss_id=999)

    system_messages = [m["content"] for m in calls[0]["messages"] if m["role"] == "system"]
    assert len(system_messages) == 1
    assert result["message"] == "Sure thing"


@patch("services.agent_service._get_client")
def test_run_agent_turn_gives_up_after_max_iterations(mock_get_client, client):
    # Model keeps calling tools forever — loop must not hang.
    infinite_tool_call = _response(tool_calls=[_tool_call("call_1", "get_roster", {})])
    mock_get_client.return_value = _fake_client(*([infinite_tool_call] * 5))

    result = run_agent_turn([{"role": "user", "content": "hi"}])

    assert "couldn't finish" in result["message"]
