#!/usr/bin/env python3
import os, sys, json, asyncio, websockets

URL   = os.environ.get("WS_URL") or "ws://127.0.0.1:8000/ws/audio"
WAV   = sys.argv[1] if len(sys.argv) > 1 else "test_16k.wav"
TOKEN = (os.environ.get("TOKEN") or "").strip()

async def run_once(url, use_header):
    headers = {"Authorization": f"Bearer {TOKEN}"} if (use_header and TOKEN) else None
    async with websockets.connect(url, extra_headers=headers, max_size=None) as ws:
        # start
        await ws.send(json.dumps({"type":"start","sample_rate":16000,"channels":1,"format":"pcm_s16le"}))
        # audio
        with open(WAV, "rb") as f:
            pcm = f.read()
        CHUNK = 3200
        for i in range(0, len(pcm), CHUNK):
            await ws.send(pcm[i:i+CHUNK])
        # finalize
        await ws.send(b"")        # empty-binary
        await ws.send("end")      # finalize

        # read until tts_end
        while True:
            msg = await ws.recv()
            print(msg)
            if isinstance(msg, str):
                try:
                    data = json.loads(msg)
                    if data.get("type") == "tts_end":
                        break
                except Exception:
                    pass

async def main():
    # try header first if URL में ?token= नहीं है, वरना direct URL
    use_header = ("token=" not in URL) and bool(TOKEN)
    try:
        await run_once(URL, use_header)
    except websockets.exceptions.InvalidStatusCode as e:
        # HTTP 403 आदि पर तुरंत fallback: query param से
        if e.status_code == 403 or use_header:
            # sanitize token for URL
            tok = TOKEN.replace("\n","").replace("\r","")
            qurl = URL if "token=" in URL else (URL + ("&" if "?" in URL else "?") + f"token={tok}")
            await run_once(qurl, False)
        else:
            raise

if __name__ == "__main__":
    asyncio.run(main())
