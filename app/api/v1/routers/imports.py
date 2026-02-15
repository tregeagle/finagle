from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.import_result import ImportResult
from app.services import import_service, user_service

router = APIRouter(tags=["import"])

TEMPLATE_PATH = Path(__file__).resolve().parents[4] / "templates" / "stock_transactions.csv"


@router.get("/import/template")
def download_template():
    return FileResponse(
        TEMPLATE_PATH,
        media_type="text/csv",
        filename="stock_transactions.csv",
    )


@router.post("/users/{user_id}/import", response_model=ImportResult)
async def import_file(user_id: int, file: UploadFile, db: Session = Depends(get_db)):
    if not user_service.get_user(db, user_id):
        raise HTTPException(404, "User not found")

    content = await file.read()
    imported, errors = import_service.parse_and_import(
        db, user_id, file.filename or "upload.csv", content
    )
    return ImportResult(imported=imported, errors=errors)
