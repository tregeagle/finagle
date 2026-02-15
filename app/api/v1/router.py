from fastapi import APIRouter, Depends

from app.api.v1.routers import imports, reports, transactions, users
from app.core.security import require_api_key

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])
router.include_router(users.router)
router.include_router(transactions.router)
router.include_router(imports.router)
router.include_router(reports.router)
