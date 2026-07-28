from flask import Blueprint, jsonify, request

from services.agent_service import run_agent_turn
from services.agent_tools import apply_reassignment

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agent")


@agent_bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages")
    if not messages:
        return jsonify(error="messages is required"), 400

    result = run_agent_turn(messages)
    return jsonify(result)


@agent_bp.post("/apply")
def apply():
    data = request.get_json(silent=True) or {}
    proposal = data.get("proposal")
    if not proposal:
        return jsonify(error="proposal is required"), 400

    try:
        result = apply_reassignment(proposal)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(result)
