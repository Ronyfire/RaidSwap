def make_raider(client, **overrides):
    data = {"name": "Testorix", "wow_class": "Warrior", "spec": "Fury", "role": "DPS"}
    data.update(overrides)
    return client.post("/api/raiders", json=data)


def test_create_and_get_raider(client):
    resp = make_raider(client)
    assert resp.status_code == 201
    raider_id = resp.get_json()["id"]

    resp = client.get(f"/api/raiders/{raider_id}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Testorix"


def test_list_raiders(client):
    make_raider(client)
    resp = client.get("/api/raiders")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_create_raider_missing_fields(client):
    resp = client.post("/api/raiders", json={"name": "Incompleto"})
    assert resp.status_code == 400
    assert "wow_class" in resp.get_json()["error"]


def test_update_raider(client):
    raider_id = make_raider(client).get_json()["id"]

    resp = client.put(f"/api/raiders/{raider_id}", json={"spec": "Arms"})
    assert resp.status_code == 200
    assert resp.get_json()["spec"] == "Arms"
    assert resp.get_json()["wow_class"] == "Warrior"


def test_delete_raider(client):
    raider_id = make_raider(client).get_json()["id"]

    resp = client.delete(f"/api/raiders/{raider_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/raiders/{raider_id}")
    assert resp.status_code == 404


def test_get_raider_not_found(client):
    resp = client.get("/api/raiders/999")
    assert resp.status_code == 404
