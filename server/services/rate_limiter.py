"""Per-user, per-action rate limiting for agent actions.

See projects/agent-architecture.md. In-memory on purpose — plenty for the
10-15 person tester phase, and a backend restart clearing everyone's cooldown
is an acceptable trade-off at this scale. Revisit (Redis, a DB table) only if
that stops being true.

Wired into POST /api/agent/apply (see routes/agent.py) — a User lookup by JWT
identity, a check_rate_limit call keyed on user.tier, and an early 429 with
retry_after_seconds when the cooldown hasn't elapsed.
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
