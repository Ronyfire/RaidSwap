from services.note_service import replace_tag_in_note_line


def test_replace_tag_in_note_line():
    note_line = "time:16;ph:1;bossSpell:1284931;tag:Grynga;spellid:471195;"
    result = replace_tag_in_note_line(note_line, "Grynga", "Thrall")
    assert result == "time:16;ph:1;bossSpell:1284931;tag:Thrall;spellid:471195;"


def test_replace_tag_in_note_line_tag_not_found():
    note_line = "time:16;ph:1;bossSpell:1284931;tag:Grynga;spellid:471195;"
    result = replace_tag_in_note_line(note_line, "Nonexistent", "Thrall")
    assert result == note_line
