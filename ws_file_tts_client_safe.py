#!/usr/bin/env python3
# Minimal, robust WS client: start -> binary bytes -> finalize -> read until tts_end (with timeout)
# pip install websockets
import asyncio, json, os, sys, wave, signal
import websockets  # type: ignore

URL   = os.environ.get("WS_URL", "ws://127.0.0.1:8000/ws/audio")
CHUNK = 3200   # 100ms @ 16k mono s16le
TIMEOUT_SEC = float(os.environ.get("WS_RECV_TIMEOUT", "20"))

def read_pcm16_mono_16k(path: str) -> bytes:
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        ch = wf.getnchannels()
        sw = wf.getsampwidth()
        assert sr == 16000 and ch == 1 and sw == 2, "need 16kHz mono pcm_s16le WAV"
        return wf.readframes(wf.getnframes())

async def main(path: str):
    pcm = read_pcm16_mono_16k(path)
    extra_headers = {}
    token = os.environ.get("WS_BEARER_TOKEN")
    if token:
        extra_headers["Authorization"] = f"Bearer {token}"

    finalized = False

    async with websockets.connect(URL, max_size=None, extra_headers=extra_headers) as ws:
        # graceful Ctrl-C: still try to finalize
        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop_event.set)
            except NotImplementedError:
                pass

        # 1) start
        await ws.send(json.dumps({"type":"start","sample_rate":16000,"channels":1,"format":"pcm_s16le"}))

        # 2) audio bytes
        for i in range(0, len(pcm), CHUNK):
            if stop_event.is_set():
                break
            await ws.send(pcm[i:i+CHUNK])

        # 3) finalize (even if interrupted)
        try:
            await ws.send(json.dumps({"type":"finalize"}))
            finalized = True
        except Exception:
            pass

        # 4) receive until tts_end (or timeout)
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=TIMEOUT_SEC)
                try:
                    evt = json.loads(msg)
                except Exception:
                    continue  # ignore non-JSON frames
                if evt.get("type") == "warn":
                    continue  # mute server warn frames
                print("[<-]", json.dumps(evt))
                if evt.get("type") in ("tts_end","error","closed"):
                    break
        except asyncio.TimeoutError:
            print("[i] recv timeout; closing")
        except asyncio.CancelledError:
            print("[i] cancelled; closing")
        finally:
            try:
                if not finalized:
                    await ws.send(json.dumps({"type":"finalize"}))
            except Exception:
                pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python ws_file_tts_client_safe.py <wav path 16k mono s16le>")
        sys.exit(2)
    asyncio.run(main(sys.argv[1]))
