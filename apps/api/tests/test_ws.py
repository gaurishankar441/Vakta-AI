from fastapi.testclient import TestClient
from app.main import app

def test_ws_echo():
    c = TestClient(app)
    with c.websocket_connect("/ws/audio") as ws:
        ws.send_text("start")
        assert ws.receive_json()["type"] == "ready"
        ws.send_bytes(b"\x00"*32)
        assert isinstance(ws.receive_bytes(), (bytes, bytearray))
