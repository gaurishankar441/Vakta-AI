from fastapi import APIRouter, WebSocket, Depends, HTTPException
import os, jwt

router = APIRouter()

# --- Auth helper: header Bearer OR ?token ---
async def _ws_auth(websocket: WebSocket):
    h = websocket.headers.get("authorization") or websocket.headers.get("Authorization")
    token = None
    if h and h.lower().startswith("bearer "):
        token = h.split(" ", 1)[1].strip()
    if not token:
        token = websocket.query_params.get("token")
    if not token:
        raise HTTPException(status_code=403, detail="Missing token")

    try:
        payload = jwt.decode(token, os.environ.get("JWT_SECRET","dev-secret-change-me"), algorithms=["HS256"])
        # optional: attach identity on scope if you want
        websocket.scope["user"] = payload
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expired")
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Token invalid: {e}")

# --- One handler, two paths, deps ONLY via decorator (no signature Depends) ---
@router.websocket("/audio",    dependencies=[Depends(_ws_auth)])
@router.websocket("/ws/audio", dependencies=[Depends(_ws_auth)])
async def ws_audio(websocket: WebSocket):
    # If auth passed, we get here
    await websocket.accept()
    await websocket.send_json({"type":"ready"})
    # simple echo to prove it works
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"type":"echo","text":msg})
    except Exception:
        # client closed
        await websocket.close()
