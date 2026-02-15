from decimal import Decimal

import pytest


@pytest.fixture()
def user_id(client):
    r = client.post("/api/v1/users", json={"username": "investor"})
    return r.json()["id"]


def _buy(client, uid, date, ticker, qty, price, fee="9.95"):
    client.post(f"/api/v1/users/{uid}/transactions", json={
        "date": date, "time": "10:00:00", "action": "buy", "ticker": ticker,
        "quantity": qty, "price": price, "value": str(Decimal(price) * qty),
        "fee": fee,
    })


def _sell(client, uid, date, ticker, qty, price, fee="9.95"):
    client.post(f"/api/v1/users/{uid}/transactions", json={
        "date": date, "time": "10:00:00", "action": "sell", "ticker": ticker,
        "quantity": qty, "price": price, "value": str(Decimal(price) * qty),
        "fee": fee,
    })


def test_simple_gain_no_discount(client, user_id):
    """Buy and sell within 12 months — no CGT discount."""
    _buy(client, user_id, "2024-01-10", "BHP", 100, "40.00", "10.00")
    _sell(client, user_id, "2024-06-15", "BHP", 100, "50.00", "10.00")

    r = client.get(f"/api/v1/users/{user_id}/reports/cgt/2023-24")
    assert r.status_code == 200
    fy = r.json()["financial_years"][0]
    assert fy["financial_year"] == "2023-24"
    assert len(fy["lot_matches"]) == 1

    lot = fy["lot_matches"][0]
    # cost_base = 100 * (40 + 10/100) = 4010
    assert Decimal(lot["cost_base"]) == Decimal("4010.00")
    # proceeds = 100 * (50 - 10/100) = 4990
    assert Decimal(lot["proceeds"]) == Decimal("4990.00")
    assert Decimal(lot["raw_gain"]) == Decimal("980.00")
    assert lot["held_over_12_months"] is False
    assert Decimal(lot["discount"]) == Decimal("0.00")
    assert Decimal(fy["net_capital_gain"]) == Decimal("980.00")


def test_discount_gain(client, user_id):
    """Buy and sell >12 months apart — 50% CGT discount."""
    _buy(client, user_id, "2023-01-10", "BHP", 100, "40.00", "10.00")
    _sell(client, user_id, "2024-02-15", "BHP", 100, "50.00", "10.00")

    r = client.get(f"/api/v1/users/{user_id}/reports/cgt/2023-24")
    fy = r.json()["financial_years"][0]
    lot = fy["lot_matches"][0]
    assert lot["held_over_12_months"] is True
    assert Decimal(lot["discount"]) == Decimal("490.00")
    assert Decimal(lot["net_gain"]) == Decimal("490.00")
    assert Decimal(fy["net_capital_gain"]) == Decimal("490.00")


def test_fifo_partial_lot(client, user_id):
    """FIFO: sell consumes partial first lot."""
    _buy(client, user_id, "2024-01-10", "BHP", 100, "40.00", "0.00")
    _buy(client, user_id, "2024-02-10", "BHP", 100, "50.00", "0.00")
    _sell(client, user_id, "2024-03-10", "BHP", 150, "55.00", "0.00")

    r = client.get(f"/api/v1/users/{user_id}/reports/cgt/2023-24")
    fy = r.json()["financial_years"][0]
    assert len(fy["lot_matches"]) == 2

    # First lot: 100 @ 40, sold 55 => gain 1500
    assert fy["lot_matches"][0]["quantity"] == 100
    assert Decimal(fy["lot_matches"][0]["raw_gain"]) == Decimal("1500.00")

    # Second lot: 50 @ 50, sold 55 => gain 250
    assert fy["lot_matches"][1]["quantity"] == 50
    assert Decimal(fy["lot_matches"][1]["raw_gain"]) == Decimal("250.00")


def test_loss_offsets_gain(client, user_id):
    """Losses offset gains per ATO 18A."""
    _buy(client, user_id, "2024-01-10", "AAA", 100, "50.00", "0.00")
    _sell(client, user_id, "2024-03-10", "AAA", 100, "30.00", "0.00")  # loss of 2000

    _buy(client, user_id, "2024-01-10", "BBB", 100, "20.00", "0.00")
    _sell(client, user_id, "2024-03-10", "BBB", 100, "40.00", "0.00")  # gain of 2000

    r = client.get(f"/api/v1/users/{user_id}/reports/cgt/2023-24")
    fy = r.json()["financial_years"][0]
    assert Decimal(fy["net_capital_gain"]) == Decimal("0.00")


def test_overview_has_no_lot_matches(client, user_id):
    """CGT overview strips lot matches."""
    _buy(client, user_id, "2024-01-10", "BHP", 100, "40.00", "0.00")
    _sell(client, user_id, "2024-06-10", "BHP", 100, "50.00", "0.00")

    r = client.get(f"/api/v1/users/{user_id}/reports/cgt")
    for fy in r.json()["financial_years"]:
        assert fy["lot_matches"] == []


def test_cgt_no_data(client, user_id):
    r = client.get(f"/api/v1/users/{user_id}/reports/cgt/2099-00")
    assert r.status_code == 404
