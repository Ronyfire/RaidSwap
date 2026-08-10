from unittest.mock import Mock, patch

import pytest

from extensions import db
from models import IconCache
from services import blizzard_service
from services.blizzard_service import (
    BlizzardServiceError,
    get_creature_icon,
    get_playable_class_icon,
    get_spell_icon,
)

_ENV = {"BLIZZARD_CLIENT_ID": "test-id", "BLIZZARD_CLIENT_SECRET": "test-secret"}
_TOKEN_RESPONSE = Mock(
    status_code=200,
    json=lambda: {"access_token": "fake-token", "token_type": "bearer", "expires_in": 86399},
)


@pytest.fixture(autouse=True)
def reset_token_cache():
    # Module-level cache — must reset between tests or a token fetched in
    # one test leaks into the next and hides a broken OAuth call.
    blizzard_service._token_cache = {"access_token": None, "expires_at": 0.0}
    yield


def _media_response(key, value):
    return Mock(status_code=200, json=lambda: {"assets": [{"key": key, "value": value}], "id": 1})


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.get")
@patch("services.blizzard_service.httpx.post")
def test_get_spell_icon_success_and_caches(mock_post, mock_get, app):
    mock_post.return_value = _TOKEN_RESPONSE
    mock_get.return_value = _media_response("icon", "https://render.worldofwarcraft.com/icon.jpg")

    icon = get_spell_icon(133)

    assert icon == "https://render.worldofwarcraft.com/icon.jpg"
    row = IconCache.query.filter_by(media_type="spell", external_id=133, region="us").first()
    assert row is not None
    assert row.resolved_value == icon


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.get")
@patch("services.blizzard_service.httpx.post")
def test_get_playable_class_icon_success(mock_post, mock_get, app):
    mock_post.return_value = _TOKEN_RESPONSE
    mock_get.return_value = _media_response("icon", "https://render.worldofwarcraft.com/warrior.jpg")

    assert get_playable_class_icon(1) == "https://render.worldofwarcraft.com/warrior.jpg"


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.get")
@patch("services.blizzard_service.httpx.post")
def test_get_creature_icon_does_two_hop_lookup_and_caches_both(mock_post, mock_get, app):
    mock_post.return_value = _TOKEN_RESPONSE
    creature_response = Mock(
        status_code=200, json=lambda: {"creature_displays": [{"id": 37541}]}
    )
    media_response = _media_response("zoom", "https://render.worldofwarcraft.com/zoom.jpg")
    mock_get.side_effect = [creature_response, media_response]

    icon = get_creature_icon(51600)

    assert icon == "https://render.worldofwarcraft.com/zoom.jpg"
    lookup = IconCache.query.filter_by(
        media_type="creature_display_lookup", external_id=51600, region="us"
    ).first()
    assert lookup is not None and lookup.resolved_value == "37541"
    display = IconCache.query.filter_by(
        media_type="creature_display", external_id=37541, region="us"
    ).first()
    assert display is not None and display.resolved_value == icon


@patch.dict("os.environ", {}, clear=True)
@patch("services.blizzard_service.httpx.post")
def test_missing_credentials_raises_without_calling_network(mock_post, app):
    with pytest.raises(BlizzardServiceError, match="not set"):
        get_spell_icon(133)
    mock_post.assert_not_called()


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.post")
def test_oauth_non_200_raises(mock_post, app):
    mock_post.return_value = Mock(status_code=401)
    with pytest.raises(BlizzardServiceError, match="OAuth returned HTTP 401"):
        get_spell_icon(133)


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.get")
@patch("services.blizzard_service.httpx.post")
def test_media_non_200_raises(mock_post, mock_get, app):
    mock_post.return_value = _TOKEN_RESPONSE
    mock_get.return_value = Mock(status_code=404)
    with pytest.raises(BlizzardServiceError, match="HTTP 404"):
        get_spell_icon(133)


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.get")
@patch("services.blizzard_service.httpx.post")
def test_missing_asset_key_raises(mock_post, mock_get, app):
    mock_post.return_value = _TOKEN_RESPONSE
    mock_get.return_value = _media_response("zoom", "irrelevant")  # spell wants "icon", not "zoom"
    with pytest.raises(BlizzardServiceError, match="No 'icon' asset"):
        get_spell_icon(133)


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.get")
@patch("services.blizzard_service.httpx.post")
def test_cached_value_skips_network_entirely(mock_post, mock_get, app):
    db.session.add(
        IconCache(
            media_type="spell", external_id=133, region="us",
            resolved_value="https://render.worldofwarcraft.com/cached.jpg",
        )
    )
    db.session.commit()

    icon = get_spell_icon(133)

    assert icon == "https://render.worldofwarcraft.com/cached.jpg"
    mock_post.assert_not_called()
    mock_get.assert_not_called()


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.get")
@patch("services.blizzard_service.httpx.post")
def test_token_is_fetched_once_and_reused_across_calls(mock_post, mock_get, app):
    mock_post.return_value = _TOKEN_RESPONSE
    mock_get.return_value = _media_response("icon", "https://render.worldofwarcraft.com/icon.jpg")

    get_spell_icon(133)
    get_spell_icon(190)  # different id -> not a cache hit, must reuse the token

    assert mock_post.call_count == 1


@patch.dict("os.environ", _ENV)
@patch("services.blizzard_service.httpx.get")
@patch("services.blizzard_service.httpx.post")
def test_class_icon_route_success(mock_post, mock_get, client):
    mock_post.return_value = _TOKEN_RESPONSE
    mock_get.return_value = _media_response("icon", "https://render.worldofwarcraft.com/warrior.jpg")

    resp = client.get("/api/blizzard/class-icon/1")

    assert resp.status_code == 200
    assert resp.get_json() == {"icon_url": "https://render.worldofwarcraft.com/warrior.jpg"}


@patch.dict("os.environ", {}, clear=True)
def test_class_icon_route_returns_503_without_credentials(client):
    resp = client.get("/api/blizzard/class-icon/1")

    assert resp.status_code == 503
    assert "not set" in resp.get_json()["error"]


@patch.dict("os.environ", _ENV)
@patch("routes.blizzard.httpx.get")
@patch("routes.blizzard.get_playable_class_icon")
def test_class_icon_image_route_proxies_bytes(mock_get_icon, mock_route_get, client):
    # Mocked at the routes.blizzard boundary, not services.blizzard_service's
    # httpx calls — both modules share the same underlying httpx.get
    # attribute, so patching "services.blizzard_service.httpx.get" and
    # "routes.blizzard.httpx.get" in the same test collide (last patch
    # applied wins for both call sites). The route's own OAuth/media
    # resolution is already covered by the service-level tests above; this
    # test is only about the route's own proxy behavior.
    mock_get_icon.return_value = "https://render.worldofwarcraft.com/warrior.jpg"
    mock_route_get.return_value = Mock(
        status_code=200, content=b"fake-jpeg-bytes", headers={"content-type": "image/jpeg"}
    )

    resp = client.get("/api/blizzard/class-icon/1/image")

    assert resp.status_code == 200
    assert resp.data == b"fake-jpeg-bytes"
    assert resp.content_type == "image/jpeg"
    mock_route_get.assert_called_once_with("https://render.worldofwarcraft.com/warrior.jpg", timeout=10)


@patch.dict("os.environ", {}, clear=True)
def test_class_icon_image_route_returns_503_without_credentials(client):
    resp = client.get("/api/blizzard/class-icon/1/image")

    assert resp.status_code == 503


@patch.dict("os.environ", _ENV)
@patch("routes.blizzard.httpx.get")
@patch("routes.blizzard.get_playable_class_icon")
def test_class_icon_image_route_returns_502_on_fetch_failure(mock_get_icon, mock_route_get, client):
    mock_get_icon.return_value = "https://render.worldofwarcraft.com/warrior.jpg"
    mock_route_get.return_value = Mock(status_code=404)

    resp = client.get("/api/blizzard/class-icon/1/image")

    assert resp.status_code == 502
