from extensions import db
from models import Boss

RAID_NAME = "The Venomous Abyss"

BOSSES = [
    ("Nek'zali the Soulcoiler", 1),
    ("Entombed Sentinels", 2),
    ("The Lost Explorers", 3),
    ("Vashnik the Malignant", 4),
    ("Sszorak", 5),
    ("The Twin Fangs", 6),
    ("The Coiled Altar", 7),
    ("Ula'tek", 8),
]


def seed_venomous_abyss():
    for name, order in BOSSES:
        boss = Boss.query.filter_by(name=name).first()
        if boss is None:
            db.session.add(Boss(name=name, raid=RAID_NAME, order=order))
        else:
            boss.raid = RAID_NAME
            boss.order = order
    db.session.commit()
