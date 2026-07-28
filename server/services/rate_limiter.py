"""Per-user, per-action rate limiting for agent actions.

See projects/agent-architecture.md. In-memory on purpose — plenty for the
10-15 person tester phase, and a backend restart clearing everyone's cooldown
is an acceptable trade-off at this scale. Revisit (Redis, a DB table) only if
that stops being true.

Not wired into any route yet: this needs both routes/agent.py (feature/agent-
core) and JWT identity + User.tier (feature/auth-jwt), neither of which is on
this branch, since both are still unmerged siblings of this one. Once both
land, wiring POST /api/agent/apply looks like:

    from flask_jwt_extended import get_jwt_identity
    from services.rate_limiter import check_rate_limit

    user = db.session.get(User, int(get_jwt_identity()))
    result = check_rate_limit(user.id, "note_change", user.tier)
    if not result["allowed"]:
        return jsonify(error="Rate limit exceeded", retry_after_seconds=result["retry_after_seconds"]), 429

That's a config lookup + an early return, not a rearchitecture.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

LIMITS = {
    "free": {
        "note_change": {"max": 5, "window_minutes": 10},
        "raidplan_change": {"max": 1, "window_minutes": 10},
    },
}

_events: dict[tuple[int, str], list[datetime]] = defaultdict(list)


def check_rate_limit(
    user_id: int, action_type: str, tier: str = "free", _now: datetime | None = None
) -> dict:
    """Check (and, if allowed, record) one action against its cooldown.

    Returns {"allowed": True} or {"allowed": False, "retry_after_seconds": int}.
    An action_type with no configured limit for the tier is never limited —
    that's a deliberate default (fail open on missing config, not closed).

    _now is a test-only hook to simulate the passage of time without a mocking
    library — real callers never pass it.
    """
    limits = LIMITS.get(tier, LIMITS["free"]).get(action_type)
    if limits is None:
        return {"allowed": True}

    now = _now or datetime.now(timezone.utc)
    window = timedelta(minutes=limits["window_minutes"])
    key = (user_id, action_type)

    recent = [t for t in _events[key] if now - t < window]

    if len(recent) >= limits["max"]:
        retry_after = window - (now - min(recent))
        _events[key] = recent
        return {"allowed": False, "retry_after_seconds": max(1, int(retry_after.total_seconds()))}

    recent.append(now)
    _events[key] = recent
    return {"allowed": True}


def reset() -> None:
    """Clear all recorded events. Test-only — real usage never needs this."""
    _events.clear()
