from datetime import datetime, timedelta, timezone

from services.rate_limiter import check_rate_limit


def test_allows_up_to_the_limit():
    for _ in range(5):
        result = check_rate_limit(1, "note_change", "free")
        assert result["allowed"] is True


def test_rejects_past_the_limit():
    for _ in range(5):
        check_rate_limit(1, "note_change", "free")

    result = check_rate_limit(1, "note_change", "free")
    assert result["allowed"] is False
    assert result["retry_after_seconds"] > 0


def test_raidplan_change_limit_is_one():
    assert check_rate_limit(1, "raidplan_change", "free")["allowed"] is True
    assert check_rate_limit(1, "raidplan_change", "free")["allowed"] is False


def test_action_types_have_independent_counters():
    for _ in range(5):
        check_rate_limit(1, "note_change", "free")

    assert check_rate_limit(1, "note_change", "free")["allowed"] is False
    assert check_rate_limit(1, "raidplan_change", "free")["allowed"] is True


def test_users_have_independent_counters():
    for _ in range(5):
        check_rate_limit(1, "note_change", "free")

    assert check_rate_limit(1, "note_change", "free")["allowed"] is False
    assert check_rate_limit(2, "note_change", "free")["allowed"] is True


def test_unknown_tier_falls_back_to_free_limits():
    for _ in range(5):
        check_rate_limit(1, "note_change", "nonexistent-tier")

    assert check_rate_limit(1, "note_change", "nonexistent-tier")["allowed"] is False


def test_unconfigured_action_type_is_never_limited():
    for _ in range(50):
        result = check_rate_limit(1, "some_future_action", "free")
        assert result["allowed"] is True


def test_limit_resets_after_the_window_passes():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for _ in range(5):
        check_rate_limit(1, "note_change", "free", _now=start)

    assert check_rate_limit(1, "note_change", "free", _now=start)["allowed"] is False

    later = start + timedelta(minutes=11)
    assert check_rate_limit(1, "note_change", "free", _now=later)["allowed"] is True
