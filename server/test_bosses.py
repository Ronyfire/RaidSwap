def make_boss(client, **overrides):
    data = {"name": "Test Boss", "raid": "The Venomous Abyss", "order": 1}
    data.update(overrides)
    return client.post("/api/bosses", json=data)


def test_create_and_get_boss(client):
    resp = make_boss(client)
    assert resp.status_code == 201
    boss_id = resp.get_json()["id"]

    resp = client.get(f"/api/bosses/{boss_id}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Test Boss"


def test_list_bosses(client):
    make_boss(client)
    resp = client.get("/api/bosses")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_create_boss_missing_fields(client):
    resp = client.post("/api/bosses", json={"name": "Incompleto"})
    assert resp.status_code == 400
    assert "raid" in resp.get_json()["error"]


def test_update_boss(client):
    boss_id = make_boss(client).get_json()["id"]

    resp = client.put(f"/api/bosses/{boss_id}", json={"order": 2})
    assert resp.status_code == 200
    assert resp.get_json()["order"] == 2
    assert resp.get_json()["raid"] == "The Venomous Abyss"


def test_delete_boss(client):
    boss_id = make_boss(client).get_json()["id"]

    resp = client.delete(f"/api/bosses/{boss_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/bosses/{boss_id}")
    assert resp.status_code == 404


def test_get_boss_not_found(client):
    resp = client.get("/api/bosses/999")
    assert resp.status_code == 404
