def test_create_user(client):
    r = client.post("/api/v1/users", json={"username": "alice"})
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert "id" in data


def test_create_user_idempotent(client):
    r1 = client.post("/api/v1/users", json={"username": "alice"})
    r2 = client.post("/api/v1/users", json={"username": "alice"})
    assert r1.json()["id"] == r2.json()["id"]


def test_get_user(client):
    r = client.post("/api/v1/users", json={"username": "alice"})
    uid = r.json()["id"]
    r = client.get(f"/api/v1/users/{uid}")
    assert r.status_code == 200
    assert r.json()["username"] == "alice"


def test_get_user_not_found(client):
    assert client.get("/api/v1/users/999").status_code == 404


def test_delete_user(client):
    r = client.post("/api/v1/users", json={"username": "alice"})
    uid = r.json()["id"]
    assert client.delete(f"/api/v1/users/{uid}").status_code == 204
    assert client.get(f"/api/v1/users/{uid}").status_code == 404


def test_export_json(client):
    r = client.post("/api/v1/users", json={"username": "alice"})
    uid = r.json()["id"]
    r = client.get(f"/api/v1/users/{uid}/export?format=json")
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["username"] == "alice"
    assert data["transactions"] == []


def test_export_csv(client):
    r = client.post("/api/v1/users", json={"username": "alice"})
    uid = r.json()["id"]
    r = client.get(f"/api/v1/users/{uid}/export?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
