from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
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
@limiter.limit("10/minute")
async def import_file(
    request: Request, user_id: int, file: UploadFile, db: Session = Depends(get_db)
):
    if not user_service.get_user(db, user_id):
        raise HTTPException(404, "User not found")

    content = await file.read()

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb}MB limit")

    imported, errors = import_service.parse_and_import(
        db, user_id, file.filename or "upload.csv", content
    )
    return ImportResult(imported=imported, errors=errors)
