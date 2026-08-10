"""Blizzard Game Data / Media API adapter (#93) — optional, behind its own
file per CLAUDE.md: whatever in #19 ends up rendering icons doesn't need
this configured to work, it just falls back to a placeholder.

Confirmed with a real smoke test (2026-08-10), not just the docs — the
official docs at develop.battle.net are a client-rendered SPA this
environment can't execute, so the endpoint shapes below were cross-checked
against FuzzyStatic/blizzard (an actively maintained open-source client)
before being verified live.

- OAuth 2.0 client credentials: POST https://oauth.battle.net/token, HTTP
  Basic auth (client_id:client_secret), grant_type=client_credentials.
  Token cached in memory for its real `expires_in`, refreshed proactively
  (see _get_access_token) rather than waiting for a 401.
- Media endpoints live under https://{region}.api.blizzard.com/data/wow/media/...,
  namespace=static-{region}, Authorization: Bearer {token}. Response shape:
  {"assets": [{"key": "<icon|zoom>", "value": "<CDN URL>"}], "id": N} — spell
  and playable-class assets are keyed "icon", but creature-display assets
  are always keyed "zoom" (verified against 3 real creatures, no "icon" key
  ever showed up there), see _ASSET_KEYS.
- The Creature Display Media API takes a creature-DISPLAY id, not the
  creature id you'd actually have curated — get_creature_icon does the
  extra /data/wow/creature/{id} hop first and caches that mapping too
  (IconCache.media_type="creature_display_lookup"), so it only costs an
  extra API call the first time a given creature id is resolved.
- Resolved icons are cached in the icon_cache table (IconCache), keyed by
  (media_type, external_id, region) — never re-hit the API for an id
  that's already resolved. Combined with the 36,000 req/hour · 100 req/sec
  limit Blizzard documents, this is enough headroom for how few unique
  spell/creature/class ids a raid roster actually has; no separate
  token-bucket limiter until real usage says otherwise.
"""

import base64
import os
import time

import httpx

from extensions import db
from models import IconCache

_OAUTH_TOKEN_URL = "https://oauth.battle.net/token"
_MEDIA_ENDPOINTS = {
    "spell": "/data/wow/media/spell/{id}",
    "creature_display": "/data/wow/media/creature-display/{id}",
    "playable_class": "/data/wow/media/playable-class/{id}",
}
# The asset "key" to pull out of the response differs by type — verified
# live against real ids, not assumed: spell/playable-class return "icon",
# but creature-display always returns "zoom" (checked Ragnaros, Deathwing,
# Spawn of Onyxia — no "icon" key ever showed up for creatures).
_ASSET_KEYS = {"spell": "icon", "playable_class": "icon", "creature_display": "zoom"}

# In-memory only — a fresh token per process restart is fine, this isn't
# shared across workers and doesn't need to survive a redeploy.
_token_cache: dict = {"access_token": None, "expires_at": 0.0}


class BlizzardServiceError(Exception):
    pass


def _get_access_token() -> str:
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    client_id = os.environ.get("BLIZZARD_CLIENT_ID")
    client_secret = os.environ.get("BLIZZARD_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise BlizzardServiceError(
            "BLIZZARD_CLIENT_ID / BLIZZARD_CLIENT_SECRET are not set in the server environment"
        )

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    try:
        response = httpx.post(
            _OAUTH_TOKEN_URL,
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
    except httpx.HTTPError as e:
        raise BlizzardServiceError(f"Couldn't reach Blizzard's OAuth endpoint: {e}") from e

    if response.status_code != 200:
        raise BlizzardServiceError(f"Blizzard OAuth returned HTTP {response.status_code}")

    data = response.json()
    # Refresh a bit before the real expiry, not exactly at it — avoids a
    # request landing right as the token dies.
    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 0) - 60
    return _token_cache["access_token"]


def _get_cached(media_type: str, external_id: int, region: str) -> str | None:
    row = IconCache.query.filter_by(
        media_type=media_type, external_id=external_id, region=region
    ).first()
    return row.resolved_value if row else None


def _set_cached(media_type: str, external_id: int, region: str, value: str) -> None:
    row = IconCache.query.filter_by(
        media_type=media_type, external_id=external_id, region=region
    ).first()
    if row is None:
        db.session.add(
            IconCache(
                media_type=media_type,
                external_id=external_id,
                region=region,
                resolved_value=value,
            )
        )
    else:
        row.resolved_value = value
    db.session.commit()


def _fetch_media_asset(media_type: str, external_id: int, region: str) -> str:
    token = _get_access_token()
    path = _MEDIA_ENDPOINTS[media_type].format(id=external_id)
    url = f"https://{region}.api.blizzard.com{path}"
    try:
        response = httpx.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params={"namespace": f"static-{region}", "locale": "en_US"},
            timeout=10,
        )
    except httpx.HTTPError as e:
        raise BlizzardServiceError(f"Couldn't reach Blizzard's Media API: {e}") from e

    if response.status_code != 200:
        raise BlizzardServiceError(
            f"Blizzard Media API returned HTTP {response.status_code} for "
            f"{media_type}/{external_id}"
        )

    assets = response.json().get("assets", [])
    asset_key = _ASSET_KEYS[media_type]
    icon = next((a["value"] for a in assets if a.get("key") == asset_key), None)
    if not icon:
        raise BlizzardServiceError(
            f"No {asset_key!r} asset in response for {media_type}/{external_id}"
        )
    return icon


def _resolve_icon(media_type: str, external_id: int, region: str) -> str:
    cached = _get_cached(media_type, external_id, region)
    if cached:
        return cached
    icon = _fetch_media_asset(media_type, external_id, region)
    _set_cached(media_type, external_id, region, icon)
    return icon


def get_spell_icon(spell_id: int, region: str = "us") -> str:
    return _resolve_icon("spell", spell_id, region)


def get_playable_class_icon(class_id: int, region: str = "us") -> str:
    return _resolve_icon("playable_class", class_id, region)


def get_creature_icon(creature_id: int, region: str = "us") -> str:
    display_id_str = _get_cached("creature_display_lookup", creature_id, region)
    if display_id_str is None:
        display_id_str = str(_fetch_creature_display_id(creature_id, region))
        _set_cached("creature_display_lookup", creature_id, region, display_id_str)
    return _resolve_icon("creature_display", int(display_id_str), region)


def _fetch_creature_display_id(creature_id: int, region: str) -> int:
    token = _get_access_token()
    url = f"https://{region}.api.blizzard.com/data/wow/creature/{creature_id}"
    try:
        response = httpx.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params={"namespace": f"static-{region}", "locale": "en_US"},
            timeout=10,
        )
    except httpx.HTTPError as e:
        raise BlizzardServiceError(f"Couldn't reach Blizzard's Creature API: {e}") from e

    if response.status_code != 200:
        raise BlizzardServiceError(
            f"Blizzard Creature API returned HTTP {response.status_code} for creature/{creature_id}"
        )

    displays = response.json().get("creature_displays", [])
    if not displays:
        raise BlizzardServiceError(f"No creature_displays for creature/{creature_id}")
    return displays[0]["id"]
