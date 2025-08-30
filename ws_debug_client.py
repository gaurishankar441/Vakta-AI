#!/usr/bin/env python3
import asyncio, json, os, sys, wave, signal, time
import websockets  # pip install websockets

URL   = os.environ.get("WS_URL", "ws://127.0.0.1:8000/ws/audio")
CHUNK = 3200
RECV_FOR = float(os.environ.get("WS_DEBUG_RECV_FOR", "15"))  # seconds to listen after finalize
NOOP_AFTER = os.environ.get("WS_NOOP_AFTER_FINALIZE", "0") == "1"  # send tiny text frame to tick server

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
        # start
        msg = {"type":"start","sample_rate":16000,"channels":1,"format":"pcm_s16le"}
        await ws.send(json.dumps(msg))
        print("[dbg] -> start", msg)

        # bytes
        sent = 0
        for i in range(0, len(pcm), CHUNK):
            chunk = pcm[i:i+CHUNK]
            await ws.send(chunk)
            sent += len(chunk)
        print("[dbg] -> bytes total", sent)

        # finalize
        await ws.send(json.dumps({"type":"finalize"}))
        print("[dbg] -> finalize")

        # optional "noop" text frame to emulate earlier 'Unknown text frame'
        if NOOP_AFTER:
            await ws.send(" ")
            print("[dbg] -> noop text (single space)")

        # read for RECV_FOR seconds (print text JSON or raw text; show binary sizes)
        deadline = time.time() + RECV_FOR
        try:
            while time.time() < deadline:
                timeout = max(0.1, deadline - time.time())
                frame = await asyncio.wait_for(ws.recv(), timeout=timeout)
                if isinstance(frame, bytes):
                    print(f"[<-bin] {len(frame)} bytes")
                else:
                    try:
                        evt = json.loads(frame)
                        print("[<-json]", evt)
                        if evt.get("type") in ("tts_end","error","closed"):
                            break
                    except Exception:
                        print("[<-text]", frame[:120].replace("\n","\\n"))
        except asyncio.TimeoutError:
            print("[dbg] recv window ended")
        except Exception as e:
            print("[dbg] recv error:", repr(e))
