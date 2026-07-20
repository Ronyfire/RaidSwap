from flask import Blueprint, jsonify, request

from extensions import db
from models import MechanicProfile, Raider, Responsibility

mechanic_profiles_bp = Blueprint(
    "mechanic_profiles", __name__, url_prefix="/api/mechanic-profiles"
)

REQUIRED_FIELDS = ["raider_id", "responsibility_id", "proficiency_level"]


def _validate_foreign_keys(data):
    if "raider_id" in data and db.session.get(Raider, data["raider_id"]) is None:
        return f"Raider {data['raider_id']} not found"
    if (
        "responsibility_id" in data
        and db.session.get(Responsibility, data["responsibility_id"]) is None
    ):
        return f"Responsibility {data['responsibility_id']} not found"
    return None


@mechanic_profiles_bp.get("")
def list_mechanic_profiles():
    return jsonify([m.to_dict() for m in MechanicProfile.query.all()])


@mechanic_profiles_bp.get("/<int:mechanic_profile_id>")
def get_mechanic_profile(mechanic_profile_id):
    profile = db.session.get(MechanicProfile, mechanic_profile_id)
    if profile is None:
        return jsonify(error="MechanicProfile not found"), 404
    return jsonify(profile.to_dict())


@mechanic_profiles_bp.post("")
def create_mechanic_profile():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if data.get(f) is None]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    fk_error = _validate_foreign_keys(data)
    if fk_error:
        return jsonify(error=fk_error), 404

    profile = MechanicProfile(**{f: data[f] for f in REQUIRED_FIELDS})
    db.session.add(profile)
    db.session.commit()
    return jsonify(profile.to_dict()), 201


@mechanic_profiles_bp.put("/<int:mechanic_profile_id>")
def update_mechanic_profile(mechanic_profile_id):
    profile = db.session.get(MechanicProfile, mechanic_profile_id)
    if profile is None:
        return jsonify(error="MechanicProfile not found"), 404

    data = request.get_json(silent=True) or {}
    fk_error = _validate_foreign_keys(data)
    if fk_error:
        return jsonify(error=fk_error), 404

    for field in REQUIRED_FIELDS:
        if field in data:
            setattr(profile, field, data[field])
    db.session.commit()
    return jsonify(profile.to_dict())


@mechanic_profiles_bp.delete("/<int:mechanic_profile_id>")
def delete_mechanic_profile(mechanic_profile_id):
    profile = db.session.get(MechanicProfile, mechanic_profile_id)
    if profile is None:
        return jsonify(error="MechanicProfile not found"), 404

    db.session.delete(profile)
    db.session.commit()
    return "", 204
