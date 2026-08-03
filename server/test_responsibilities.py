def make_responsibility(client, **overrides):
    data = {"name": "Kick rotation"}
    data.update(overrides)
    return client.post("/api/responsibilities", json=data)


def test_create_responsibility_only_name_uses_defaults(client):
    resp = make_responsibility(client)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["confidence"] == "unconfirmed"
    assert body["requires_prior_experience"] is False


def test_create_responsibility_missing_name(client):
    resp = client.post("/api/responsibilities", json={})
    assert resp.status_code == 400


def test_partial_update_does_not_touch_other_fields(client):
    resp_id = make_responsibility(client).get_json()["id"]

    resp = client.put(
        f"/api/responsibilities/{resp_id}", json={"requires_prior_experience": True}
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["requires_prior_experience"] is True
    assert body["name"] == "Kick rotation"


def test_explicit_false_is_applied(client):
    # Regresión: si el filtro del PUT usara data.get(f) en vez de "f in data",
    # un False explícito se ignoraría silenciosamente por ser falsy.
    resp_id = make_responsibility(
        client, requires_prior_experience=True
    ).get_json()["id"]

    resp = client.put(
        f"/api/responsibilities/{resp_id}", json={"requires_prior_experience": False}
    )
    assert resp.status_code == 200
    assert resp.get_json()["requires_prior_experience"] is False


def test_create_responsibility_with_note_line(client):
    resp = make_responsibility(client, note_line="tag:Rob;")
    assert resp.status_code == 201
    assert resp.get_json()["note_line"] == "tag:Rob;"


def test_update_note_line(client):
    resp_id = make_responsibility(client).get_json()["id"]

    resp = client.put(f"/api/responsibilities/{resp_id}", json={"note_line": "tag:Sam;"})
    assert resp.status_code == 200
    assert resp.get_json()["note_line"] == "tag:Sam;"


def test_create_responsibility_with_type(client):
    resp = make_responsibility(client, type="interrupt")
    assert resp.status_code == 201
    assert resp.get_json()["type"] == "interrupt"


def test_create_responsibility_type_defaults_to_none(client):
    resp = make_responsibility(client)
    assert resp.get_json()["type"] is None


def test_update_type(client):
    resp_id = make_responsibility(client).get_json()["id"]

    resp = client.put(f"/api/responsibilities/{resp_id}", json={"type": "cooldown"})
    assert resp.status_code == 200
    assert resp.get_json()["type"] == "cooldown"


def test_delete_responsibility(client):
    resp_id = make_responsibility(client).get_json()["id"]

    resp = client.delete(f"/api/responsibilities/{resp_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/responsibilities/{resp_id}")
    assert resp.status_code == 404
