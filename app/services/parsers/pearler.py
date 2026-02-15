import csv
import io
from datetime import date, time
from decimal import Decimal

from app.services.parsers import ParsedTransaction, register

EXPECTED_HEADERS = ["Symbol", "Exchange", "Trade Date", "Trade Type", "Quantity", "Price",
                    "Brokerage Fee"]


@register
class PearlerParser:
    @staticmethod
    def can_handle(filename: str, content: bytes) -> bool:
        if not filename.lower().endswith(".csv"):
            return False
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            return False
        reader = csv.reader(io.StringIO(text))
        try:
            header = next(reader)
        except StopIteration:
            return False
        normalised = [h.strip() for h in header[:7]]
        return normalised == EXPECTED_HEADERS

    @staticmethod
    def parse(filename: str, content: bytes) -> tuple[list[ParsedTransaction], list[str]]:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        transactions: list[ParsedTransaction] = []
        errors: list[str] = []

        for row_num, row in enumerate(reader, start=2):
            try:
                trade_date_raw = row["Trade Date"].strip()
                if "T" in trade_date_raw:
                    date_str, time_str = trade_date_raw.split("T", 1)
                else:
                    date_str = trade_date_raw
                    time_str = "00:00:00"

                txn_date = date.fromisoformat(date_str)
                txn_time = time.fromisoformat(time_str)
                qty = abs(int(float(row["Quantity"].strip())))
                price = Decimal(row["Price"].strip())
                value = price * qty
                fee = Decimal(row["Brokerage Fee"].strip())
                reference = row.get("Reference", "").strip() or None

                txn = ParsedTransaction(
                    date=txn_date,
                    time=txn_time,
                    action=row["Trade Type"].strip().lower(),
                    ticker=row["Symbol"].strip().upper(),
                    quantity=qty,
                    price=price,
                    value=value,
                    fee=fee,
                    contract_note=reference,
                )
                transactions.append(txn)
            except Exception as e:
                errors.append(f"Row {row_num}: {e}")

        return transactions, errors
