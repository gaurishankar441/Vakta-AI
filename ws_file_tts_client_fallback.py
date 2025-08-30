#!/usr/bin/env python3
# WS client with finalize fallback ("finalize" -> wait -> if no event, send "stop")
import asyncio, json, os, sys, wave, signal, time
import websockets  # type: ignore

URL   = os.environ.get("WS_URL", "ws://127.0.0.1:8000/ws/audio")
CHUNK = 3200
RECV_TIMEOUT = float(os.environ.get("WS_RECV_TIMEOUT", "30"))
HANDSHAKE_WAIT = float(os.environ.get("WS_HANDSHAKE_WAIT", "1.2"))  # wait for first event after finalize

def read_pcm16_mono_16k(path: str) -> bytes:
    with wave.open(path, "rb") as wf:
        assert wf.getframerate()==16000 and wf.getnchannels()==1 and wf.getsampwidth()==2, "need 16kHz mono pcm_s16le"
        return wf.readframes(wf.getnframes())

async def recv_until(ws, deadline: float):
    while True:
        timeout = max(0.1, deadline - time.time())
        if timeout <= 0: raise asyncio.TimeoutError
        msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
        try:
            evt = json.loads(msg)
        except Exception:
            continue
        if evt.get("type") == "warn":  # mute warns
            continue
        print("[<-]", json.dumps(evt))
        if evt.get("type") in ("tts_end","error","closed"):
            return True
        # keep waiting for tts_end
        # some servers send 'finalizing' first, then transcript/assistant/tts/tts_end

async def main(path: str):
    pcm = read_pcm16_mono_16k(path)
    headers = {}
    tok = os.environ.get("WS_BEARER_TOKEN")
    if tok: headers["Authorization"] = f"Bearer {tok}"

    async with websockets.connect(URL, max_size=None, extra_headers=headers) as ws:
        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try: loop.add_signal_handler(sig, stop_event.set)
            except NotImplementedError: pass

        # 1) start
        await ws.send(json.dumps({"type":"start","sample_rate":16000,"channels":1,"format":"pcm_s16le"}))

        # 2) audio
        for i in range(0, len(pcm), CHUNK):
            if stop_event.is_set(): break
            await ws.send(pcm[i:i+CHUNK])

        # 3) finalize (primary)
        await ws.send(json.dumps({"type":"finalize"}))

        # 3a) give a moment to see first event (like "finalizing")
        first_deadline = time.time() + HANDSHAKE_WAIT
        try:
            await recv_until(ws, first_deadline)  # returns only if it hits tts_end quickly
            return
        except asyncio.TimeoutError:
            # no event → try fallback verb "stop"
            try:
                await ws.send(json.dumps({"type":"stop"}))
            except Exception:
                pass

        # 4) now wait fully for tts_end
        full_deadline = time.time() + RECV_TIMEOUT
        try:
            await recv_until(ws, full_deadline)
        except asyncio.TimeoutError:
            print("[i] recv timeout after finalize/stop; closing")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python ws_file_tts_client_fallback.py <wav 16k mono s16le>")
        sys.exit(2)
    asyncio.run(main(sys.argv[1]))
