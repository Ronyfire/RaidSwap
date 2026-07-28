import pytest

from app import create_app
from extensions import db
from services import rate_limiter


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    rate_limiter.reset()
    yield
    rate_limiter.reset()


@pytest.fixture
def app():
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "TESTING": True})

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    from flask_jwt_extended import create_access_token

    from models import User

    user = User(email="leader@guild.gg", password_hash="unused", tier="free")
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    test_client = app.test_client()
    test_client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return test_client


@pytest.fixture
def unauthenticated_client(app):
    return app.test_client()
