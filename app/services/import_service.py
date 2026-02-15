from sqlalchemy.orm import Session

from app.models.transaction import Action, StockTransaction

# Import parsers to trigger registration
from app.services.parsers import PARSERS  # noqa: F401
import app.services.parsers.native  # noqa: F401
import app.services.parsers.sharesight  # noqa: F401
import app.services.parsers.pearler  # noqa: F401


def parse_and_import(
    db: Session, user_id: int, filename: str, content: bytes
) -> tuple[int, list[str]]:
    for parser_cls in PARSERS:
        if parser_cls.can_handle(filename, content):
            transactions, errors = parser_cls.parse(filename, content)
            if errors:
                return 0, errors

            for txn in transactions:
                db.add(
                    StockTransaction(
                        user_id=user_id,
                        date=txn.date,
                        time=txn.time,
                        action=Action(txn.action),
                        ticker=txn.ticker,
                        quantity=txn.quantity,
                        price=txn.price,
                        value=txn.value,
                        fee=txn.fee,
                        contract_note=txn.contract_note,
                    )
                )

            if transactions:
                db.commit()
            return len(transactions), errors

    return 0, ["Unrecognised file format"]
