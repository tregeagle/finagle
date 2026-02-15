from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.report import CGTOverview
from app.services import cgt_service, user_service

router = APIRouter(prefix="/users/{user_id}/reports", tags=["reports"])


@router.get("/cgt", response_model=CGTOverview)
def cgt_overview(user_id: int, db: Session = Depends(get_db)):
    if not user_service.get_user(db, user_id):
        raise HTTPException(404, "User not found")
    result = cgt_service.compute_cgt(db, user_id)
    # Strip lot matches for overview
    for fy in result.financial_years:
        fy.lot_matches = []
    return result


@router.get("/cgt/{fy}", response_model=CGTOverview)
def cgt_detail(user_id: int, fy: str, db: Session = Depends(get_db)):
    if not user_service.get_user(db, user_id):
        raise HTTPException(404, "User not found")
    result = cgt_service.compute_cgt(db, user_id, fy=fy)
    if not result.financial_years:
        raise HTTPException(404, "No data for this financial year")
    return result
