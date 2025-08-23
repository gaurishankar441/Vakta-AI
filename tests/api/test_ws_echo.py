from fastapi.testclient import TestClient
from app.main import app

def test_ws_audio_ready():
    c = TestClient(app)
    with c.websocket_connect("/ws/audio") as ws:
        ws.send_json({"type":"start"})
        assert ws.receive_json()["type"] == "ready"
        ws.send_bytes(b"\x01"*4000)
        # we should see some flow: partial or transcript eventually
        m = ws.receive()
        assert m
        ws.send_json({"type":"stop"})
