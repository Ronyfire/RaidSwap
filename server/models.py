from datetime import datetime, timezone

from sqlalchemy import event

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # "free" is the only tier in use today — see #55/#56 in projects/agent-architecture.md
    # for the "member" tier + BYOK + billing hooks this leaves room for.
    tier = db.Column(db.String(20), nullable=False, default="free")

    def to_dict(self):
        return {"id": self.id, "email": self.email, "tier": self.tier}


class Raider(db.Model):
    __tablename__ = "raiders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    wow_class = db.Column(db.String(40), nullable=False)
    spec = db.Column(db.String(40), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    # "active" / "bench" — Mythic takes 20, the roster carries more (see
    # projects/venomous-abyss-curation.md). apply_reassignment flips a
    # bench raider to active when they get swapped in.
    status = db.Column(db.String(20), nullable=False, default="active")

    mechanic_profiles = db.relationship("MechanicProfile", back_populates="raider")
    assignments = db.relationship("Assignment", back_populates="raider")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "wow_class": self.wow_class,
            "spec": self.spec,
            "role": self.role,
            "status": self.status,
        }


class Boss(db.Model):
    __tablename__ = "bosses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    raid = db.Column(db.String(120), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    positions = db.relationship("Position", back_populates="boss")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "raid": self.raid,
            "order": self.order,
        }


class Responsibility(db.Model):
    __tablename__ = "responsibilities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    actor_label = db.Column(db.String(120))
    difficulty_variant = db.Column(db.String(20))
    requires_role = db.Column(db.String(20))
    requires_prior_experience = db.Column(db.Boolean, nullable=False, default=False)
    description = db.Column(db.Text)
    confidence = db.Column(db.String(20), nullable=False, default="unconfirmed")
    note_line = db.Column(db.String(500), nullable=True)
    # Content axis from Viserio's note taxonomy (see projects/notes-model.md):
    # interrupt / cooldown / mechanic / assignment / positioning. Nullable —
    # existing/uncategorized responsibilities aren't forced to pick one.
    type = db.Column(db.String(20), nullable=True)
    last_updated = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    positions = db.relationship("Position", back_populates="responsibility")
    mechanic_profiles = db.relationship("MechanicProfile", back_populates="responsibility")
    assignments = db.relationship("Assignment", back_populates="responsibility")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "actor_label": self.actor_label,
            "difficulty_variant": self.difficulty_variant,
            "requires_role": self.requires_role,
            "requires_prior_experience": self.requires_prior_experience,
            "description": self.description,
            "confidence": self.confidence,
            "note_line": self.note_line,
            "type": self.type,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class Position(db.Model):
    __tablename__ = "positions"

    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    boss_id = db.Column(db.Integer, db.ForeignKey("bosses.id"), nullable=False)
    requires_role = db.Column(db.String(20))
    # "melee" / "ranged" — nullable, same "unset = no constraint" pattern as
    # requires_role. Not backfilled on the curated data yet: which spot is
    # melee vs. ranged is real fight knowledge (see CLAUDE.md), for Robert to
    # curate, not to guess (#18).
    requires_range = db.Column(db.String(10))
    responsibility_id = db.Column(db.Integer, db.ForeignKey("responsibilities.id"), nullable=True)

    boss = db.relationship("Boss", back_populates="positions")
    responsibility = db.relationship("Responsibility", back_populates="positions")
    assignments = db.relationship("Assignment", back_populates="position")

    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "boss_id": self.boss_id,
            "requires_role": self.requires_role,
            "requires_range": self.requires_range,
            "responsibility_id": self.responsibility_id,
        }


class MechanicProfile(db.Model):
    __tablename__ = "mechanic_profiles"
    __table_args__ = (db.UniqueConstraint("raider_id", "responsibility_id"),)

    id = db.Column(db.Integer, primary_key=True)
    raider_id = db.Column(db.Integer, db.ForeignKey("raiders.id"), nullable=False)
    responsibility_id = db.Column(db.Integer, db.ForeignKey("responsibilities.id"), nullable=False)
    # Valores esperados: "never", "has_done_it", "mastered" — string libre, sin Enum por ahora
    proficiency_level = db.Column(db.String(20), nullable=False)

    raider = db.relationship("Raider", back_populates="mechanic_profiles")
    responsibility = db.relationship("Responsibility", back_populates="mechanic_profiles")

    def to_dict(self):
        return {
            "id": self.id,
            "raider_id": self.raider_id,
            "responsibility_id": self.responsibility_id,
            "proficiency_level": self.proficiency_level,
        }


class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    raider_id = db.Column(db.Integer, db.ForeignKey("raiders.id"), nullable=False)
    responsibility_id = db.Column(db.Integer, db.ForeignKey("responsibilities.id"), nullable=True)
    position_id = db.Column(db.Integer, db.ForeignKey("positions.id"), nullable=True)
    active_note_ref = db.Column(db.String(255))

    raider = db.relationship("Raider", back_populates="assignments")
    responsibility = db.relationship("Responsibility", back_populates="assignments")
    position = db.relationship("Position", back_populates="assignments")

    def to_dict(self):
        return {
            "id": self.id,
            "raider_id": self.raider_id,
            "responsibility_id": self.responsibility_id,
            "position_id": self.position_id,
            "active_note_ref": self.active_note_ref,
        }


@event.listens_for(Assignment, "before_insert")
@event.listens_for(Assignment, "before_update")
def validate_assignment_target(mapper, connection, target):
    if target.responsibility_id is None and target.position_id is None:
        raise ValueError(
            "Assignment requiere al menos responsibility_id o position_id"
        )
