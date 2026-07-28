def test_register_creates_user_and_returns_token(unauthenticated_client):
    resp = unauthenticated_client.post(
        "/api/auth/register", json={"email": "leader@guild.gg", "password": "hunter2"}
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["access_token"]
    assert body["user"]["email"] == "leader@guild.gg"
    assert body["user"]["tier"] == "free"


def test_register_missing_fields(unauthenticated_client):
    resp = unauthenticated_client.post("/api/auth/register", json={"email": "leader@guild.gg"})
    assert resp.status_code == 400


def test_register_duplicate_email(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register", json={"email": "leader@guild.gg", "password": "hunter2"}
    )
    resp = unauthenticated_client.post(
        "/api/auth/register", json={"email": "leader@guild.gg", "password": "different"}
    )
    assert resp.status_code == 409


def test_login_with_correct_password(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register", json={"email": "leader@guild.gg", "password": "hunter2"}
    )
    resp = unauthenticated_client.post(
        "/api/auth/login", json={"email": "leader@guild.gg", "password": "hunter2"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["access_token"]


def test_login_with_wrong_password(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register", json={"email": "leader@guild.gg", "password": "hunter2"}
    )
    resp = unauthenticated_client.post(
        "/api/auth/login", json={"email": "leader@guild.gg", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_login_unknown_email(unauthenticated_client):
    resp = unauthenticated_client.post(
        "/api/auth/login", json={"email": "nobody@guild.gg", "password": "whatever"}
    )
    assert resp.status_code == 401


def test_protected_route_without_token_is_rejected(unauthenticated_client):
    resp = unauthenticated_client.get("/api/raiders")
    assert resp.status_code == 401


def test_protected_route_with_token_is_allowed(client):
    resp = client.get("/api/raiders")
    assert resp.status_code == 200


def test_health_does_not_require_auth(unauthenticated_client):
    resp = unauthenticated_client.get("/health")
    assert resp.status_code == 200
