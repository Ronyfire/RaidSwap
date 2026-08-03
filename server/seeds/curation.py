import re

from extensions import db
from models import Assignment, Boss, Position, Raider, Responsibility

# See projects/venomous-abyss-curation.md — this is PTR placeholder data
# (confidence=unconfirmed), refined against real notes in the 4-18 ago window.
# Boss names below match seeds/venomous_abyss.py exactly (the curation doc's
# headers have extra detail, e.g. "The Twin Fangs (Vexhul & Ithraz)").

# Mythic takes 20 fixed raiders; the roster carries 24 (20 active + 4 bench)
# — that gap is the product's premise, RaidSwap manages swapping bench in
# for active. See projects/venomous-abyss-curation.md.
RAIDERS = [
    ("Paco", "Warrior", "Protection", "Tank", "active"),
    ("Orrin", "Death Knight", "Blood", "Tank", "active"),
    ("Kaeli", "Priest", "Holy", "Healer", "active"),
    ("Grethak", "Shaman", "Restoration", "Healer", "active"),
    ("Mistra", "Monk", "Mistweaver", "Healer", "active"),
    ("Aldric", "Paladin", "Holy", "Healer", "active"),
    ("Sylvi", "Mage", "Frost", "DPS", "active"),
    ("Doran", "Rogue", "Assassination", "DPS", "active"),
    ("Ilse", "Hunter", "Beast Mastery", "DPS", "active"),
    ("Brannor", "Paladin", "Retribution", "DPS", "active"),
    ("Vashti", "Warlock", "Destruction", "DPS", "active"),
    ("Fenn", "Warrior", "Fury", "DPS", "active"),
    ("Nyx", "Rogue", "Subtlety", "DPS", "active"),
    ("Torvald", "Death Knight", "Frost", "DPS", "active"),
    ("Elowen", "Druid", "Balance", "DPS", "active"),
    ("Kaelen", "Mage", "Fire", "DPS", "active"),
    ("Rurik", "Shaman", "Elemental", "DPS", "active"),
    ("Sabine", "Priest", "Shadow", "DPS", "active"),
    ("Garrik", "Hunter", "Marksmanship", "DPS", "active"),
    ("Lyra", "Warlock", "Affliction", "DPS", "active"),
    ("Quill", "Rogue", "Outlaw", "DPS", "bench"),
    ("Dagen", "Demon Hunter", "Havoc", "DPS", "bench"),
    ("Maren", "Paladin", "Protection", "Tank", "bench"),
    ("Cillian", "Evoker", "Preservation", "Healer", "bench"),
]

# boss_name -> [(responsibility_name, requires_role, note_line, type), ...]
# type is a best-guess categorization (interrupt/cooldown/mechanic/assignment/
# positioning, see projects/notes-model.md) — same "unconfirmed, refine later"
# status as the rest of this PTR data, not a precise ruling.
BOSS_RESPONSIBILITIES = {
    "Nek'zali the Soulcoiler": [
        ("Interrupt Soulcoil Ritual", "DPS", "ph:1;tag:Sylvi;", "interrupt"),
        ("Spirit adds", "DPS", "ph:1;tag:Doran;tag:Ilse;", "assignment"),
        ("Nek'zali tank swap", "Tank", "tag:Paco;", "mechanic"),
        ("Venom pulse heal CD", "Healer", "ph:2;tag:Kaeli;", "cooldown"),
    ],
    "Entombed Sentinels": [
        ("Tank Blood of Ula'tek", "Tank", "tag:Paco;", "assignment"),
        ("Tank Breath of Ula'tek", "Tank", "tag:Orrin;", "assignment"),
        ("Dominance soak / dispel", "Healer", "tag:Grethak;", "mechanic"),
    ],
    "Vashnik the Malignant": [
        ("Venom dispels", "Healer", "tag:Kaeli;tag:Mistra;", "mechanic"),
        ("Tank Vashnik (stacks)", "Tank", "tag:Orrin;", "assignment"),
        ("Soak poison pools", "DPS", "tag:Brannor;", "mechanic"),
    ],
    "The Lost Explorers": [
        ("CC tortollan poseídos", "DPS", "tag:Sylvi;tag:Doran;", "mechanic"),
        ("Kill order (prioridad)", "DPS", "tag:Ilse;tag:Vashti;", "assignment"),
        ("Tank líder poseído", "Tank", "tag:Paco;", "assignment"),
    ],
    "Sszorak": [
        ("Encarar frontales (Mutilate/Ravage)", "Tank", "tag:Paco;", "positioning"),
        ("Corroding Venom tank swap", "Tank", "tag:Orrin;", "mechanic"),
        ("Pop Viscous Cysts", "DPS", "tag:Doran;tag:Brannor;", "mechanic"),
        ("Howling Maelstrom burn (Bloodlust)", "DPS", "ph:2;tag:Ilse;", "cooldown"),
    ],
    "The Twin Fangs": [
        ("Tank Vexhul", "Tank", "tag:Paco;", "assignment"),
        ("Tank Ithraz", "Tank", "tag:Orrin;", "assignment"),
        ("Balance de daño (2 targets)", "DPS", "tag:Sylvi;tag:Vashti;", "assignment"),
        ("Feeding / add management", "DPS", "tag:Doran;", "assignment"),
    ],
    "The Coiled Altar": [
        ("Interrupt fase Zul'jan", "DPS", "ph:1;tag:Sylvi;", "interrupt"),
        ("Handling de posesión", "Healer", "ph:2;tag:Kaeli;", "mechanic"),
        ("Tank dual-boss finish", "Tank", "ph:3;tag:Paco;tag:Orrin;", "assignment"),
    ],
    "Ula'tek": [
        ("Tank Ula'tek", "Tank", "tag:Paco;", "assignment"),
        ("Venom P1 (dispels/heal CD)", "Healer", "ph:1;tag:Grethak;", "cooldown"),
        ("Add management P2", "DPS", "ph:2;tag:Doran;tag:Ilse;", "assignment"),
        ("Arena colapsante P3 (movimiento)", "DPS", "ph:3;tag:Vashti;", "positioning"),
    ],
}

TAG_PATTERN = re.compile(r"tag:([^;]+);")


def _upsert_raider(name, wow_class, spec, role, status):
    raider = Raider.query.filter_by(name=name).first()
    if raider is None:
        raider = Raider(name=name, wow_class=wow_class, spec=spec, role=role, status=status)
        db.session.add(raider)
    else:
        raider.wow_class, raider.spec, raider.role, raider.status = wow_class, spec, role, status
    return raider


def _upsert_responsibility(name, requires_role, note_line, type_):
    responsibility = Responsibility.query.filter_by(name=name).first()
    if responsibility is None:
        responsibility = Responsibility(
            name=name,
            requires_role=requires_role,
            note_line=note_line,
            type=type_,
            confidence="unconfirmed",
        )
        db.session.add(responsibility)
    else:
        responsibility.requires_role = requires_role
        responsibility.note_line = note_line
        responsibility.type = type_
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
    for name, wow_class, spec, role, status in RAIDERS:
        _upsert_raider(name, wow_class, spec, role, status)
    db.session.flush()

    for boss_name, responsibilities in BOSS_RESPONSIBILITIES.items():
        boss = Boss.query.filter_by(name=boss_name).first()
        if boss is None:
            raise ValueError(
                f"Boss '{boss_name}' not found — run `flask seed-venomous-abyss` first."
            )
        for index, (resp_name, requires_role, note_line, type_) in enumerate(responsibilities):
            responsibility = _upsert_responsibility(resp_name, requires_role, note_line, type_)
            db.session.flush()
            _upsert_position(boss, responsibility, requires_role, index)
            db.session.flush()
            _sync_assignments(responsibility, note_line)

    db.session.commit()
