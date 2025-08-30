import os
from fastapi import WebSocket, status
from fastapi.exceptions import HTTPException
from jose import jwt, JWTError  # use python-jose (usually shipped with FastAPI stacks)

SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY") or "changeme"
ALGO = os.getenv("JWT_ALGORITHM", "HS256")

def _bearer(h: str | None):
    if not h:
        return None
    parts = h.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None

async def get_current_user_ws(websocket: WebSocket):
    # Prefer Authorization header injected by middleware; fallback to ?token=
    token = _bearer(websocket.headers.get("authorization")) \
            or websocket.query_params.get("token") \
            or websocket.query_params.get("Token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail="Missing token")

    try:
        claims = jwt.decode(token, SECRET, algorithms=[ALGO], options={"verify_aud": False})
        return claims
    except JWTError as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail=f"Token invalid: {e}")
