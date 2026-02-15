import pytest


@pytest.fixture()
def user_id(client):
    r = client.post("/api/v1/users", json={"username": "trader"})
    return r.json()["id"]


TXN = {
    "date": "2024-01-15",
    "time": "10:30:00",
    "action": "buy",
    "ticker": "BHP",
    "quantity": 100,
    "price": "45.50",
    "value": "4550.00",
    "fee": "9.95",
}


def test_create_transaction(client, user_id):
    r = client.post(f"/api/v1/users/{user_id}/transactions", json=TXN)
    assert r.status_code == 201
    data = r.json()
    assert data["ticker"] == "BHP"
    assert data["quantity"] == 100


def test_list_transactions(client, user_id):
    client.post(f"/api/v1/users/{user_id}/transactions", json=TXN)
    r = client.get(f"/api/v1/users/{user_id}/transactions")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_list_filter_ticker(client, user_id):
    client.post(f"/api/v1/users/{user_id}/transactions", json=TXN)
    r = client.get(f"/api/v1/users/{user_id}/transactions?ticker=BHP")
    assert len(r.json()) == 1
    r = client.get(f"/api/v1/users/{user_id}/transactions?ticker=CBA")
    assert len(r.json()) == 0


def test_get_transaction(client, user_id):
    r = client.post(f"/api/v1/users/{user_id}/transactions", json=TXN)
    txn_id = r.json()["id"]
    r = client.get(f"/api/v1/users/{user_id}/transactions/{txn_id}")
    assert r.status_code == 200
    assert r.json()["id"] == txn_id


def test_delete_transaction(client, user_id):
    r = client.post(f"/api/v1/users/{user_id}/transactions", json=TXN)
    txn_id = r.json()["id"]
    assert client.delete(f"/api/v1/users/{user_id}/transactions/{txn_id}").status_code == 204
    assert client.get(f"/api/v1/users/{user_id}/transactions/{txn_id}").status_code == 404


def test_transaction_user_not_found(client):
    r = client.get("/api/v1/users/999/transactions")
    assert r.status_code == 404
