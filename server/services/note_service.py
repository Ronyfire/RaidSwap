def replace_tag_in_note_line(note_line: str, old_name: str, new_name: str) -> str:
    old_pattern = f"tag:{old_name};"
    new_pattern = f"tag:{new_name};"
    return note_line.replace(old_pattern, new_pattern)
