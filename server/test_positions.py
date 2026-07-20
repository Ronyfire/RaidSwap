def make_boss(client, **overrides):
    data = {"name": "Test Boss", "raid": "The Venomous Abyss", "order": 1}
    data.update(overrides)
    return client.post("/api/bosses", json=data).get_json()["id"]


def make_responsibility(client, **overrides):
    data = {"name": "Kick rotation"}
    data.update(overrides)
    return client.post("/api/responsibilities", json=data).get_json()["id"]


def make_position(client, boss_id, **overrides):
    data = {"x": 10.5, "y": 20.5, "boss_id": boss_id}
    data.update(overrides)
    return client.post("/api/positions", json=data)


def test_create_and_get_position(client):
    boss_id = make_boss(client)
    resp = make_position(client, boss_id)
    assert resp.status_code == 201
    position_id = resp.get_json()["id"]

    resp = client.get(f"/api/positions/{position_id}")
    assert resp.status_code == 200
    assert resp.get_json()["boss_id"] == boss_id


def test_list_positions(client):
    boss_id = make_boss(client)
    make_position(client, boss_id)
    resp = client.get("/api/positions")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_create_position_missing_fields(client):
    resp = client.post("/api/positions", json={"x": 1.0})
    assert resp.status_code == 400


def test_create_position_x_zero_is_not_missing(client):
    # x=0 es un valor valido, no deberia contar como "campo faltante"
    boss_id = make_boss(client)
    resp = make_position(client, boss_id, x=0, y=0)
    assert resp.status_code == 201
    assert resp.get_json()["x"] == 0


def test_create_position_boss_not_found(client):
    resp = make_position(client, boss_id=999)
    assert resp.status_code == 404


def test_create_position_responsibility_not_found(client):
    boss_id = make_boss(client)
    resp = make_position(client, boss_id, responsibility_id=999)
    assert resp.status_code == 404


def test_create_position_with_responsibility(client):
    boss_id = make_boss(client)
    responsibility_id = make_responsibility(client)
    resp = make_position(client, boss_id, responsibility_id=responsibility_id)
    assert resp.status_code == 201
    assert resp.get_json()["responsibility_id"] == responsibility_id


def test_update_position(client):
    boss_id = make_boss(client)
    position_id = make_position(client, boss_id).get_json()["id"]

    resp = client.put(f"/api/positions/{position_id}", json={"requires_role": "tank"})
    assert resp.status_code == 200
    assert resp.get_json()["requires_role"] == "tank"


def test_update_position_boss_not_found(client):
    boss_id = make_boss(client)
    position_id = make_position(client, boss_id).get_json()["id"]

    resp = client.put(f"/api/positions/{position_id}", json={"boss_id": 999})
    assert resp.status_code == 404


def test_update_position_responsibility_not_found(client):
    boss_id = make_boss(client)
    position_id = make_position(client, boss_id).get_json()["id"]

    resp = client.put(f"/api/positions/{position_id}", json={"responsibility_id": 999})
    assert resp.status_code == 404


def test_delete_position(client):
    boss_id = make_boss(client)
    position_id = make_position(client, boss_id).get_json()["id"]

    resp = client.delete(f"/api/positions/{position_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/positions/{position_id}")
    assert resp.status_code == 404


def test_get_position_not_found(client):
    resp = client.get("/api/positions/999")
    assert resp.status_code == 404
