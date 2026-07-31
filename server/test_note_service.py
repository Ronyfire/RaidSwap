from extensions import db
from models import Boss, Position, Responsibility
from services.note_service import assemble_boss_note, replace_tag_in_note_line


def test_replace_tag_in_note_line():
    note_line = "time:16;ph:1;bossSpell:1284931;tag:Grynga;spellid:471195;"
    result = replace_tag_in_note_line(note_line, "Grynga", "Thrall")
    assert result == "time:16;ph:1;bossSpell:1284931;tag:Thrall;spellid:471195;"


def test_replace_tag_in_note_line_tag_not_found():
    note_line = "time:16;ph:1;bossSpell:1284931;tag:Grynga;spellid:471195;"
    result = replace_tag_in_note_line(note_line, "Nonexistent", "Thrall")
    assert result == note_line


def _make_position(boss, name, note_line, index):
    responsibility = Responsibility(name=name, requires_role="DPS", note_line=note_line)
    db.session.add(responsibility)
    db.session.flush()
    db.session.add(
        Position(x=float(index), y=0.0, boss_id=boss.id, responsibility_id=responsibility.id)
    )
    return responsibility


def test_assemble_boss_note_joins_all_responsibility_lines(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    _make_position(boss, "Interrupt", "ph:1;tag:Sylvi;", 0)
    _make_position(boss, "Tank swap", "tag:Paco;", 1)
    db.session.commit()

    note = assemble_boss_note(boss.id)
    assert note == "Interrupt: ph:1;tag:Sylvi;\nTank swap: tag:Paco;"


def test_assemble_boss_note_skips_positions_without_responsibility(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    db.session.add(Position(x=0.0, y=0.0, boss_id=boss.id, responsibility_id=None))
    db.session.commit()

    assert assemble_boss_note(boss.id) == ""


def test_assemble_boss_note_skips_responsibilities_without_note_line(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    _make_position(boss, "No note yet", None, 0)
    db.session.commit()

    assert assemble_boss_note(boss.id) == ""


def test_assemble_boss_note_empty_boss(app):
    boss = Boss(name="Empty Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.commit()

    assert assemble_boss_note(boss.id) == ""
