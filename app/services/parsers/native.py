import csv
import io
from datetime import date, time
from decimal import Decimal, InvalidOperation

from app.services.parsers import ParsedTransaction, register

EXPECTED_HEADERS = [
    "date", "time", "action", "ticker", "quantity", "price", "value", "fee", "contract_note"
]


@register
class NativeParser:
    @staticmethod
    def can_handle(filename: str, content: bytes) -> bool:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            return False
        reader = csv.reader(io.StringIO(text))
        try:
            header = next(reader)
        except StopIteration:
            return False
        normalised = [h.strip().lower() for h in header]
        required = {"date", "time", "action", "ticker", "quantity", "price", "value", "fee"}
        return required <= set(normalised)

    @staticmethod
    def parse(filename: str, content: bytes) -> tuple[list[ParsedTransaction], list[str]]:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames is None:
            return [], ["Empty or invalid CSV file"]

        normalised = [h.strip().lower() for h in reader.fieldnames]
        missing = set(EXPECTED_HEADERS) - {"contract_note"} - set(normalised)
        if missing:
            return [], [f"Missing required columns: {', '.join(sorted(missing))}"]

        transactions: list[ParsedTransaction] = []
        errors: list[str] = []
        for row_num, row in enumerate(reader, start=2):
            row = {k.strip().lower(): v.strip() for k, v in row.items()}
            row_errors = _validate_row(row, row_num)
            if row_errors:
                errors.extend(row_errors)
                continue

            txn = ParsedTransaction(
                date=date.fromisoformat(row["date"]),
                time=time.fromisoformat(row["time"]),
                action=row["action"].lower(),
                ticker=row["ticker"].upper(),
                quantity=int(row["quantity"]),
                price=Decimal(row["price"]),
                value=Decimal(row["value"]),
                fee=Decimal(row["fee"]),
                contract_note=row.get("contract_note") or None,
            )
            transactions.append(txn)

        return transactions, errors


def _validate_row(row: dict, row_num: int) -> list[str]:
    errors: list[str] = []
    prefix = f"Row {row_num}"

    try:
        date.fromisoformat(row.get("date", ""))
    except ValueError:
        errors.append(f"{prefix}: invalid date '{row.get('date', '')}'")

    try:
        time.fromisoformat(row.get("time", ""))
    except ValueError:
        errors.append(f"{prefix}: invalid time '{row.get('time', '')}'")

    action_val = row.get("action", "").lower()
    if action_val not in ("buy", "sell"):
        errors.append(f"{prefix}: action must be 'buy' or 'sell', got '{row.get('action', '')}'")

    if not row.get("ticker", "").strip():
        errors.append(f"{prefix}: ticker is required")

    try:
        q = int(row.get("quantity", ""))
        if q <= 0:
            errors.append(f"{prefix}: quantity must be positive")
    except ValueError:
        errors.append(f"{prefix}: invalid quantity '{row.get('quantity', '')}'")

    for field in ("price", "value", "fee"):
        try:
            Decimal(row.get(field, ""))
        except InvalidOperation:
            errors.append(f"{prefix}: invalid {field} '{row.get(field, '')}'")

    return errors
