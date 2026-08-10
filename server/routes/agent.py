from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from extensions import db
from models import User
from services.agent_service import run_agent_turn
from services.agent_tools import apply_reassignment
from services.rate_limiter import check_rate_limit

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agent")


@agent_bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages")
    if not messages:
        return jsonify(error="messages is required"), 400

    result = run_agent_turn(messages, boss_id=data.get("boss_id"))
    return jsonify(result)


@agent_bp.post("/apply")
def apply():
    data = request.get_json(silent=True) or {}
    proposal = data.get("proposal")
    if not proposal:
        return jsonify(error="proposal is required"), 400

    user = db.session.get(User, int(get_jwt_identity()))
    limit_result = check_rate_limit(user.id, "note_change", user.tier)
    if not limit_result["allowed"]:
        return jsonify(
            error="Rate limit exceeded",
            retry_after_seconds=limit_result["retry_after_seconds"],
        ), 429

    try:
        result = apply_reassignment(proposal, acknowledged_risk=bool(data.get("acknowledged_risk")))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(result)
