import pytest

from app import create_app
from extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///:memory:", TESTING=True)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    from flask_jwt_extended import create_access_token

    token = create_access_token(identity="1")
    test_client = app.test_client()
    test_client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return test_client


@pytest.fixture
def unauthenticated_client(app):
    return app.test_client()
