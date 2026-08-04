"""WoWAudit adapter (#20) — optional, behind its own file per CLAUDE.md:
roster_import_service.py (the core) never imports this or depends on it
being configured.

No documented public REST endpoint was found for reading a team's roster
(see projects/integrations-research.md) — WoWAudit's real public API docs
are a client-rendered SPA this environment can't execute. What's verified
working instead (tested 2026-08-04 against a real team with a real
per-team API key): a single GET to the team's roster page with an
`Authorization: <api_key>` header returns the page HTML, and that HTML
embeds the full roster as a `var prefetched_data = {...};` JSON blob meant
for the frontend to hydrate from. No OAuth dance, no session cookie.

That means this is coupled to WoWAudit's internal page markup rather than
a stable, versioned API contract — if it silently starts returning zero
entries, that's the likely cause: check whether `prefetched_data` still
exists in the response and whether `Team.members[].characterReference`
still has the same shape.
"""

import json
import os
import re

import httpx

_PREFETCHED_DATA_PATTERN = re.compile(r"var prefetched_data = (\{.*?\});\s*\n", re.DOTALL)

# WoWAudit's own role values split DPS into melee/ranged — RaidSwap's
# Raider.role doesn't make that distinction (see #18's Position.requires_range
# for where melee/ranged actually lives here), so both collapse to "DPS".
_ROLE_MAP = {"tank": "Tank", "heal": "Healer", "melee": "DPS", "ranged": "DPS"}


class WowAuditError(Exception):
    pass


def fetch_roster(region: str, realm: str, guild: str, team: str) -> list[dict]:
    api_key = os.environ.get("WOWAUDIT_API_KEY")
    if not api_key:
        raise WowAuditError("WOWAUDIT_API_KEY is not set in the server environment")

    url = f"https://wowaudit.com/guild/{region}/{realm}/{guild}/teams/{team}/roster"
    try:
        response = httpx.get(url, headers={"Authorization": api_key}, timeout=10)
    except httpx.HTTPError as e:
        raise WowAuditError(f"Couldn't reach WoWAudit: {e}") from e

    if response.status_code != 200:
        raise WowAuditError(f"WoWAudit returned HTTP {response.status_code}")

    match = _PREFETCHED_DATA_PATTERN.search(response.text)
    if not match:
        raise WowAuditError(
            "Couldn't find roster data in WoWAudit's response — check the "
            "region/realm/guild/team, or WoWAudit may have changed its page"
        )

    try:
        data = json.loads(match.group(1))
        members = data["Team"]["members"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise WowAuditError(f"Unexpected WoWAudit response shape: {e}") from e

    entries = []
    for member in members:
        character = member.get("characterReference") or {}
        role = _ROLE_MAP.get(character.get("role"))
        spec = (character.get("currentSpec") or {}).get("name")
        name = character.get("name")
        wow_class = character.get("characterClass")
        if not (role and spec and name and wow_class):
            continue
        entries.append({"name": name, "wow_class": wow_class, "spec": spec, "role": role})
    return entries
