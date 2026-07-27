from models import Boss
from seeds.venomous_abyss import BOSSES, seed_venomous_abyss


def test_seed_creates_all_bosses(app):
    seed_venomous_abyss()
    assert Boss.query.count() == len(BOSSES)


def test_seed_is_idempotent(app):
    seed_venomous_abyss()
    seed_venomous_abyss()
    assert Boss.query.count() == len(BOSSES)


def test_seed_sets_raid_and_order(app):
    seed_venomous_abyss()
    boss = Boss.query.filter_by(name="Ula'tek").first()
    assert boss.raid == "The Venomous Abyss"
    assert boss.order == 8
