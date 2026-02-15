import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.services import user_service, transaction_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    return user_service.get_or_create_user(db, body.username)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if not user_service.delete_user(db, user_id):
        raise HTTPException(404, "User not found")


@router.get("/{user_id}/export")
def export_user_data(
    user_id: int,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    txns = transaction_service.list_transactions(db, user_id)

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "date", "time", "action", "ticker", "quantity",
            "price", "value", "fee", "contract_note",
        ])
        for t in txns:
            writer.writerow([
                t.date.isoformat(), t.time.isoformat(), t.action.value, t.ticker,
                t.quantity, str(t.price), str(t.value), str(t.fee), t.contract_note or "",
            ])
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={user.username}_export.csv"},
        )

    data = {
        "user": {"id": user.id, "username": user.username, "created_at": user.created_at.isoformat()},
        "transactions": [
            {
                "id": t.id, "date": t.date.isoformat(), "time": t.time.isoformat(),
                "action": t.action.value, "ticker": t.ticker, "quantity": t.quantity,
                "price": str(t.price), "value": str(t.value), "fee": str(t.fee),
                "contract_note": t.contract_note,
            }
            for t in txns
        ],
    }
    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={user.username}_export.json"},
    )
