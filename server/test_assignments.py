def make_raider(client, **overrides):
    data = {"name": "Testorix", "wow_class": "Mage", "spec": "Frost", "role": "DPS"}
    data.update(overrides)
    return client.post("/api/raiders", json=data).get_json()["id"]


def make_responsibility(client, **overrides):
    data = {"name": "Kick rotation"}
    data.update(overrides)
    return client.post("/api/responsibilities", json=data).get_json()["id"]


def test_create_assignment_with_responsibility_only(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)

    resp = client.post(
        "/api/assignments", json={"raider_id": raider_id, "responsibility_id": responsibility_id}
    )
    assert resp.status_code == 201


def test_create_assignment_missing_raider(client):
    resp = client.post("/api/assignments", json={})
    assert resp.status_code == 400


def test_create_assignment_raider_not_found(client):
    responsibility_id = make_responsibility(client)
    resp = client.post(
        "/api/assignments", json={"raider_id": 999, "responsibility_id": responsibility_id}
    )
    assert resp.status_code == 404


def test_create_assignment_responsibility_not_found(client):
    raider_id = make_raider(client)
    resp = client.post(
        "/api/assignments", json={"raider_id": raider_id, "responsibility_id": 999}
    )
    assert resp.status_code == 404


def test_create_assignment_without_responsibility_or_position_fails(client):
    # Ejercita el event listener de models.py a traves del endpoint real,
    # no una segunda validacion en la ruta.
    raider_id = make_raider(client)

    resp = client.post("/api/assignments", json={"raider_id": raider_id})
    assert resp.status_code == 400


def test_update_assignment_removing_only_link_fails(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)
    assignment_id = client.post(
        "/api/assignments", json={"raider_id": raider_id, "responsibility_id": responsibility_id}
    ).get_json()["id"]

    resp = client.put(f"/api/assignments/{assignment_id}", json={"responsibility_id": None})
    assert resp.status_code == 400


def test_update_assignment_raider_not_found(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)
    assignment_id = client.post(
        "/api/assignments", json={"raider_id": raider_id, "responsibility_id": responsibility_id}
    ).get_json()["id"]

    resp = client.put(f"/api/assignments/{assignment_id}", json={"raider_id": 999})
    assert resp.status_code == 404


def test_update_assignment_responsibility_not_found(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)
    assignment_id = client.post(
        "/api/assignments", json={"raider_id": raider_id, "responsibility_id": responsibility_id}
    ).get_json()["id"]

    resp = client.put(f"/api/assignments/{assignment_id}", json={"responsibility_id": 999})
    assert resp.status_code == 404


def test_delete_assignment(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)
    assignment_id = client.post(
        "/api/assignments", json={"raider_id": raider_id, "responsibility_id": responsibility_id}
    ).get_json()["id"]

    resp = client.delete(f"/api/assignments/{assignment_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/assignments/{assignment_id}")
    assert resp.status_code == 404


def test_get_assignment_not_found(client):
    resp = client.get("/api/assignments/999")
    assert resp.status_code == 404
