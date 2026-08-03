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
from services.note_service import replace_raider_name_in_note_line


def _find_raider(name: str) -> Raider | None:
    return Raider.query.filter(db.func.lower(Raider.name) == name.lower()).first()


def _find_boss(name: str) -> Boss | None:
    return Boss.query.filter(db.func.lower(Boss.name) == name.lower()).first()


def _find_responsibility(name: str) -> Responsibility | None:
    return Responsibility.query.filter(db.func.lower(Responsibility.name) == name.lower()).first()


def get_boss_context(boss_id: int) -> dict | None:
    """Boss name + its responsibility names, for injecting into the agent's
    conversation as context — NOT an LLM-callable tool. Lets the model resolve
    informal references ("the interrupt") to an exact responsibility name, and
    skip asking which boss, when the raid leader is already on that boss's page.
    """
    boss = db.session.get(Boss, boss_id)
    if boss is None:
        return None

    responsibility_names = []
    seen_ids = set()
    for position in Position.query.filter_by(boss_id=boss_id).all():
        responsibility = position.responsibility
        if responsibility is not None and responsibility.id not in seen_ids:
            seen_ids.add(responsibility.id)
            responsibility_names.append(responsibility.name)

    return {"boss_name": boss.name, "responsibility_names": responsibility_names}


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


def propose_reassignment(
    boss_name: str,
    responsibility_name: str,
    new_raider_name: str,
    from_raider_name: str | None = None,
) -> dict:
    """Prepare a reassignment for review — does NOT write to the database.

    Returns either {"error": "..."} or a proposal dict the raid leader can
    apply via apply_reassignment(). Confidence is "confirmed" when the new
    raider has a "has_done_it"/"mastered" MechanicProfile for this
    responsibility, otherwise "unknown" — the caller should treat "unknown"
    as a prompt to ask the raid leader rather than proceed silently.

    A responsibility can have more than one raider currently assigned (e.g.
    "Spirit adds": Doran+Ilse). With one or zero current assignees,
    from_raider_name isn't needed — it's inferred. With more than one,
    from_raider_name is required; omitting it returns an ambiguity error
    listing current_assignees instead of guessing which one to bump — same
    "ask, don't assume" pattern as the confidence cascade.
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

    current_assignments = Assignment.query.filter_by(responsibility_id=responsibility.id).all()

    if from_raider_name:
        from_assignment = next(
            (a for a in current_assignments if a.raider.name.lower() == from_raider_name.lower()),
            None,
        )
        if from_assignment is None:
            return {
                "error": f"{from_raider_name} isn't currently assigned to '{responsibility.name}'"
            }
        resolved_from_name = from_assignment.raider.name
    elif len(current_assignments) > 1:
        return {
            "error": (
                f"'{responsibility.name}' has more than one raider assigned — "
                "specify which one to replace."
            ),
            "current_assignees": [a.raider.name for a in current_assignments],
        }
    else:
        resolved_from_name = current_assignments[0].raider.name if current_assignments else None

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
        "from_raider_name": resolved_from_name,
        "to_raider_name": new_raider.name,
        "confidence": confidence,
    }


def apply_reassignment(proposal: dict) -> dict:
    """Commit a proposal produced by propose_reassignment().

    Re-resolves everything by name instead of trusting IDs from the client,
    and re-reads the *current* assignments at apply time (not whatever the
    proposal said earlier) so the note_line tag swap is always correct even
    if something else changed the assignment in between.

    Re-validates the from_raider_name disambiguation independently of
    propose_reassignment — a proposal built by hand (or from a stale
    conversation) doesn't get to skip it: with more than one current
    assignee and no from_raider_name, this raises rather than guessing.
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

    current_assignments = Assignment.query.filter_by(responsibility_id=responsibility.id).all()
    from_raider_name = proposal.get("from_raider_name")

    if from_raider_name:
        assignment = next(
            (a for a in current_assignments if a.raider.name.lower() == from_raider_name.lower()),
            None,
        )
        if assignment is None:
            raise ValueError(
                f"{from_raider_name} isn't currently assigned to '{responsibility.name}'"
            )
    elif len(current_assignments) > 1:
        names = ", ".join(a.raider.name for a in current_assignments)
        raise ValueError(
            f"'{responsibility.name}' has more than one raider assigned ({names}) — "
            "specify from_raider_name"
        )
    else:
        assignment = current_assignments[0] if current_assignments else None

    old_raider = assignment.raider if assignment else None

    if assignment:
        assignment.raider_id = new_raider.id
    else:
        assignment = Assignment(raider_id=new_raider.id, responsibility_id=responsibility.id)
        db.session.add(assignment)

    # Mythic invariant: exactly 20 active. A swap is 1-for-1 — the raider
    # coming IN flips to active, the raider going OUT flips to bench, so the
    # active count never drifts.
    # Known gap, not handled here: if the outgoing raider holds assignments
    # on OTHER bosses, those are left pointing at a now-benched raider
    # (orphaned, not reassigned/flagged). Doesn't show in a single-boss demo;
    # handling it is a separate follow-up, not something this swap decides.
    if new_raider.status == "bench":
        new_raider.status = "active"
    if old_raider is not None and old_raider.id != new_raider.id:
        old_raider.status = "bench"

    if responsibility.note_line and old_raider is not None:
        responsibility.note_line = replace_raider_name_in_note_line(
            responsibility.note_line, old_raider.name, new_raider.name
        )

    db.session.commit()

    return {
        "assignment": assignment.to_dict(),
        "responsibility": responsibility.to_dict(),
    }
