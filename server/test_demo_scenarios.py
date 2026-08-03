"""Pre-demo verification battery — deterministic cases only (see the model
e2e cases, run manually against the fixed OPENROUTER_MODEL, in the PR
description / session report, not here — they can't be made deterministic
in CI).

Each test is numbered to match the case list from the pre-demo verification
request, so a failing test maps directly back to "what not to show".
"""

from extensions import db
from models import Assignment, Boss, Position, Raider, Responsibility
from seeds.curation import seed_curation
from seeds.venomous_abyss import seed_venomous_abyss
from services.agent_tools import apply_reassignment, propose_reassignment
from services.note_service import assemble_boss_note


def _seed(app):
    seed_venomous_abyss()
    seed_curation()


def _active_count():
    return Raider.query.filter_by(status="active").count()


def _apply(boss_name, responsibility_name, to_raider_name):
    proposal = propose_reassignment(boss_name, responsibility_name, to_raider_name)
    assert "error" not in proposal, proposal
    return apply_reassignment(proposal)


# --- HAPPY PATH ---


def test_case_1_dps_to_dps_with_mechanic_sylvi_to_quill(app):
    _seed(app)
    result = _apply("Nek'zali the Soulcoiler", "Interrupt Soulcoil Ritual", "Quill")

    assert result["responsibility"]["note_line"] == "ph:1;tag:Quill;"
    assert Raider.query.filter_by(name="Quill").first().status == "active"
    assert Raider.query.filter_by(name="Sylvi").first().status == "bench"
    assert _active_count() == 20


def test_case_2_tank_to_tank_paco_to_maren(app):
    _seed(app)
    result = _apply("Entombed Sentinels", "Tank Blood of Ula'tek", "Maren")

    assert result["responsibility"]["note_line"] == "tag:Maren;"
    assert Raider.query.filter_by(name="Maren").first().status == "active"
    assert Raider.query.filter_by(name="Paco").first().status == "bench"
    assert _active_count() == 20


def test_case_3_healer_to_healer_kaeli_to_cillian(app):
    _seed(app)
    result = _apply("Nek'zali the Soulcoiler", "Venom pulse heal CD", "Cillian")

    assert result["responsibility"]["note_line"] == "ph:2;tag:Cillian;"
    assert Raider.query.filter_by(name="Cillian").first().status == "active"
    assert Raider.query.filter_by(name="Kaeli").first().status == "bench"
    assert _active_count() == 20


def test_case_4_bench_dps_no_mechanic_profile_replaces_a_shared_responsibility(app):
    """"Spirit adds" has TWO current assignees (Doran + Ilse) — the proposal/
    apply contract only carries a responsibility + incoming raider name, no
    "which of the two current assignees" field. apply_reassignment's lookup
    (`Assignment.query.filter_by(responsibility_id=...).first()`) picks
    whichever assignment row comes first with no ORDER BY — there is no
    guarantee it's Ilse specifically. This test documents the actual
    behavior rather than assuming the user's intended target is honored.
    """
    seed_venomous_abyss()
    seed_curation()
    responsibility = Responsibility.query.filter_by(name="Spirit adds").first()
    before_names = {a.raider.name for a in responsibility.assignments}
    assert before_names == {"Doran", "Ilse"}

    replaced_name = Assignment.query.filter_by(responsibility_id=responsibility.id).first().raider.name

    result = _apply("Nek'zali the Soulcoiler", "Spirit adds", "Dagen")

    after_names = {a.raider.name for a in Responsibility.query.filter_by(name="Spirit adds").first().assignments}
    # Whichever of the two got replaced, Dagen is in and that one is out —
    # but WHICH one is not something the caller controls today.
    assert after_names == (before_names - {replaced_name}) | {"Dagen"}
    assert Raider.query.filter_by(name="Dagen").first().status == "active"
    assert _active_count() == 20
    # The note_line only had ONE of the two tags actually swapped (the one
    # matching the replaced assignment's prior raider name) — confirms the
    # ambiguity is real, not just in the assignments table.
    assert "tag:Dagen;" in result["responsibility"]["note_line"]


# --- GUARDRAILS ---


def test_case_5_role_incompatible_healer_into_dps_responsibility(app):
    _seed(app)
    result = propose_reassignment(
        "Nek'zali the Soulcoiler", "Interrupt Soulcoil Ritual", "Kaeli"
    )

    assert "error" in result
    assert "Kaeli" in result["error"] and "DPS" in result["error"]
    # nothing changed
    assert (
        Responsibility.query.filter_by(name="Interrupt Soulcoil Ritual").first().note_line
        == "ph:1;tag:Sylvi;"
    )
    assert _active_count() == 20


def test_case_6_role_incompatible_tank_into_dps_responsibility(app):
    _seed(app)
    result = propose_reassignment("Sszorak", "Howling Maelstrom burn (Bloodlust)", "Maren")

    assert "error" in result
    assert (
        Responsibility.query.filter_by(name="Howling Maelstrom burn (Bloodlust)").first().note_line
        == "ph:2;tag:Ilse;"
    )
    assert _active_count() == 20


def test_case_7_nonexistent_raider(app):
    _seed(app)
    result = propose_reassignment(
        "Nek'zali the Soulcoiler", "Interrupt Soulcoil Ritual", "Xyzzyx"
    )

    assert "error" in result
    assert (
        Responsibility.query.filter_by(name="Interrupt Soulcoil Ritual").first().note_line
        == "ph:1;tag:Sylvi;"
    )
    assert _active_count() == 20


def test_case_8_nonexistent_responsibility(app):
    _seed(app)
    result = propose_reassignment("Nek'zali the Soulcoiler", "Nonexistent Duty", "Quill")

    assert "error" in result
    assert _active_count() == 20


# --- INVARIANTE ---


def test_case_9_active_count_stays_20_after_bench_to_active_swap(app):
    _seed(app)
    assert _active_count() == 20

    _apply("Nek'zali the Soulcoiler", "Interrupt Soulcoil Ritual", "Quill")

    assert _active_count() == 20
    assert Raider.query.filter_by(name="Quill").first().status == "active"
    assert Raider.query.filter_by(name="Sylvi").first().status == "bench"


def test_case_10_swap_and_swap_back_returns_to_original_state(app):
    _seed(app)
    assert _active_count() == 20

    _apply("Nek'zali the Soulcoiler", "Interrupt Soulcoil Ritual", "Quill")
    assert _active_count() == 20

    _apply("Nek'zali the Soulcoiler", "Interrupt Soulcoil Ritual", "Sylvi")

    assert _active_count() == 20
    assert Raider.query.filter_by(name="Sylvi").first().status == "active"
    assert Raider.query.filter_by(name="Quill").first().status == "bench"
    assert (
        Responsibility.query.filter_by(name="Interrupt Soulcoil Ritual").first().note_line
        == "ph:1;tag:Sylvi;"
    )


# --- EXPORT (#64) ---


def test_case_11_export_reflects_a_swap(app):
    _seed(app)
    boss_id = Boss.query.filter_by(name="Nek'zali the Soulcoiler").first().id

    before = assemble_boss_note(boss_id)
    assert "Sylvi - Interrupt Soulcoil Ritual" in before

    _apply("Nek'zali the Soulcoiler", "Interrupt Soulcoil Ritual", "Quill")

    after = assemble_boss_note(boss_id)
    assert "Quill - Interrupt Soulcoil Ritual" in after
    assert "Sylvi - Interrupt Soulcoil Ritual" not in after


def test_case_12_export_of_unassigned_responsibility(app):
    """Fixed by #76 (real MRT/NSRT syntax export, see note_service.py):
    every responsibility now produces at least one line, and one with no
    tagged raider (or an empty tag:;) shows "Unassigned" instead of being
    silently dropped or showing raw internal-token text."""
    boss = Boss(name="Empty Test Boss", raid="Test Raid", order=99)
    db.session.add(boss)
    db.session.flush()

    no_note = Responsibility(name="No note set", requires_role="DPS", note_line=None)
    has_note_no_assignee = Responsibility(
        name="Has note, nobody assigned", requires_role="DPS", note_line="tag:;"
    )
    db.session.add_all([no_note, has_note_no_assignee])
    db.session.flush()
    db.session.add(Position(x=0, y=0, boss_id=boss.id, responsibility_id=no_note.id))
    db.session.add(Position(x=1, y=0, boss_id=boss.id, responsibility_id=has_note_no_assignee.id))
    db.session.commit()

    note = assemble_boss_note(boss.id)

    assert note == "Unassigned - No note set\nUnassigned - Has note, nobody assigned"


# --- RATE LIMITING ---


def test_case_16_sixth_apply_within_10_minutes_is_429(client):
    boss = client.post(
        "/api/bosses", json={"name": "Rate Limit Boss", "raid": "Test", "order": 1}
    ).get_json()
    resp = client.post("/api/responsibilities", json={"name": "Interrupt"}).get_json()
    client.post(
        "/api/positions",
        json={"x": 1, "y": 1, "boss_id": boss["id"], "responsibility_id": resp["id"]},
    )
    client.post(
        "/api/raiders", json={"name": "Rob", "wow_class": "Warrior", "spec": "Arms", "role": "DPS"}
    )

    proposal = {"responsibility_name": "Interrupt", "to_raider_name": "Rob"}
    for _ in range(5):
        assert client.post("/api/agent/apply", json={"proposal": proposal}).status_code == 200

    resp = client.post("/api/agent/apply", json={"proposal": proposal})
    assert resp.status_code == 429
    assert resp.get_json()["retry_after_seconds"] > 0
