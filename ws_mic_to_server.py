import os, sys, json, asyncio, pathlib, tempfile, wave
import numpy as np, sounddevice as sd, websockets

SR, CH, SW = 16000, 1, 2  # 16k, mono, int16

def ws_url():
    u = os.environ.get("WS_URL")
    if u and u.strip(): return u.strip()
    tok = pathlib.Path(".auth_token").read_text().strip()
    return f"ws://localhost:8000/ws/audio?token={tok}"

def record_seconds(sec: int, device=None) -> np.ndarray:
    frames = int(sec * SR)
    rec = sd.rec(frames, samplerate=SR, channels=CH, dtype="int16", blocking=True, device=device)
    sd.wait()
    return rec.reshape(-1)

async def main(dur_sec: int, device=None):
    URL = ws_url()
    print(f"[cfg] url={URL} auth=True sr={SR}ch={CH} dtype=int16 dev={device}")
    audio = record_seconds(dur_sec, device=device)

    buf = bytearray()
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps({"type":"start","sr":SR,"ch":CH,"fmt":"pcm_s16le","tts_lang":"en"}))
        # ~100ms chunks
        step = SR//10
        for i in range(0, len(audio), step):
            await ws.send(audio[i:i+step].tobytes())
        # close stream (server dono accept karta hai)
        await ws.send(json.dumps({"type":"end"}))
        await ws.send("end")
        # drain replies (and collect any audio bytes back)
        try:
            while True:
                m = await asyncio.wait_for(ws.recv(), timeout=5)
                if isinstance(m,(bytes,bytearray)): buf.extend(m)
                else:
                    print("[<-]", m)
                    if '"tts_end"' in m: break
        except asyncio.TimeoutError:
            print("[note] done")

    if buf:
        p = pathlib.Path(tempfile.mkstemp(suffix=".wav")[1])
        with wave.open(str(p), "wb") as w:
            w.setnchannels(CH); w.setsampwidth(SW); w.setframerate(SR)
            w.writeframes(buf)
        print(f"[save] wav -> {p} ({len(buf)} bytes)")
        os.system(f"afplay '{p}'")

if __name__ == "__main__":
    dur = int(sys.argv[1]) if len(sys.argv)>1 else 3
    dev = os.environ.get("SD_INPUT_DEVICE")
    asyncio.run(main(dur, device=int(dev) if dev else None))
