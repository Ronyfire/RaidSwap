"""Roster import — shared core for both import sources (#20).

Both the WoWAudit adapter (wowaudit_service.py) and the paste-a-roster
fallback below produce the same shape: a list of
{"name", "wow_class", "spec", "role"}. This module owns the one place
that turns those into Raider rows, so the two sources share identical
upsert behavior instead of each reimplementing it slightly differently.
"""

from extensions import db
from models import Raider

_VALID_ROLES = {"tank": "Tank", "healer": "Healer", "dps": "DPS"}


def parse_roster_text(text: str) -> dict:
    """One raider per line, comma- or tab-separated name/class/spec/role.

    Skips blank lines and any line that doesn't parse to a known role —
    that includes a pasted header row for free ("Role" isn't tank/healer/dps),
    so callers don't need to special-case it.
    """
    entries = []
    skipped = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t") if "\t" in line else line.split(",")
        parts = [p.strip() for p in parts]
        role = _VALID_ROLES.get(parts[3].lower()) if len(parts) == 4 else None
        if len(parts) != 4 or role is None or not all(parts[:3]):
            skipped += 1
            continue
        name, wow_class, spec, _ = parts
        entries.append({"name": name, "wow_class": wow_class, "spec": spec, "role": role})
    return {"entries": entries, "skipped_lines": skipped}


def import_entries(entries: list[dict]) -> dict:
    """Idempotent upsert by name (case-insensitive) — re-importing updates
    class/spec/role on an existing raider instead of duplicating them.
    New raiders default to status="active"; an existing raider's active/bench
    status is left alone (import doesn't second-guess who's on the bench).
    """
    created = []
    updated = []
    for entry in entries:
        raider = Raider.query.filter(db.func.lower(Raider.name) == entry["name"].lower()).first()
        if raider:
            raider.wow_class = entry["wow_class"]
            raider.spec = entry["spec"]
            raider.role = entry["role"]
            updated.append(raider.name)
        else:
            raider = Raider(
                name=entry["name"],
                wow_class=entry["wow_class"],
                spec=entry["spec"],
                role=entry["role"],
                status="active",
            )
            db.session.add(raider)
            created.append(entry["name"])
    db.session.commit()
    return {"created": created, "updated": updated}
