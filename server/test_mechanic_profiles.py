def make_raider(client, **overrides):
    data = {"name": "Testorix", "wow_class": "Mage", "spec": "Frost", "role": "DPS"}
    data.update(overrides)
    return client.post("/api/raiders", json=data).get_json()["id"]


def make_responsibility(client, **overrides):
    data = {"name": "Kick rotation"}
    data.update(overrides)
    return client.post("/api/responsibilities", json=data).get_json()["id"]


def test_create_and_get_mechanic_profile(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)

    resp = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": responsibility_id,
            "proficiency_level": "has_done_it",
        },
    )
    assert resp.status_code == 201
    profile_id = resp.get_json()["id"]

    resp = client.get(f"/api/mechanic-profiles/{profile_id}")
    assert resp.status_code == 200
    assert resp.get_json()["proficiency_level"] == "has_done_it"


def test_create_mechanic_profile_missing_fields(client):
    resp = client.post("/api/mechanic-profiles", json={})
    assert resp.status_code == 400


def test_create_mechanic_profile_raider_not_found(client):
    responsibility_id = make_responsibility(client)
    resp = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": 999,
            "responsibility_id": responsibility_id,
            "proficiency_level": "never",
        },
    )
    assert resp.status_code == 404


def test_create_mechanic_profile_responsibility_not_found(client):
    raider_id = make_raider(client)
    resp = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": 999,
            "proficiency_level": "never",
        },
    )
    assert resp.status_code == 404


def test_update_mechanic_profile(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)
    profile_id = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": responsibility_id,
            "proficiency_level": "never",
        },
    ).get_json()["id"]

    resp = client.put(
        f"/api/mechanic-profiles/{profile_id}", json={"proficiency_level": "mastered"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["proficiency_level"] == "mastered"


def test_update_mechanic_profile_raider_not_found(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)
    profile_id = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": responsibility_id,
            "proficiency_level": "never",
        },
    ).get_json()["id"]

    resp = client.put(f"/api/mechanic-profiles/{profile_id}", json={"raider_id": 999})
    assert resp.status_code == 404


def test_delete_mechanic_profile(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)
    profile_id = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": responsibility_id,
            "proficiency_level": "never",
        },
    ).get_json()["id"]

    resp = client.delete(f"/api/mechanic-profiles/{profile_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/mechanic-profiles/{profile_id}")
    assert resp.status_code == 404
