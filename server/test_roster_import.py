import json
from unittest.mock import Mock, patch

import pytest

from models import Raider
from services.roster_import_service import import_entries, parse_roster_text
from services.wowaudit_service import WowAuditError, fetch_roster


# --- parse_roster_text ---


def test_parse_roster_text_comma_separated():
    result = parse_roster_text("Rob,Warrior,Fury,DPS\nKaeli,Priest,Holy,Healer")
    assert result["skipped_lines"] == 0
    assert result["entries"] == [
        {"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"},
        {"name": "Kaeli", "wow_class": "Priest", "spec": "Holy", "role": "Healer"},
    ]


def test_parse_roster_text_tab_separated():
    result = parse_roster_text("Rob\tWarrior\tFury\tDPS")
    assert result["entries"] == [
        {"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"}
    ]


def test_parse_roster_text_role_case_insensitive():
    result = parse_roster_text("Paco,Paladin,Protection,tank")
    assert result["entries"][0]["role"] == "Tank"


def test_parse_roster_text_skips_header_row():
    result = parse_roster_text("Name,Class,Spec,Role\nRob,Warrior,Fury,DPS")
    assert result["skipped_lines"] == 1
    assert len(result["entries"]) == 1
    assert result["entries"][0]["name"] == "Rob"


def test_parse_roster_text_skips_blank_lines():
    result = parse_roster_text("Rob,Warrior,Fury,DPS\n\n\nKaeli,Priest,Holy,Healer")
    assert len(result["entries"]) == 2
    assert result["skipped_lines"] == 0


def test_parse_roster_text_skips_malformed_lines():
    result = parse_roster_text("Rob,Warrior,Fury,DPS\nJustAName\nKaeli,Priest,Holy,Healer")
    assert len(result["entries"]) == 2
    assert result["skipped_lines"] == 1


# --- import_entries ---


def test_import_entries_creates_new_raiders(client):
    result = import_entries(
        [
            {"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"},
            {"name": "Kaeli", "wow_class": "Priest", "spec": "Holy", "role": "Healer"},
        ]
    )
    assert result == {"created": ["Rob", "Kaeli"], "updated": []}
    raider = Raider.query.filter_by(name="Rob").first()
    assert raider.status == "active"
    assert raider.role == "DPS"


def test_import_entries_is_idempotent_updates_instead_of_duplicating(client):
    import_entries([{"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"}])

    result = import_entries(
        [{"name": "Rob", "wow_class": "Warrior", "spec": "Arms", "role": "DPS"}]
    )

    assert result == {"created": [], "updated": ["Rob"]}
    assert Raider.query.filter_by(name="Rob").count() == 1
    assert Raider.query.filter_by(name="Rob").first().spec == "Arms"


def test_import_entries_matches_name_case_insensitively(client):
    import_entries([{"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"}])

    result = import_entries([{"name": "rob", "wow_class": "Warrior", "spec": "Arms", "role": "DPS"}])

    assert result == {"created": [], "updated": ["Rob"]}


def test_import_entries_does_not_touch_existing_bench_status(client):
    import_entries([{"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"}])
    raider = Raider.query.filter_by(name="Rob").first()
    raider.status = "bench"
    from extensions import db

    db.session.commit()

    import_entries([{"name": "Rob", "wow_class": "Warrior", "spec": "Arms", "role": "DPS"}])

    assert Raider.query.filter_by(name="Rob").first().status == "bench"


# --- wowaudit_service.fetch_roster ---


def _fake_wowaudit_html(members):
    payload = {"Team": {"members": members}}
    return f"<html><script>var prefetched_data = {json.dumps(payload)};\n</script></html>"


def _character(name, wow_class, spec, role):
    return {
        "characterReference": {
            "name": name,
            "characterClass": wow_class,
            "currentSpec": {"name": spec},
            "role": role,
        }
    }


@patch.dict("os.environ", {"WOWAUDIT_API_KEY": "test-key"})
@patch("services.wowaudit_service.httpx.get")
def test_fetch_roster_parses_members_and_maps_roles(mock_get):
    members = [
        _character("Grynga", "Paladin", "Holy", "heal"),
        _character("Paco", "Warrior", "Protection", "tank"),
        _character("Rob", "Warrior", "Fury", "melee"),
        _character("Sharpy", "Hunter", "Marksmanship", "ranged"),
    ]
    mock_get.return_value = Mock(status_code=200, text=_fake_wowaudit_html(members))

    entries = fetch_roster("eu", "sanguino", "gamewark", "gamewark")

    assert entries == [
        {"name": "Grynga", "wow_class": "Paladin", "spec": "Holy", "role": "Healer"},
        {"name": "Paco", "wow_class": "Warrior", "spec": "Protection", "role": "Tank"},
        {"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"},
        {"name": "Sharpy", "wow_class": "Hunter", "spec": "Marksmanship", "role": "DPS"},
    ]


@patch.dict("os.environ", {"WOWAUDIT_API_KEY": "test-key"})
@patch("services.wowaudit_service.httpx.get")
def test_fetch_roster_skips_members_missing_required_fields(mock_get):
    members = [
        _character("Grynga", "Paladin", "Holy", "heal"),
        {"characterReference": {"name": "Incomplete", "characterClass": None, "currentSpec": {}, "role": "tank"}},
    ]
    mock_get.return_value = Mock(status_code=200, text=_fake_wowaudit_html(members))

    entries = fetch_roster("eu", "sanguino", "gamewark", "gamewark")

    assert len(entries) == 1
    assert entries[0]["name"] == "Grynga"


@patch.dict("os.environ", {}, clear=True)
def test_fetch_roster_raises_without_api_key():
    with pytest.raises(WowAuditError, match="WOWAUDIT_API_KEY"):
        fetch_roster("eu", "sanguino", "gamewark", "gamewark")


@patch.dict("os.environ", {"WOWAUDIT_API_KEY": "test-key"})
@patch("services.wowaudit_service.httpx.get")
def test_fetch_roster_raises_on_non_200(mock_get):
    mock_get.return_value = Mock(status_code=404, text="not found")

    with pytest.raises(WowAuditError, match="404"):
        fetch_roster("eu", "sanguino", "gamewark", "gamewark")


@patch.dict("os.environ", {"WOWAUDIT_API_KEY": "test-key"})
@patch("services.wowaudit_service.httpx.get")
def test_fetch_roster_raises_when_prefetched_data_missing(mock_get):
    mock_get.return_value = Mock(status_code=200, text="<html>no data here</html>")

    with pytest.raises(WowAuditError, match="Couldn't find roster data"):
        fetch_roster("eu", "sanguino", "gamewark", "gamewark")


# --- routes ---


def test_paste_preview_route(client):
    resp = client.post(
        "/api/roster-import/paste/preview", json={"text": "Rob,Warrior,Fury,DPS"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["entries"] == [
        {"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"}
    ]


def test_paste_preview_route_requires_text(client):
    resp = client.post("/api/roster-import/paste/preview", json={})
    assert resp.status_code == 400


def test_confirm_route(client):
    resp = client.post(
        "/api/roster-import/confirm",
        json={"entries": [{"name": "Rob", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"}]},
    )
    assert resp.status_code == 200
    assert resp.get_json() == {"created": ["Rob"], "updated": []}
    assert Raider.query.filter_by(name="Rob").count() == 1


@patch.dict("os.environ", {"WOWAUDIT_API_KEY": "test-key"})
@patch("services.wowaudit_service.httpx.get")
def test_wowaudit_preview_route(mock_get, client):
    members = [_character("Grynga", "Paladin", "Holy", "heal")]
    mock_get.return_value = Mock(status_code=200, text=_fake_wowaudit_html(members))

    resp = client.post(
        "/api/roster-import/wowaudit/preview",
        json={"region": "eu", "realm": "sanguino", "guild": "gamewark", "team": "gamewark"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["entries"] == [
        {"name": "Grynga", "wow_class": "Paladin", "spec": "Holy", "role": "Healer"}
    ]


def test_wowaudit_preview_route_requires_all_fields(client):
    resp = client.post("/api/roster-import/wowaudit/preview", json={"region": "eu"})
    assert resp.status_code == 400
