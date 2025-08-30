from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}

@router.get("/detailed")
async def health_detailed():
    # Normally you'd ping DB/Redis here
    return {
        "status": "ok",
        "services": {"db": "up", "redis": "up"},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
