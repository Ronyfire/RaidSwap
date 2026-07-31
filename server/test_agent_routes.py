from unittest.mock import patch


def make_boss(client, **overrides):
    data = {"name": "Test Boss", "raid": "The Venomous Abyss", "order": 1}
    data.update(overrides)
    return client.post("/api/bosses", json=data).get_json()


def make_responsibility(client, **overrides):
    data = {"name": "Interrupt"}
    data.update(overrides)
    return client.post("/api/responsibilities", json=data).get_json()


def make_raider(client, **overrides):
    data = {"name": "Rob", "wow_class": "Warrior", "spec": "Arms", "role": "DPS"}
    data.update(overrides)
    return client.post("/api/raiders", json=data).get_json()


@patch("routes.agent.run_agent_turn")
def test_chat_requires_messages(mock_run, client):
    resp = client.post("/api/agent/chat", json={})
    assert resp.status_code == 400
    mock_run.assert_not_called()


@patch("routes.agent.run_agent_turn")
def test_chat_delegates_to_agent_service(mock_run, client):
    mock_run.return_value = {"message": "hi there", "proposal": None}

    resp = client.post("/api/agent/chat", json={"messages": [{"role": "user", "content": "hi"}]})

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "hi there", "proposal": None}
    mock_run.assert_called_once_with([{"role": "user", "content": "hi"}], boss_id=None)


@patch("routes.agent.run_agent_turn")
def test_chat_passes_boss_id_through(mock_run, client):
    mock_run.return_value = {"message": "hi there", "proposal": None}

    client.post(
        "/api/agent/chat",
        json={"messages": [{"role": "user", "content": "hi"}], "boss_id": 3},
    )

    mock_run.assert_called_once_with([{"role": "user", "content": "hi"}], boss_id=3)


def test_apply_requires_proposal(client):
    resp = client.post("/api/agent/apply", json={})
    assert resp.status_code == 400


def test_apply_commits_a_valid_proposal(client):
    boss = make_boss(client)
    resp = make_responsibility(client)
    client.post(
        "/api/positions",
        json={"x": 1, "y": 1, "boss_id": boss["id"], "responsibility_id": resp["id"]},
    )
    raider = make_raider(client)

    apply_resp = client.post(
        "/api/agent/apply",
        json={"proposal": {"responsibility_name": "Interrupt", "to_raider_name": "Rob"}},
    )

    assert apply_resp.status_code == 200
    assert apply_resp.get_json()["assignment"]["raider_id"] == raider["id"]


def test_apply_rejects_unknown_raider(client):
    make_responsibility(client)
    resp = client.post(
        "/api/agent/apply",
        json={"proposal": {"responsibility_name": "Interrupt", "to_raider_name": "Nobody"}},
    )
    assert resp.status_code == 400


def test_apply_is_rate_limited_past_the_free_tier_cooldown(client):
    boss = make_boss(client)
    resp = make_responsibility(client)
    client.post(
        "/api/positions",
        json={"x": 1, "y": 1, "boss_id": boss["id"], "responsibility_id": resp["id"]},
    )
    make_raider(client)

    proposal = {"responsibility_name": "Interrupt", "to_raider_name": "Rob"}
    for _ in range(5):
        assert client.post("/api/agent/apply", json={"proposal": proposal}).status_code == 200

    limited_resp = client.post("/api/agent/apply", json={"proposal": proposal})
    assert limited_resp.status_code == 429
    assert limited_resp.get_json()["retry_after_seconds"] > 0
