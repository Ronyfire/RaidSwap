import pytest

from services.agent_tools import (
    apply_reassignment,
    get_mechanic_profile,
    get_roster,
    propose_reassignment,
)


def make_raider(client, **overrides):
    data = {"name": "Testorix", "wow_class": "Mage", "spec": "Frost", "role": "DPS"}
    data.update(overrides)
    return client.post("/api/raiders", json=data).get_json()


def make_boss(client, **overrides):
    data = {"name": "Nek'zali the Soulcoiler", "raid": "The Venomous Abyss", "order": 1}
    data.update(overrides)
    return client.post("/api/bosses", json=data).get_json()


def make_responsibility(client, **overrides):
    data = {"name": "Kick rotation"}
    data.update(overrides)
    return client.post("/api/responsibilities", json=data).get_json()


def link_to_boss(client, boss_id, responsibility_id):
    client.post(
        "/api/positions",
        json={"x": 1, "y": 1, "boss_id": boss_id, "responsibility_id": responsibility_id},
    )


def test_get_roster(client):
    make_raider(client, name="Rob")
    make_raider(client, name="Sam")

    result = get_roster()
    names = {r["name"] for r in result["raiders"]}
    assert names == {"Rob", "Sam"}


def test_get_mechanic_profile_found(client):
    raider = make_raider(client, name="Rob")
    resp = make_responsibility(client, name="Interrupt")
    client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider["id"],
            "responsibility_id": resp["id"],
            "proficiency_level": "mastered",
        },
    )

    result = get_mechanic_profile("Rob", "Interrupt")
    assert result == {
        "found": True,
        "raider_name": "Rob",
        "responsibility_name": "Interrupt",
        "proficiency_level": "mastered",
    }


def test_get_mechanic_profile_no_profile_yet(client):
    make_raider(client, name="Rob")
    make_responsibility(client, name="Interrupt")

    result = get_mechanic_profile("Rob", "Interrupt")
    assert result["found"] is True
    assert result["proficiency_level"] is None


def test_get_mechanic_profile_raider_not_found(client):
    make_responsibility(client, name="Interrupt")
    result = get_mechanic_profile("Nobody", "Interrupt")
    assert result["found"] is False


def test_propose_reassignment_confirmed(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt", requires_role="DPS")
    link_to_boss(client, boss["id"], resp["id"])
    old_raider = make_raider(client, name="Old", role="DPS")
    new_raider = make_raider(client, name="New", role="DPS")
    client.post(
        "/api/assignments", json={"raider_id": old_raider["id"], "responsibility_id": resp["id"]}
    )
    client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": new_raider["id"],
            "responsibility_id": resp["id"],
            "proficiency_level": "has_done_it",
        },
    )

    result = propose_reassignment(boss["name"], "Interrupt", "New")
    assert result == {
        "boss_name": boss["name"],
        "responsibility_name": "Interrupt",
        "from_raider_name": "Old",
        "to_raider_name": "New",
        "confidence": "confirmed",
    }


def test_propose_reassignment_unknown_confidence_no_profile(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt")
    link_to_boss(client, boss["id"], resp["id"])
    make_raider(client, name="New")

    result = propose_reassignment(boss["name"], "Interrupt", "New")
    assert result["confidence"] == "unknown"
    assert result["from_raider_name"] is None


def test_propose_reassignment_unassigned_responsibility_still_works(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt")
    link_to_boss(client, boss["id"], resp["id"])
    make_raider(client, name="New")

    result = propose_reassignment(boss["name"], "Interrupt", "New")
    assert "error" not in result
    assert result["from_raider_name"] is None


def test_propose_reassignment_boss_not_found(client):
    result = propose_reassignment("Nobody's Boss", "Interrupt", "New")
    assert "error" in result


def test_propose_reassignment_responsibility_not_linked_to_boss(client):
    boss = make_boss(client)
    make_responsibility(client, name="Interrupt")
    make_raider(client, name="New")

    result = propose_reassignment(boss["name"], "Interrupt", "New")
    assert "error" in result


def test_propose_reassignment_raider_not_found(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt")
    link_to_boss(client, boss["id"], resp["id"])

    result = propose_reassignment(boss["name"], "Interrupt", "Nobody")
    assert "error" in result


def test_propose_reassignment_role_incompatible(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Taunt swap", requires_role="Tank")
    link_to_boss(client, boss["id"], resp["id"])
    make_raider(client, name="Healy", role="Healer")

    result = propose_reassignment(boss["name"], "Taunt swap", "Healy")
    assert "error" in result


def test_apply_reassignment_creates_new_assignment(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt", note_line="tag:;")
    link_to_boss(client, boss["id"], resp["id"])
    make_raider(client, name="New")

    proposal = propose_reassignment(boss["name"], "Interrupt", "New")
    result = apply_reassignment(proposal)

    assert result["assignment"]["raider_id"] is not None
    assert result["responsibility"]["note_line"] == "tag:;"  # no previous assignee to swap out


def test_apply_reassignment_updates_existing_and_swaps_note_tag(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt", note_line="time:0;tag:Old;")
    link_to_boss(client, boss["id"], resp["id"])
    old_raider = make_raider(client, name="Old")
    new_raider = make_raider(client, name="New")
    client.post(
        "/api/assignments", json={"raider_id": old_raider["id"], "responsibility_id": resp["id"]}
    )

    proposal = propose_reassignment(boss["name"], "Interrupt", "New")
    result = apply_reassignment(proposal)

    assert result["assignment"]["raider_id"] == new_raider["id"]
    assert result["responsibility"]["note_line"] == "time:0;tag:New;"


def test_apply_reassignment_role_incompatible_raises(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Taunt swap", requires_role="Tank")
    link_to_boss(client, boss["id"], resp["id"])
    make_raider(client, name="Healy", role="Healer")

    with pytest.raises(ValueError):
        apply_reassignment(
            {
                "responsibility_name": "Taunt swap",
                "to_raider_name": "Healy",
            }
        )


def test_apply_reassignment_raider_not_found_raises(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt")
    link_to_boss(client, boss["id"], resp["id"])

    with pytest.raises(ValueError):
        apply_reassignment({"responsibility_name": "Interrupt", "to_raider_name": "Nobody"})
