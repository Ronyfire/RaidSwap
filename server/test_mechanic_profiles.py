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


def test_create_mechanic_profile_duplicate_pair_rejected(client):
    raider_id = make_raider(client)
    responsibility_id = make_responsibility(client)
    payload = {
        "raider_id": raider_id,
        "responsibility_id": responsibility_id,
        "proficiency_level": "never",
    }
    first = client.post("/api/mechanic-profiles", json=payload)
    assert first.status_code == 201

    second = client.post("/api/mechanic-profiles", json=payload)
    assert second.status_code == 400
    assert "already exists" in second.get_json()["error"]


def test_create_mechanic_profile_role_incompatible_rejected(client):
    raider_id = make_raider(client, name="Healy", role="Healer")
    responsibility_id = make_responsibility(client, name="Interrupt", requires_role="DPS")

    resp = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": responsibility_id,
            "proficiency_level": "never",
        },
    )
    assert resp.status_code == 400
    assert "Healer" in resp.get_json()["error"] and "DPS" in resp.get_json()["error"]


def test_update_mechanic_profile_into_duplicate_pair_rejected(client):
    raider_id = make_raider(client)
    responsibility_a = make_responsibility(client, name="Interrupt A")
    responsibility_b = make_responsibility(client, name="Interrupt B")
    client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": responsibility_a,
            "proficiency_level": "never",
        },
    )
    profile_b_id = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": responsibility_b,
            "proficiency_level": "never",
        },
    ).get_json()["id"]

    resp = client.put(
        f"/api/mechanic-profiles/{profile_b_id}", json={"responsibility_id": responsibility_a}
    )
    assert resp.status_code == 400
    assert "already exists" in resp.get_json()["error"]


def test_update_mechanic_profile_own_pair_unchanged_is_allowed(client):
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
        f"/api/mechanic-profiles/{profile_id}",
        json={"raider_id": raider_id, "proficiency_level": "mastered"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["proficiency_level"] == "mastered"


def test_update_mechanic_profile_role_incompatible_rejected(client):
    raider_id = make_raider(client, role="Tank")
    tank_resp = make_responsibility(client, name="Taunt swap", requires_role="Tank")
    dps_resp = make_responsibility(client, name="Interrupt", requires_role="DPS")
    profile_id = client.post(
        "/api/mechanic-profiles",
        json={
            "raider_id": raider_id,
            "responsibility_id": tank_resp,
            "proficiency_level": "never",
        },
    ).get_json()["id"]

    resp = client.put(
        f"/api/mechanic-profiles/{profile_id}", json={"responsibility_id": dps_resp}
    )
    assert resp.status_code == 400


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
