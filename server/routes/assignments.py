from flask import Blueprint, jsonify, request

from extensions import db
from models import Assignment, Position, Raider, Responsibility

assignments_bp = Blueprint("assignments", __name__, url_prefix="/api/assignments")

REQUIRED_FIELDS = ["raider_id"]
UPDATABLE_FIELDS = ["raider_id", "responsibility_id", "position_id", "active_note_ref"]


def _validate_foreign_keys(data):
    if "raider_id" in data and db.session.get(Raider, data["raider_id"]) is None:
        return f"Raider {data['raider_id']} not found"
    if (
        data.get("responsibility_id") is not None
        and db.session.get(Responsibility, data["responsibility_id"]) is None
    ):
        return f"Responsibility {data['responsibility_id']} not found"
    if (
        data.get("position_id") is not None
        and db.session.get(Position, data["position_id"]) is None
    ):
        return f"Position {data['position_id']} not found"
    return None


@assignments_bp.get("")
def list_assignments():
    return jsonify([a.to_dict() for a in Assignment.query.all()])


@assignments_bp.get("/<int:assignment_id>")
def get_assignment(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if assignment is None:
        return jsonify(error="Assignment not found"), 404
    return jsonify(assignment.to_dict())


@assignments_bp.post("")
def create_assignment():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if data.get(f) is None]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    fk_error = _validate_foreign_keys(data)
    if fk_error:
        return jsonify(error=fk_error), 404

    fields = {f: data[f] for f in UPDATABLE_FIELDS if f in data}
    assignment = Assignment(**fields)
    db.session.add(assignment)
    try:
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify(error=str(e)), 400
    return jsonify(assignment.to_dict()), 201


@assignments_bp.put("/<int:assignment_id>")
def update_assignment(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if assignment is None:
        return jsonify(error="Assignment not found"), 404

    data = request.get_json(silent=True) or {}
    fk_error = _validate_foreign_keys(data)
    if fk_error:
        return jsonify(error=fk_error), 404

    for field in UPDATABLE_FIELDS:
        if field in data:
            setattr(assignment, field, data[field])

    try:
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify(error=str(e)), 400
    return jsonify(assignment.to_dict())


@assignments_bp.delete("/<int:assignment_id>")
def delete_assignment(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if assignment is None:
        return jsonify(error="Assignment not found"), 404

    db.session.delete(assignment)
    db.session.commit()
    return "", 204
