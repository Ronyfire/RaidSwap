from extensions import db
from models import Boss, Position, Responsibility
from services.note_service import (
    assemble_boss_note,
    render_mrt_lines,
    replace_raider_name_in_note_line,
)


def test_replace_raider_name_in_note_line():
    note_line = "time:16;ph:1;bossSpell:1284931;tag:Grynga;spellid:471195;"
    result = replace_raider_name_in_note_line(note_line, "Grynga", "Thrall")
    assert result == "time:16;ph:1;bossSpell:1284931;tag:Thrall;spellid:471195;"


def test_replace_raider_name_in_note_line_not_found():
    note_line = "time:16;ph:1;bossSpell:1284931;tag:Grynga;spellid:471195;"
    result = replace_raider_name_in_note_line(note_line, "Nonexistent", "Thrall")
    assert result == note_line


def test_replace_raider_name_in_note_line_respects_word_boundaries():
    # "Ilse" must not match inside "Ilsemarie" — names are unique, but a
    # naive substring replace would still corrupt an unrelated name.
    note_line = "tag:Ilsemarie;"
    result = replace_raider_name_in_note_line(note_line, "Ilse", "Doran")
    assert result == "tag:Ilsemarie;"


def test_replace_raider_name_in_note_line_works_on_real_mrt_syntax_too():
    # Not tied to the tag: token — works on any syntax the name appears in,
    # including the real MRT/NSRT line format render_mrt_lines produces.
    line = "{time:1:30}{spell:47788}Kaeli - Guardian Spirit en el tank"
    result = replace_raider_name_in_note_line(line, "Kaeli", "Cillian")
    assert result == "{time:1:30}{spell:47788}Cillian - Guardian Spirit en el tank"


def test_render_mrt_lines_minimal_tag_only():
    assert render_mrt_lines("tag:Sylvi;", "Interrupt Soulcoil Ritual") == [
        "Sylvi - Interrupt Soulcoil Ritual"
    ]


def test_render_mrt_lines_full_time_and_spell():
    note_line = "time:90;ph:1;bossSpell:1284931;tag:Kaeli;spellid:47788;"
    assert render_mrt_lines(note_line, "Guardian Spirit en el tank") == [
        "{time:1:30}{spell:47788}Kaeli - Guardian Spirit en el tank"
    ]


def test_render_mrt_lines_time_only_no_spell():
    assert render_mrt_lines("time:65;tag:Paco;", "Tank swap") == [
        "{time:1:05}Paco - Tank swap"
    ]


def test_render_mrt_lines_spell_only_no_time():
    assert render_mrt_lines("spellid:12345;tag:Paco;", "Tank swap") == [
        "{spell:12345}Paco - Tank swap"
    ]


def test_render_mrt_lines_multiple_raiders_one_line_each():
    assert render_mrt_lines("ph:1;tag:Doran;tag:Ilse;", "Spirit adds") == [
        "Doran - Spirit adds",
        "Ilse - Spirit adds",
    ]


def test_render_mrt_lines_no_tag_is_unassigned():
    assert render_mrt_lines("ph:1;", "Interrupt Soulcoil Ritual") == [
        "Unassigned - Interrupt Soulcoil Ritual"
    ]


def test_render_mrt_lines_empty_tag_is_unassigned():
    assert render_mrt_lines("tag:;", "Interrupt Soulcoil Ritual") == [
        "Unassigned - Interrupt Soulcoil Ritual"
    ]


def test_render_mrt_lines_empty_note_line_is_unassigned():
    assert render_mrt_lines("", "Interrupt Soulcoil Ritual") == [
        "Unassigned - Interrupt Soulcoil Ritual"
    ]


def _make_position(boss, name, note_line, index, description=None):
    responsibility = Responsibility(
        name=name, requires_role="DPS", note_line=note_line, description_es=description
    )
    db.session.add(responsibility)
    db.session.flush()
    db.session.add(
        Position(x=float(index), y=0.0, boss_id=boss.id, responsibility_id=responsibility.id)
    )
    return responsibility


def test_assemble_boss_note_real_syntax_minimal_data(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    _make_position(boss, "Interrupt", "ph:1;tag:Sylvi;", 0)
    _make_position(boss, "Tank swap", "tag:Paco;", 1)
    db.session.commit()

    note = assemble_boss_note(boss.id)
    assert note == "Sylvi - Interrupt\nPaco - Tank swap"


def test_assemble_boss_note_prefers_description_as_action(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    _make_position(
        boss, "Tank swap", "tag:Paco;", 0, description="Guardian Spirit en el tank"
    )
    db.session.commit()

    assert assemble_boss_note(boss.id) == "Paco - Guardian Spirit en el tank"


def test_assemble_boss_note_full_syntax_with_time_and_spell(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    _make_position(boss, "Heal CD", "time:90;tag:Kaeli;spellid:47788;", 0)
    db.session.commit()

    assert assemble_boss_note(boss.id) == "{time:1:30}{spell:47788}Kaeli - Heal CD"


def test_assemble_boss_note_skips_positions_without_responsibility(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    db.session.add(Position(x=0.0, y=0.0, boss_id=boss.id, responsibility_id=None))
    db.session.commit()

    assert assemble_boss_note(boss.id) == ""


def test_assemble_boss_note_responsibility_without_note_line_shows_unassigned(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    _make_position(boss, "No note yet", None, 0)
    db.session.commit()

    assert assemble_boss_note(boss.id) == "Unassigned - No note yet"


def test_assemble_boss_note_empty_boss(app):
    boss = Boss(name="Empty Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.commit()

    assert assemble_boss_note(boss.id) == ""


def test_assemble_boss_note_multi_assignee_responsibility_gets_one_line_per_raider(app):
    boss = Boss(name="Test Boss", raid="Test Raid", order=1)
    db.session.add(boss)
    db.session.flush()
    _make_position(boss, "Spirit adds", "ph:1;tag:Doran;tag:Ilse;", 0)
    db.session.commit()

    assert assemble_boss_note(boss.id) == "Doran - Spirit adds\nIlse - Spirit adds"
