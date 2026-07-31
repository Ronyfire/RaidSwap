def replace_tag_in_note_line(note_line: str, old_name: str, new_name: str) -> str:
    old_pattern = f"tag:{old_name};"
    new_pattern = f"tag:{new_name};"
    return note_line.replace(old_pattern, new_pattern)


def assemble_boss_note(boss_id: int) -> str:
    """One copyable MRT/NSRT-style block: every responsibility's note_line for
    this boss, one per line, prefixed with its name so the raid leader can
    tell lines apart when pasting into MRT/NSRT."""
    from models import Position

    positions = Position.query.filter_by(boss_id=boss_id).all()
    responsibilities = []
    seen_ids = set()
    for position in positions:
        responsibility = position.responsibility
        if responsibility is None or responsibility.id in seen_ids:
            continue
        seen_ids.add(responsibility.id)
        responsibilities.append(responsibility)

    lines = [
        f"{r.name}: {r.note_line}" for r in responsibilities if r.note_line
    ]
    return "\n".join(lines)
