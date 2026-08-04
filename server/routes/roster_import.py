from flask import Blueprint, jsonify, request

from services.roster_import_service import import_entries, parse_roster_text
from services.wowaudit_service import WowAuditError, fetch_roster

roster_import_bp = Blueprint("roster_import", __name__, url_prefix="/api/roster-import")


@roster_import_bp.post("/wowaudit/preview")
def wowaudit_preview():
    data = request.get_json(silent=True) or {}
    missing = [f for f in ("region", "realm", "guild", "team") if not data.get(f)]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    try:
        entries = fetch_roster(data["region"], data["realm"], data["guild"], data["team"])
    except WowAuditError as e:
        return jsonify(error=str(e)), 400

    return jsonify(entries=entries)


@roster_import_bp.post("/paste/preview")
def paste_preview():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        return jsonify(error="text is required"), 400

    return jsonify(**parse_roster_text(text))


@roster_import_bp.post("/confirm")
def confirm():
    data = request.get_json(silent=True) or {}
    entries = data.get("entries")
    if not entries:
        return jsonify(error="entries is required"), 400

    return jsonify(import_entries(entries))
