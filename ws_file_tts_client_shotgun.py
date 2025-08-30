#!/usr/bin/env python3
# Sends start -> bytes -> a sequence of finalize variants (+ ping + noop)
# and then listens up to WS_RECV_TIMEOUT seconds for server events.
import asyncio, json, os, sys, wave, time
import websockets  # pip install websockets

URL   = os.environ.get("WS_URL", "ws://127.0.0.1:8000/ws/audio")
CHUNK = 3200
TIMEOUT = float(os.environ.get("WS_RECV_TIMEOUT", "60"))

def read_pcm16_mono_16k(path: str) -> bytes:
    with wave.open(path, "rb") as wf:
        assert wf.getframerate()==16000 and wf.getnchannels()==1 and wf.getsampwidth()==2, "need 16kHz mono pcm_s16le"
        return wf.readframes(wf.getnframes())

async def main(path: str):
    pcm = read_pcm16_mono_16k(path)
    headers = {}
    tok = os.environ.get("WS_BEARER_TOKEN")
    if tok: headers["Authorization"] = f"Bearer {tok}"

    async with websockets.connect(URL, max_size=None, extra_headers=headers) as ws:
        print("[dbg] connect", URL)
        await ws.send(json.dumps({"type":"start","sample_rate":16000,"channels":1,"format":"pcm_s16le"}))
        for i in range(0, len(pcm), CHUNK):
            await ws.send(pcm[i:i+CHUNK])

        # try a bunch of finalize shapes spaced a bit apart
        variants = [
            {"type":"finalize"},
            {"type":"stop"},
            {"event":"finalize"},
            {"finalize": True},
            {"type":"done"},
        ]
        for v in variants:
            await ws.send(json.dumps(v))
            await asyncio.sleep(0.15)

        try:
            await ws.ping()
        except Exception:
            pass

        # also send a tiny noop text frame (this used to trigger your server)
        await ws.send(" ")

        # listen for replies up to TIMEOUT
        deadline = time.time() + TIMEOUT
        while time.time() < deadline:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=max(0.1, deadline - time.time()))
            except asyncio.TimeoutError:
                print("[i] timeout waiting for server events")
                break
            if isinstance(msg, bytes):
                print(f"[<-bin] {len(msg)} bytes")
                continue
            try:
                evt = json.loads(msg)
            except Exception:
                print("[<-text]", msg[:120].replace("\n","\\n"))
                continue
            print("[<-json]", evt)
            if evt.get("type") in ("tts_end","error","closed"):
                break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python ws_file_tts_client_shotgun.py <wav 16k mono s16le>")
        sys.exit(2)
    asyncio.run(main(sys.argv[1]))
