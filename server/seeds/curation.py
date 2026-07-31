import re

from extensions import db
from models import Assignment, Boss, Position, Raider, Responsibility

# See projects/venomous-abyss-curation.md — this is PTR placeholder data
# (confidence=unconfirmed), refined against real notes in the 4-18 ago window.
# Boss names below match seeds/venomous_abyss.py exactly (the curation doc's
# headers have extra detail, e.g. "The Twin Fangs (Vexhul & Ithraz)").

RAIDERS = [
    ("Paco", "Warrior", "Protection", "Tank"),
    ("Orrin", "Death Knight", "Blood", "Tank"),
    ("Kaeli", "Priest", "Holy", "Healer"),
    ("Grethak", "Shaman", "Restoration", "Healer"),
    ("Mistra", "Monk", "Mistweaver", "Healer"),
    ("Sylvi", "Mage", "Frost", "DPS"),
    ("Doran", "Rogue", "Assassination", "DPS"),
    ("Ilse", "Hunter", "Beast Mastery", "DPS"),
    ("Brannor", "Paladin", "Retribution", "DPS"),
    ("Vashti", "Warlock", "Destruction", "DPS"),
]

# boss_name -> [(responsibility_name, requires_role, note_line), ...]
BOSS_RESPONSIBILITIES = {
    "Nek'zali the Soulcoiler": [
        ("Interrupt Soulcoil Ritual", "DPS", "ph:1;tag:Sylvi;"),
        ("Spirit adds", "DPS", "ph:1;tag:Doran;tag:Ilse;"),
        ("Nek'zali tank swap", "Tank", "tag:Paco;"),
        ("Venom pulse heal CD", "Healer", "ph:2;tag:Kaeli;"),
    ],
    "Entombed Sentinels": [
        ("Tank Blood of Ula'tek", "Tank", "tag:Paco;"),
        ("Tank Breath of Ula'tek", "Tank", "tag:Orrin;"),
        ("Dominance soak / dispel", "Healer", "tag:Grethak;"),
    ],
    "Vashnik the Malignant": [
        ("Venom dispels", "Healer", "tag:Kaeli;tag:Mistra;"),
        ("Tank Vashnik (stacks)", "Tank", "tag:Orrin;"),
        ("Soak poison pools", "DPS", "tag:Brannor;"),
    ],
    "The Lost Explorers": [
        ("CC tortollan poseídos", "DPS", "tag:Sylvi;tag:Doran;"),
        ("Kill order (prioridad)", "DPS", "tag:Ilse;tag:Vashti;"),
        ("Tank líder poseído", "Tank", "tag:Paco;"),
    ],
    "Sszorak": [
        ("Encarar frontales (Mutilate/Ravage)", "Tank", "tag:Paco;"),
        ("Corroding Venom tank swap", "Tank", "tag:Orrin;"),
        ("Pop Viscous Cysts", "DPS", "tag:Doran;tag:Brannor;"),
        ("Howling Maelstrom burn (Bloodlust)", "DPS", "ph:2;tag:Ilse;"),
    ],
    "The Twin Fangs": [
        ("Tank Vexhul", "Tank", "tag:Paco;"),
        ("Tank Ithraz", "Tank", "tag:Orrin;"),
        ("Balance de daño (2 targets)", "DPS", "tag:Sylvi;tag:Vashti;"),
        ("Feeding / add management", "DPS", "tag:Doran;"),
    ],
    "The Coiled Altar": [
        ("Interrupt fase Zul'jan", "DPS", "ph:1;tag:Sylvi;"),
        ("Handling de posesión", "Healer", "ph:2;tag:Kaeli;"),
        ("Tank dual-boss finish", "Tank", "ph:3;tag:Paco;tag:Orrin;"),
    ],
    "Ula'tek": [
        ("Tank Ula'tek", "Tank", "tag:Paco;"),
        ("Venom P1 (dispels/heal CD)", "Healer", "ph:1;tag:Grethak;"),
        ("Add management P2", "DPS", "ph:2;tag:Doran;tag:Ilse;"),
        ("Arena colapsante P3 (movimiento)", "DPS", "ph:3;tag:Vashti;"),
    ],
}

TAG_PATTERN = re.compile(r"tag:([^;]+);")


def _upsert_raider(name, wow_class, spec, role):
    raider = Raider.query.filter_by(name=name).first()
    if raider is None:
        raider = Raider(name=name, wow_class=wow_class, spec=spec, role=role)
        db.session.add(raider)
    else:
        raider.wow_class, raider.spec, raider.role = wow_class, spec, role
    return raider


def _upsert_responsibility(name, requires_role, note_line):
    responsibility = Responsibility.query.filter_by(name=name).first()
    if responsibility is None:
        responsibility = Responsibility(
            name=name,
            requires_role=requires_role,
            note_line=note_line,
            confidence="unconfirmed",
        )
        db.session.add(responsibility)
    else:
        responsibility.requires_role = requires_role
        responsibility.note_line = note_line
        responsibility.confidence = "unconfirmed"
    return responsibility


def _upsert_position(boss, responsibility, requires_role, index):
    position = Position.query.filter_by(
        boss_id=boss.id, responsibility_id=responsibility.id
    ).first()
    # Placeholder coords — no raidplan overlay yet, real x/y come later from
    # raidplan.io/Viserio and update these same rows.
    x, y = float(index * 10), 0.0
    if position is None:
        position = Position(
            x=x, y=y, boss_id=boss.id, responsibility_id=responsibility.id,
            requires_role=requires_role,
        )
        db.session.add(position)
    else:
        position.requires_role = requires_role


def _sync_assignments(responsibility, note_line):
    desired_names = TAG_PATTERN.findall(note_line)
    desired_raiders = {
        r.name: r for r in Raider.query.filter(Raider.name.in_(desired_names)).all()
    }

    existing = Assignment.query.filter_by(responsibility_id=responsibility.id).all()
    existing_by_raider_name = {a.raider.name: a for a in existing}

    for stale_name, assignment in existing_by_raider_name.items():
        if stale_name not in desired_raiders:
            db.session.delete(assignment)

    for name, raider in desired_raiders.items():
        if name not in existing_by_raider_name:
            db.session.add(Assignment(raider_id=raider.id, responsibility_id=responsibility.id))


def seed_curation():
    for name, wow_class, spec, role in RAIDERS:
        _upsert_raider(name, wow_class, spec, role)
    db.session.flush()

    for boss_name, responsibilities in BOSS_RESPONSIBILITIES.items():
        boss = Boss.query.filter_by(name=boss_name).first()
        if boss is None:
            raise ValueError(
                f"Boss '{boss_name}' not found — run `flask seed-venomous-abyss` first."
            )
        for index, (resp_name, requires_role, note_line) in enumerate(responsibilities):
            responsibility = _upsert_responsibility(resp_name, requires_role, note_line)
            db.session.flush()
            _upsert_position(boss, responsibility, requires_role, index)
            db.session.flush()
            _sync_assignments(responsibility, note_line)

    db.session.commit()
