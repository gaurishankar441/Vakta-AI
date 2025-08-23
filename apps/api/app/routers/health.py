from fastapi import APIRouter
from time import time
from datetime import datetime, timezone
from sqlalchemy import text
from app.db import engine
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "timestamp": time(), "version": "0.0.1"}

@router.get("/health/detailed")
def health_detailed():
    checks = {}
    # DB
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as e:
        checks["db"] = f"error:{type(e).__name__}"
    # Redis
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error:{type(e).__name__}"
    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks, "time": datetime.now(timezone.utc).isoformat()}
