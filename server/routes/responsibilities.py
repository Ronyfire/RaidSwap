from flask import Blueprint, jsonify, request

from extensions import db
from models import Responsibility

responsibilities_bp = Blueprint(
    "responsibilities", __name__, url_prefix="/api/responsibilities"
)

REQUIRED_FIELDS = ["name"]
UPDATABLE_FIELDS = [
    "name",
    "actor_label",
    "difficulty_variant",
    "requires_role",
    "requires_prior_experience",
    "description",
    "confidence",
    "note_line",
    "type",
]


@responsibilities_bp.get("")
def list_responsibilities():
    return jsonify([r.to_dict() for r in Responsibility.query.all()])


@responsibilities_bp.get("/<int:responsibility_id>")
def get_responsibility(responsibility_id):
    responsibility = db.session.get(Responsibility, responsibility_id)
    if responsibility is None:
        return jsonify(error="Responsibility not found"), 404
    return jsonify(responsibility.to_dict())


@responsibilities_bp.post("")
def create_responsibility():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    # Solo pasamos al constructor los campos que realmente llegaron en el
    # body, para no pisar los defaults del modelo (ej. confidence) con None
    fields = {f: data[f] for f in UPDATABLE_FIELDS if f in data}
    responsibility = Responsibility(**fields)
    db.session.add(responsibility)
    db.session.commit()
    return jsonify(responsibility.to_dict()), 201


@responsibilities_bp.put("/<int:responsibility_id>")
def update_responsibility(responsibility_id):
    responsibility = db.session.get(Responsibility, responsibility_id)
    if responsibility is None:
        return jsonify(error="Responsibility not found"), 404

    data = request.get_json(silent=True) or {}
    for field in UPDATABLE_FIELDS:
        if field in data:
            setattr(responsibility, field, data[field])
    db.session.commit()
    return jsonify(responsibility.to_dict())


@responsibilities_bp.delete("/<int:responsibility_id>")
def delete_responsibility(responsibility_id):
    responsibility = db.session.get(Responsibility, responsibility_id)
    if responsibility is None:
        return jsonify(error="Responsibility not found"), 404

    db.session.delete(responsibility)
    db.session.commit()
    return "", 204
