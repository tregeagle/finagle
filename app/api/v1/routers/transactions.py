from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.transaction import Action
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services import transaction_service, user_service

router = APIRouter(prefix="/users/{user_id}/transactions", tags=["transactions"])


def _require_user(user_id: int, db: Session):
    if not user_service.get_user(db, user_id):
        raise HTTPException(404, "User not found")


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    user_id: int,
    ticker: str | None = Query(None),
    action: Action | None = Query(None),
    fy: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _require_user(user_id, db)
    return transaction_service.list_transactions(db, user_id, ticker, action, fy)


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(
    user_id: int, body: TransactionCreate, db: Session = Depends(get_db)
):
    _require_user(user_id, db)
    return transaction_service.create_transaction(db, user_id, body)


@router.get("/{txn_id}", response_model=TransactionRead)
def get_transaction(user_id: int, txn_id: int, db: Session = Depends(get_db)):
    _require_user(user_id, db)
    txn = transaction_service.get_transaction(db, user_id, txn_id)
    if not txn:
        raise HTTPException(404, "Transaction not found")
    return txn


@router.delete("/{txn_id}", status_code=204)
def delete_transaction(user_id: int, txn_id: int, db: Session = Depends(get_db)):
    _require_user(user_id, db)
    if not transaction_service.delete_transaction(db, user_id, txn_id):
        raise HTTPException(404, "Transaction not found")
