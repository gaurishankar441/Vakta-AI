import time
from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.get("/echo")
async def http_echo(message:str="Hello"):
    return {"echo":message,"ts":time.time(),"svc":"vakta-api"}

@router.websocket("/ws/echo")
async def ws_echo(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"type":"ready","ts":time.time()})
    try:
        while True:
            msg = await ws.receive()
            if "text" in msg and msg["text"] is not None:
                await ws.send_json({"type":"text", "echo":msg["text"], "ts":time.time()})
            elif "bytes" in msg and msg["bytes"] is not None:
                b = msg["bytes"]
                await ws.send_json({"type":"bytes", "len":len(b), "ts":time.time()})
                await ws.send_bytes(b)
    except Exception:
        await ws.close()
