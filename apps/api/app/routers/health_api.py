from fastapi import APIRouter
from . import health

# expose health endpoints again under /api/*
router = APIRouter(prefix="/api")
router.include_router(health.router)
