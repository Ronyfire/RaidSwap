import pytest

from models import Raider
from seeds.curation import seed_curation
from seeds.venomous_abyss import seed_venomous_abyss
from services.agent_tools import (
    apply_reassignment,
    get_boss_context,
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


def test_apply_reassignment_flips_incoming_bench_raider_to_active(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt", note_line="tag:Old;")
    link_to_boss(client, boss["id"], resp["id"])
    old_raider = make_raider(client, name="Old")
    bench_raider = make_raider(client, name="Bench", status="bench")
    client.post(
        "/api/assignments", json={"raider_id": old_raider["id"], "responsibility_id": resp["id"]}
    )

    proposal = propose_reassignment(boss["name"], "Interrupt", "Bench")
    apply_reassignment(proposal)

    assert client.get(f"/api/raiders/{bench_raider['id']}").get_json()["status"] == "active"


def test_apply_reassignment_flips_outgoing_raider_to_bench(client):
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt", note_line="tag:Old;")
    link_to_boss(client, boss["id"], resp["id"])
    old_raider = make_raider(client, name="Old")
    new_raider = make_raider(client, name="New")
    client.post(
        "/api/assignments", json={"raider_id": old_raider["id"], "responsibility_id": resp["id"]}
    )

    proposal = propose_reassignment(boss["name"], "Interrupt", "New")
    apply_reassignment(proposal)

    assert client.get(f"/api/raiders/{old_raider['id']}").get_json()["status"] == "bench"


def test_apply_reassignment_keeps_active_count_stable_for_a_swap(client):
    # A 1-for-1 swap (bench raider in, active raider out) must not change the
    # active headcount — Mythic's invariant is exactly 20.
    boss = make_boss(client)
    resp = make_responsibility(client, name="Interrupt", note_line="tag:Old;")
    link_to_boss(client, boss["id"], resp["id"])
    old_raider = make_raider(client, name="Old", status="active")
    bench_raider = make_raider(client, name="Bench", status="bench")
    client.post(
        "/api/assignments", json={"raider_id": old_raider["id"], "responsibility_id": resp["id"]}
    )
    active_before = len(
        [r for r in client.get("/api/raiders").get_json() if r["status"] == "active"]
    )

    proposal = propose_reassignment(boss["name"], "Interrupt", "Bench")
    apply_reassignment(proposal)

    raiders = client.get("/api/raiders").get_json()
    active_after = len([r for r in raiders if r["status"] == "active"])
    assert active_after == active_before
    assert next(r for r in raiders if r["name"] == "Bench")["status"] == "active"
    assert next(r for r in raiders if r["name"] == "Old")["status"] == "bench"


def test_apply_reassignment_keeps_demo_roster_at_20_active(client):
    seed_venomous_abyss()
    seed_curation()
    assert Raider.query.filter_by(status="active").count() == 20

    proposal = propose_reassignment(
        "Nek'zali the Soulcoiler", "Interrupt Soulcoil Ritual", "Quill"
    )
    apply_reassignment(proposal)

    assert Raider.query.filter_by(status="active").count() == 20
    assert Raider.query.filter_by(name="Quill").first().status == "active"
    assert Raider.query.filter_by(name="Sylvi").first().status == "bench"


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


def test_get_boss_context_returns_boss_name_and_responsibilities(client):
    boss = make_boss(client)
    interrupt = make_responsibility(client, name="Interrupt")
    tank_swap = make_responsibility(client, name="Tank swap")
    link_to_boss(client, boss["id"], interrupt["id"])
    link_to_boss(client, boss["id"], tank_swap["id"])

    context = get_boss_context(boss["id"])

    assert context["boss_name"] == "Nek'zali the Soulcoiler"
    assert set(context["responsibility_names"]) == {"Interrupt", "Tank swap"}


def test_get_boss_context_unknown_boss_returns_none(client):
    assert get_boss_context(999) is None


def test_get_boss_context_ignores_positions_without_responsibility(client):
    boss = make_boss(client)
    client.post("/api/positions", json={"x": 1, "y": 1, "boss_id": boss["id"]})

    context = get_boss_context(boss["id"])

    assert context["responsibility_names"] == []
