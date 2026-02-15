import io
from datetime import date, time
from decimal import Decimal

from python_calamine import CalamineWorkbook

from app.services.parsers import ParsedTransaction, register

EXPECTED_HEADERS = ["Code", "Market Code", "Name", "Date", "Type", "Qty"]


@register
class SharesightParser:
    @staticmethod
    def can_handle(filename: str, content: bytes) -> bool:
        if not filename.lower().endswith(".xlsx"):
            return False
        try:
            wb = CalamineWorkbook.from_filelike(io.BytesIO(content))
            sheet = wb.get_sheet_by_index(0)
            rows = sheet.to_python()
            if not rows:
                return False
            # Check title row or header row
            if "All Trades Report" in str(rows[0][0]):
                return True
            if len(rows) > 2:
                header = [str(c).strip() for c in rows[2][:6]]
                return header == EXPECTED_HEADERS
        except Exception:
            return False
        return False

    @staticmethod
    def parse(filename: str, content: bytes) -> tuple[list[ParsedTransaction], list[str]]:
        wb = CalamineWorkbook.from_filelike(io.BytesIO(content))
        sheet = wb.get_sheet_by_index(0)
        rows = sheet.to_python()

        # Row 0 = title, row 1 = blank, row 2 = headers, data starts at row 3
        if len(rows) < 4:
            return [], ["Sharesight file has no data rows"]

        header = [str(c).strip() for c in rows[2]]
        col = {name: i for i, name in enumerate(header)}

        transactions: list[ParsedTransaction] = []
        errors: list[str] = []

        for row_idx, row in enumerate(rows[3:], start=4):
            # Skip the "Total" row at the end
            if str(row[0]).strip().lower() == "total":
                continue

            try:
                code = str(row[col["Code"]]).strip()
                type_val = str(row[col["Type"]]).strip().lower()
                qty = abs(int(float(row[col["Qty"]])))
                price = Decimal(str(row[col["Price"]]))
                value = abs(Decimal(str(row[col["Value"]])))
                brokerage = Decimal(str(row[col["Brokerage"]]))

                date_val = row[col["Date"]]
                if isinstance(date_val, str):
                    txn_date = date.fromisoformat(date_val)
                else:
                    txn_date = date_val  # calamine returns date objects

                txn = ParsedTransaction(
                    date=txn_date,
                    time=time(0, 0, 0),
                    action=type_val,
                    ticker=code.upper(),
                    quantity=qty,
                    price=price,
                    value=value,
                    fee=brokerage,
                )
                transactions.append(txn)
            except Exception as e:
                errors.append(f"Row {row_idx}: {e}")

        return transactions, errors
