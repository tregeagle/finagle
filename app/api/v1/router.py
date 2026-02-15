from fastapi import APIRouter

from app.api.v1.routers import imports, reports, transactions, users

router = APIRouter(prefix="/api/v1")
router.include_router(users.router)
router.include_router(transactions.router)
router.include_router(imports.router)
router.include_router(reports.router)
