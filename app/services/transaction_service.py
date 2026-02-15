from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Action, StockTransaction
from app.schemas.transaction import TransactionCreate


def list_transactions(
    db: Session,
    user_id: int,
    ticker: str | None = None,
    action: Action | None = None,
    fy: str | None = None,
) -> list[StockTransaction]:
    stmt = select(StockTransaction).where(StockTransaction.user_id == user_id)
    if ticker:
        stmt = stmt.where(StockTransaction.ticker == ticker.upper())
    if action:
        stmt = stmt.where(StockTransaction.action == action)
    if fy:
        start_year = int(fy.split("-")[0])
        from datetime import date

        fy_start = date(start_year, 7, 1)
        fy_end = date(start_year + 1, 6, 30)
        stmt = stmt.where(StockTransaction.date >= fy_start, StockTransaction.date <= fy_end)
    stmt = stmt.order_by(StockTransaction.date, StockTransaction.time)
    return list(db.scalars(stmt).all())


def create_transaction(
    db: Session, user_id: int, data: TransactionCreate
) -> StockTransaction:
    txn = StockTransaction(user_id=user_id, **data.model_dump())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def get_transaction(db: Session, user_id: int, txn_id: int) -> StockTransaction | None:
    stmt = select(StockTransaction).where(
        StockTransaction.id == txn_id, StockTransaction.user_id == user_id
    )
    return db.scalars(stmt).first()


def delete_transaction(db: Session, user_id: int, txn_id: int) -> bool:
    txn = get_transaction(db, user_id, txn_id)
    if not txn:
        return False
    db.delete(txn)
    db.commit()
    return True
