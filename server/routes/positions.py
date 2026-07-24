from flask import Blueprint, jsonify, request

from extensions import db
from models import Boss, Position, Responsibility

positions_bp = Blueprint("positions", __name__, url_prefix="/api/positions")

REQUIRED_FIELDS = ["x", "y", "boss_id"]
UPDATABLE_FIELDS = ["x", "y", "boss_id", "requires_role", "responsibility_id"]


def _validate_foreign_keys(data):
    if "boss_id" in data and db.session.get(Boss, data["boss_id"]) is None:
        return f"Boss {data['boss_id']} not found"
    if (
        data.get("responsibility_id") is not None
        and db.session.get(Responsibility, data["responsibility_id"]) is None
    ):
        return f"Responsibility {data['responsibility_id']} not found"
    return None


@positions_bp.get("")
def list_positions():
    query = Position.query
    boss_id = request.args.get("boss_id", type=int)
    if boss_id is not None:
        query = query.filter_by(boss_id=boss_id)
    return jsonify([p.to_dict() for p in query.all()])


@positions_bp.get("/<int:position_id>")
def get_position(position_id):
    position = db.session.get(Position, position_id)
    if position is None:
        return jsonify(error="Position not found"), 404
    return jsonify(position.to_dict())


@positions_bp.post("")
def create_position():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if data.get(f) is None]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    fk_error = _validate_foreign_keys(data)
    if fk_error:
        return jsonify(error=fk_error), 404

    fields = {f: data[f] for f in UPDATABLE_FIELDS if f in data}
    position = Position(**fields)
    db.session.add(position)
    db.session.commit()
    return jsonify(position.to_dict()), 201


@positions_bp.put("/<int:position_id>")
def update_position(position_id):
    position = db.session.get(Position, position_id)
    if position is None:
        return jsonify(error="Position not found"), 404

    data = request.get_json(silent=True) or {}
    fk_error = _validate_foreign_keys(data)
    if fk_error:
        return jsonify(error=fk_error), 404

    for field in UPDATABLE_FIELDS:
        if field in data:
            setattr(position, field, data[field])
    db.session.commit()
    return jsonify(position.to_dict())


@positions_bp.delete("/<int:position_id>")
def delete_position(position_id):
    position = db.session.get(Position, position_id)
    if position is None:
        return jsonify(error="Position not found"), 404

    db.session.delete(position)
    db.session.commit()
    return "", 204
