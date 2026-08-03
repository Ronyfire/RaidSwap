import pytest

from extensions import db
from models import Assignment, Position, Raider, Responsibility
from seeds.curation import BOSS_RESPONSIBILITIES, RAIDERS, seed_curation
from seeds.venomous_abyss import seed_venomous_abyss


def test_seed_requires_bosses_first(app):
    with pytest.raises(ValueError):
        seed_curation()


def test_seed_creates_all_raiders(app):
    seed_venomous_abyss()
    seed_curation()
    assert Raider.query.count() == len(RAIDERS)


def test_seed_sets_raider_status(app):
    seed_venomous_abyss()
    seed_curation()

    active_count = Raider.query.filter_by(status="active").count()
    bench_count = Raider.query.filter_by(status="bench").count()
    assert active_count == 20
    assert bench_count == 4

    quill = Raider.query.filter_by(name="Quill").first()
    assert quill.status == "bench"
    assert quill.role == "DPS"


def test_seed_creates_responsibilities_and_positions(app):
    seed_venomous_abyss()
    seed_curation()

    total_responsibilities = sum(len(v) for v in BOSS_RESPONSIBILITIES.values())
    assert Responsibility.query.count() == total_responsibilities
    assert Position.query.count() == total_responsibilities

    interrupt = Responsibility.query.filter_by(name="Interrupt Soulcoil Ritual").first()
    assert interrupt.requires_role == "DPS"
    assert interrupt.note_line == "ph:1;tag:Sylvi;"
    assert interrupt.confidence == "unconfirmed"


def test_seed_creates_assignments_from_note_line_tags(app):
    seed_venomous_abyss()
    seed_curation()

    spirit_adds = Responsibility.query.filter_by(name="Spirit adds").first()
    assigned_names = {a.raider.name for a in spirit_adds.assignments}
    assert assigned_names == {"Doran", "Ilse"}


def test_seed_is_idempotent(app):
    seed_venomous_abyss()
    seed_curation()
    seed_curation()

    total_responsibilities = sum(len(v) for v in BOSS_RESPONSIBILITIES.values())
    assert Responsibility.query.count() == total_responsibilities
    assert Position.query.count() == total_responsibilities

    spirit_adds = Responsibility.query.filter_by(name="Spirit adds").first()
    assert len(spirit_adds.assignments) == 2


def test_seed_replaces_stale_assignments_on_rerun(app):
    seed_venomous_abyss()
    seed_curation()

    interrupt = Responsibility.query.filter_by(name="Interrupt Soulcoil Ritual").first()
    interrupt.note_line = "ph:1;tag:Doran;"
    db.session.commit()

    seed_curation()

    interrupt = Responsibility.query.filter_by(name="Interrupt Soulcoil Ritual").first()
    assigned_names = {a.raider.name for a in interrupt.assignments}
    assert assigned_names == {"Sylvi"}
    assert interrupt.note_line == "ph:1;tag:Sylvi;"


def test_seed_does_not_duplicate_bosses_position_link(app):
    seed_venomous_abyss()
    seed_curation()

    tank_swap = Responsibility.query.filter_by(name="Nek'zali tank swap").first()
    assert len(tank_swap.positions) == 1
    assert tank_swap.positions[0].boss.name == "Nek'zali the Soulcoiler"
