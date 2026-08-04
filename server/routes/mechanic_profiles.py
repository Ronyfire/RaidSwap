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


def _validate_pair(raider_id, responsibility_id, exclude_id=None):
    """Rejects role-incompatible pairs and duplicate (raider, responsibility)
    rows — same pair twice is ambiguous (which proficiency_level wins?), and
    "healer assigned to an interrupt" is nonsensical data (#46)."""
    raider = db.session.get(Raider, raider_id)
    responsibility = db.session.get(Responsibility, responsibility_id)
    if responsibility.requires_role is not None and responsibility.requires_role != raider.role:
        return (
            f"{raider.name} is {raider.role}, but '{responsibility.name}' "
            f"requires {responsibility.requires_role}"
        )

    duplicate_query = MechanicProfile.query.filter_by(
        raider_id=raider_id, responsibility_id=responsibility_id
    )
    if exclude_id is not None:
        duplicate_query = duplicate_query.filter(MechanicProfile.id != exclude_id)
    if duplicate_query.first() is not None:
        return f"A MechanicProfile for {raider.name} / '{responsibility.name}' already exists"

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

    pair_error = _validate_pair(data["raider_id"], data["responsibility_id"])
    if pair_error:
        return jsonify(error=pair_error), 400

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

    new_raider_id = data.get("raider_id", profile.raider_id)
    new_responsibility_id = data.get("responsibility_id", profile.responsibility_id)
    pair_error = _validate_pair(new_raider_id, new_responsibility_id, exclude_id=profile.id)
    if pair_error:
        return jsonify(error=pair_error), 400

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
