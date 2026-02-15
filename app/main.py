import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router

app = FastAPI(title="Finagle", version="0.1.0", description="Personal finance & CGT tracker")

cors_origins = os.environ.get("FINAGLE_CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)
