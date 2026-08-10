import httpx
from flask import Blueprint, Response, jsonify, request

from services.blizzard_service import BlizzardServiceError, get_playable_class_icon

blizzard_bp = Blueprint("blizzard", __name__, url_prefix="/api/blizzard")


@blizzard_bp.get("/class-icon/<int:class_id>")
def class_icon(class_id):
    region = request.args.get("region", "us")
    try:
        icon_url = get_playable_class_icon(class_id, region)
    except BlizzardServiceError as e:
        # Optional integration — a raid leader without Blizzard credentials
        # configured still gets a working raid plan, just without real
        # icons, so this is a clean 503 for the frontend to fall back on,
        # not a 500.
        return jsonify(error=str(e)), 503

    return jsonify(icon_url=icon_url)


@blizzard_bp.get("/class-icon/<int:class_id>/image")
def class_icon_image(class_id):
    """Proxies the actual icon bytes through our own origin.

    render.worldofwarcraft.com (Blizzard's icon CDN) sends no
    Access-Control-Allow-Origin header, so a plain <img crossOrigin> can't
    be read back out of a <canvas> for the raid plan export (#19 piece 3) —
    the browser blocks it as a CORS violation. The live overlay doesn't hit
    this (a plain <img src> with no crossOrigin attribute displays a
    cross-origin image fine, CORS only matters when JS reads the pixels
    back). Only the export path needs this proxy."""
    region = request.args.get("region", "us")
    try:
        icon_url = get_playable_class_icon(class_id, region)
    except BlizzardServiceError as e:
        return jsonify(error=str(e)), 503

    try:
        image_resp = httpx.get(icon_url, timeout=10)
    except httpx.HTTPError as e:
        return jsonify(error=f"Couldn't fetch icon image: {e}"), 502
    if image_resp.status_code != 200:
        return jsonify(error=f"Icon image fetch returned HTTP {image_resp.status_code}"), 502

    return Response(image_resp.content, mimetype=image_resp.headers.get("content-type", "image/jpeg"))
