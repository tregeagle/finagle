from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel

from app.models.transaction import Action


class TransactionCreate(BaseModel):
    date: date
    time: time
    action: Action
    ticker: str
    quantity: int
    price: Decimal
    value: Decimal
    fee: Decimal
    contract_note: str | None = None


class TransactionRead(TransactionCreate):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
