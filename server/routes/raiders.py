from flask import Blueprint, jsonify, request

from extensions import db
from models import Raider

raiders_bp = Blueprint("raiders", __name__, url_prefix="/api/raiders")

REQUIRED_FIELDS = ["name", "wow_class", "spec", "role"]
UPDATABLE_FIELDS = REQUIRED_FIELDS + ["status"]


@raiders_bp.get("")
def list_raiders():
    return jsonify([r.to_dict() for r in Raider.query.all()])


@raiders_bp.get("/<int:raider_id>")
def get_raider(raider_id):
    raider = db.session.get(Raider, raider_id)
    if raider is None:
        return jsonify(error="Raider not found"), 404
    return jsonify(raider.to_dict())


@raiders_bp.post("")
def create_raider():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    raider = Raider(**{f: data[f] for f in UPDATABLE_FIELDS if f in data})
    db.session.add(raider)
    db.session.commit()
    return jsonify(raider.to_dict()), 201


@raiders_bp.put("/<int:raider_id>")
def update_raider(raider_id):
    raider = db.session.get(Raider, raider_id)
    if raider is None:
        return jsonify(error="Raider not found"), 404

    data = request.get_json(silent=True) or {}
    for field in UPDATABLE_FIELDS:
        if field in data:
            setattr(raider, field, data[field])
    db.session.commit()
    return jsonify(raider.to_dict())


@raiders_bp.delete("/<int:raider_id>")
def delete_raider(raider_id):
    raider = db.session.get(Raider, raider_id)
    if raider is None:
        return jsonify(error="Raider not found"), 404

    db.session.delete(raider)
    db.session.commit()
    return "", 204
