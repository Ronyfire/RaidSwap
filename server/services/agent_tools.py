"""Pure-Python tool implementations for the reassignment agent.

Each function here is what the LLM calls as a "tool" — but they're plain
functions operating on the DB, with no dependency on the LLM client. That's
deliberate: they're fully testable and usable on their own.

Cascade for reassignment confidence (WCL integration comes later, per
projects/agent-architecture.md): today we only have MechanicProfile data.
If a raider has no MechanicProfile row for a responsibility, or it's
"never", the proposal is returned with confidence="unknown" so the agent's
reply can ask the raid leader to confirm instead of assuming.
"""

from extensions import db
from models import Assignment, Boss, MechanicProfile, Position, Raider, Responsibility
from services.note_service import replace_tag_in_note_line


def _find_raider(name: str) -> Raider | None:
    return Raider.query.filter(db.func.lower(Raider.name) == name.lower()).first()


def _find_boss(name: str) -> Boss | None:
    return Boss.query.filter(db.func.lower(Boss.name) == name.lower()).first()


def _find_responsibility(name: str) -> Responsibility | None:
    return Responsibility.query.filter(db.func.lower(Responsibility.name) == name.lower()).first()


def _role_compatible(raider: Raider, responsibility: Responsibility) -> bool:
    return responsibility.requires_role is None or responsibility.requires_role == raider.role


def get_roster() -> dict:
    """List every raider — name, class, spec, role."""
    return {"raiders": [r.to_dict() for r in Raider.query.all()]}


def get_mechanic_profile(raider_name: str, responsibility_name: str) -> dict:
    """Look up how proficient a raider is at a specific mechanic/responsibility."""
    raider = _find_raider(raider_name)
    if raider is None:
        return {"found": False, "error": f"No raider named '{raider_name}'"}

    responsibility = _find_responsibility(responsibility_name)
    if responsibility is None:
        return {"found": False, "error": f"No responsibility named '{responsibility_name}'"}

    profile = MechanicProfile.query.filter_by(
        raider_id=raider.id, responsibility_id=responsibility.id
    ).first()

    return {
        "found": True,
        "raider_name": raider.name,
        "responsibility_name": responsibility.name,
        "proficiency_level": profile.proficiency_level if profile else None,
    }


def propose_reassignment(boss_name: str, responsibility_name: str, new_raider_name: str) -> dict:
    """Prepare a reassignment for review — does NOT write to the database.

    Returns either {"error": "..."} or a proposal dict the raid leader can
    apply via apply_reassignment(). Confidence is "confirmed" when the new
    raider has a "has_done_it"/"mastered" MechanicProfile for this
    responsibility, otherwise "unknown" — the caller should treat "unknown"
    as a prompt to ask the raid leader rather than proceed silently.
    """
    boss = _find_boss(boss_name)
    if boss is None:
        return {"error": f"No boss named '{boss_name}'"}

    responsibility = _find_responsibility(responsibility_name)
    if responsibility is None:
        return {"error": f"No responsibility named '{responsibility_name}'"}

    linked = Position.query.filter_by(boss_id=boss.id, responsibility_id=responsibility.id).first()
    if linked is None:
        return {"error": f"'{responsibility.name}' isn't assigned to {boss.name}"}

    new_raider = _find_raider(new_raider_name)
    if new_raider is None:
        return {"error": f"No raider named '{new_raider_name}'"}

    if not _role_compatible(new_raider, responsibility):
        return {
            "error": (
                f"{new_raider.name} is {new_raider.role}, but "
                f"'{responsibility.name}' requires {responsibility.requires_role}"
            )
        }

    current_assignment = Assignment.query.filter_by(responsibility_id=responsibility.id).first()
    from_raider_name = current_assignment.raider.name if current_assignment else None

    profile = MechanicProfile.query.filter_by(
        raider_id=new_raider.id, responsibility_id=responsibility.id
    ).first()
    confidence = "confirmed" if profile and profile.proficiency_level in (
        "has_done_it",
        "mastered",
    ) else "unknown"

    return {
        "boss_name": boss.name,
        "responsibility_name": responsibility.name,
        "from_raider_name": from_raider_name,
        "to_raider_name": new_raider.name,
        "confidence": confidence,
    }


def apply_reassignment(proposal: dict) -> dict:
    """Commit a proposal produced by propose_reassignment().

    Re-resolves everything by name instead of trusting IDs from the client,
    and re-reads the *current* assignment at apply time (not whatever the
    proposal said earlier) so the note_line tag swap is always correct even
    if something else changed the assignment in between.
    """
    responsibility = _find_responsibility(proposal.get("responsibility_name", ""))
    if responsibility is None:
        raise ValueError(f"No responsibility named '{proposal.get('responsibility_name')}'")

    new_raider = _find_raider(proposal.get("to_raider_name", ""))
    if new_raider is None:
        raise ValueError(f"No raider named '{proposal.get('to_raider_name')}'")

    if not _role_compatible(new_raider, responsibility):
        raise ValueError(
            f"{new_raider.name} is {new_raider.role}, but "
            f"'{responsibility.name}' requires {responsibility.requires_role}"
        )

    assignment = Assignment.query.filter_by(responsibility_id=responsibility.id).first()
    old_raider_name = assignment.raider.name if assignment else None

    if assignment:
        assignment.raider_id = new_raider.id
    else:
        assignment = Assignment(raider_id=new_raider.id, responsibility_id=responsibility.id)
        db.session.add(assignment)

    if responsibility.note_line and old_raider_name:
        responsibility.note_line = replace_tag_in_note_line(
            responsibility.note_line, old_raider_name, new_raider.name
        )

    db.session.commit()

    return {
        "assignment": assignment.to_dict(),
        "responsibility": responsibility.to_dict(),
    }
