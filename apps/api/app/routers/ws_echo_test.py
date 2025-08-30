from fastapi import APIRouter, WebSocket
router = APIRouter()

@router.websocket("/ws/echo-test")
async def ws_echo_test(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_text()
        await ws.send_text(f"echo:{msg}")
