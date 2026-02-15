import io

import pytest
from openpyxl import Workbook


@pytest.fixture()
def user_id(client):
    r = client.post("/api/v1/users", json={"username": "importer"})
    return r.json()["id"]


CSV_GOOD = """\
date,time,action,ticker,quantity,price,value,fee,contract_note
2023-08-15,10:30:00,buy,BHP,100,45.50,4550.00,9.95,CN001
2024-09-20,14:15:00,sell,BHP,50,52.00,2600.00,9.95,
"""

CSV_BAD_ROW = """\
date,time,action,ticker,quantity,price,value,fee,contract_note
2023-08-15,10:30:00,buy,BHP,abc,45.50,4550.00,9.95,
"""

CSV_MISSING_COL = """\
date,time,action,ticker,quantity,price,value
2023-08-15,10:30:00,buy,BHP,100,45.50,4550.00
"""

PEARLER_CSV = """\
Symbol,Exchange,Trade Date,Trade Type,Quantity,Price,Brokerage Fee,Brokerage Fee Currency,Exchange Rate,Reference
VAS,ASX,2021-03-11T10:30:14,Buy,11,86.64,9.50,AUD,,AU2464
GOLD,ASX,2023-04-21T10:30:39,Sell,104,27.53,10.83,AUD,,AU307867
"""


def _make_sharesight_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["All Trades Report for Test", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    ws.append([""] * 14)
    ws.append([
        "Code", "Market Code", "Name", "Date", "Type", "Qty",
        "Price", "Instrument Currency", "Cost Base Per Share (aud)",
        "Brokerage", "Brokerage Currency", "Exch. Rate", "Value", " ",
    ])
    ws.append(["VAS", "ASX", "Vanguard", "2021-03-11", "Buy", 11, 86.64,
               "AUD", "", 9.5, "AUD", 1.0, 962.54, ""])
    ws.append(["BHP", "ASX", "BHP Group", "2024-01-15", "Sell", 50, 48.00,
               "AUD", "", 6.33, "AUD", 1.0, 2400.00, ""])
    ws.append(["Total", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_download_template(client):
    r = client.get("/api/v1/import/template")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "date" in r.text


def test_import_csv(client, user_id):
    r = client.post(
        f"/api/v1/users/{user_id}/import",
        files={"file": ("txns.csv", CSV_GOOD, "text/csv")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["imported"] == 2
    assert data["errors"] == []

    txns = client.get(f"/api/v1/users/{user_id}/transactions").json()
    assert len(txns) == 2


def test_import_csv_bad_row(client, user_id):
    r = client.post(
        f"/api/v1/users/{user_id}/import",
        files={"file": ("txns.csv", CSV_BAD_ROW, "text/csv")},
    )
    data = r.json()
    assert data["imported"] == 0
    assert len(data["errors"]) > 0


def test_import_csv_missing_column(client, user_id):
    r = client.post(
        f"/api/v1/users/{user_id}/import",
        files={"file": ("txns.csv", CSV_MISSING_COL, "text/csv")},
    )
    data = r.json()
    assert data["imported"] == 0
    assert len(data["errors"]) > 0


def test_import_sharesight_xlsx(client, user_id):
    xlsx_bytes = _make_sharesight_xlsx()
    r = client.post(
        f"/api/v1/users/{user_id}/import",
        files={"file": ("AllTradesReport.xlsx", xlsx_bytes,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["imported"] == 2
    assert data["errors"] == []

    txns = client.get(f"/api/v1/users/{user_id}/transactions").json()
    tickers = {t["ticker"] for t in txns}
    assert tickers == {"VAS", "BHP"}


def test_import_pearler_csv(client, user_id):
    r = client.post(
        f"/api/v1/users/{user_id}/import",
        files={"file": ("order-statement.csv", PEARLER_CSV, "text/csv")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["imported"] == 2
    assert data["errors"] == []

    txns = client.get(f"/api/v1/users/{user_id}/transactions").json()
    assert len(txns) == 2
    vas = next(t for t in txns if t["ticker"] == "VAS")
    assert vas["action"] == "buy"
    assert vas["contract_note"] == "AU2464"
    gold = next(t for t in txns if t["ticker"] == "GOLD")
    assert gold["action"] == "sell"


def test_import_unrecognised_format(client, user_id):
    r = client.post(
        f"/api/v1/users/{user_id}/import",
        files={"file": ("data.json", b'{"foo": "bar"}', "application/json")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["imported"] == 0
    assert any("Unrecognised" in e for e in data["errors"])
