from flask import Blueprint, jsonify, request

from extensions import db
from models import Boss

bosses_bp = Blueprint("bosses", __name__, url_prefix="/api/bosses")

REQUIRED_FIELDS = ["name", "raid", "order"]


@bosses_bp.get("")
def list_bosses():
    return jsonify([b.to_dict() for b in Boss.query.all()])


@bosses_bp.get("/<int:boss_id>")
def get_boss(boss_id):
    boss = db.session.get(Boss, boss_id)
    if boss is None:
        return jsonify(error="Boss not found"), 404
    return jsonify(boss.to_dict())


@bosses_bp.post("")
def create_boss():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    boss = Boss(**{f: data[f] for f in REQUIRED_FIELDS})
    db.session.add(boss)
    db.session.commit()
    return jsonify(boss.to_dict()), 201


@bosses_bp.put("/<int:boss_id>")
def update_boss(boss_id):
    boss = db.session.get(Boss, boss_id)
    if boss is None:
        return jsonify(error="Boss not found"), 404

    data = request.get_json(silent=True) or {}
    for field in REQUIRED_FIELDS:
        if field in data:
            setattr(boss, field, data[field])
    db.session.commit()
    return jsonify(boss.to_dict())


@bosses_bp.delete("/<int:boss_id>")
def delete_boss(boss_id):
    boss = db.session.get(Boss, boss_id)
    if boss is None:
        return jsonify(error="Boss not found"), 404

    db.session.delete(boss)
    db.session.commit()
    return "", 204
