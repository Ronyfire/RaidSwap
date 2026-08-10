import re

_TIME_PATTERN = re.compile(r"time:(\d+);")
_SPELLID_PATTERN = re.compile(r"spellid:(\d+);")
_TAG_PATTERN = re.compile(r"tag:([^;]*);")


def _seconds_to_mmss(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}:{secs:02d}"


def replace_raider_name_in_note_line(note_line: str, old_name: str, new_name: str) -> str:
    """Swap a raider's name wherever it appears in note_line. A plain,
    word-boundary-safe name replace instead of a tag:Name;-specific pattern —
    roster names are unique, so this works regardless of the surrounding
    syntax (internal tokens today, real MRT/NSRT syntax once note_line
    itself moves to that format)."""
    return re.sub(rf"\b{re.escape(old_name)}\b", new_name, note_line)


def render_mrt_lines(note_line: str, action: str) -> list[str]:
    """Real MRT/NSRT syntax: {time:MM:SS}{spell:ID}Name - action, one line
    per raider tagged in note_line. Missing time/spell are omitted cleanly
    (no empty {time:}/{spell:} braces) rather than guessed — see
    projects/notes-model.md. No tagged raider (or an empty tag:;) renders
    as a single "Unassigned" line instead of being silently dropped.
    """
    prefix = ""
    time_match = _TIME_PATTERN.search(note_line)
    if time_match:
        prefix += f"{{time:{_seconds_to_mmss(int(time_match.group(1)))}}}"
    spell_match = _SPELLID_PATTERN.search(note_line)
    if spell_match:
        prefix += f"{{spell:{spell_match.group(1)}}}"

    names = [n for n in _TAG_PATTERN.findall(note_line) if n]
    if not names:
        return [f"{prefix}Unassigned - {action}"]
    return [f"{prefix}{name} - {action}" for name in names]


def assemble_boss_note(boss_id: int) -> str:
    """One copyable block in real MRT/NSRT syntax: every responsibility for
    this boss, one line per assigned raider (or an "Unassigned" line if
    none), ready to paste into the addon with /mrtni."""
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

    lines = []
    for r in responsibilities:
        # Nota pensada para pegar en el addon con /mrtni — sin locale de request,
        # se prioriza español por ser el idioma de curación real de este raid.
        action = r.description_es or r.description_en or r.name
        lines.extend(render_mrt_lines(r.note_line or "", action))
    return "\n".join(lines)
