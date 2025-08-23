from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import WebSocketRoute

# Routers (relative imports)
from app.routers import health, auth, chat, ws_audio, metrics
from app.db import init_db

app = FastAPI(title="Vakta AI API", version="0.1.0")

# === Routers ===
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])
app.include_router(auth.router,   prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router)
app.include_router(ws_audio.router, prefix="/ws", tags=["websocket"])

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Startup DB init ===
@app.on_event("startup")
def _startup():
    init_db()

# === Raw WS handler (echo test) ===
@app.websocket("/ws/audio")
async def ws_audio_ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive()
            if "text" in msg:
                await ws.send_json({"type": "ready"})
            elif "bytes" in msg:
                await ws.send_bytes(msg["bytes"])  # echo
    except WebSocketDisconnect:
        pass

# === VAKTA WS ROUTE PRUNE ===
try:
    pruned, kept = [], []
    for r in list(app.router.routes):
        if isinstance(r, WebSocketRoute):
            mod = getattr(r.endpoint, "__module__", "")
            path = r.path
            drop = False
            if path in ("/ws/api/ws/audio", "/ws/ws/audio"):
                drop = True
            if path == "/ws/audio" and mod != "app.routers.ws_audio":
                drop = True
            if path == "/api/ws/audio" and mod != "app.routers.ws_audio":
                drop = True
            if drop:
                pruned.append((path, mod))
                continue
        kept.append(r)
    app.router.routes = kept
    if pruned:
        print("[boot] pruned WS routes:", pruned)
except Exception as e:
    print("[boot] WS prune skipped:", e)
# === /VAKTA WS ROUTE PRUNE ===
