#!/usr/bin/env python3
import asyncio, websockets, sys, json, os

CHUNK = 3200

async def main(path):
    url = os.environ.get("WS_URL")
    if not url:
        print("❌ WS_URL env var missing")
        sys.exit(1)

    async with websockets.connect(url, max_size=None) as ws:
        # Start frame
        await ws.send(json.dumps({
            "type": "start",
            "sample_rate": 16000,
            "channels": 1,
            "format": "pcm_s16le"
        }))
        print("[->json] start")

        # Send audio in chunks
        pcm = open(path, "rb").read()
        for i in range(0, len(pcm), CHUNK):
            await ws.send(pcm[i:i+CHUNK])
            await asyncio.sleep(0.01)
        print(f"[->] sent {len(pcm)} bytes")

        # End of audio
        await ws.send(b"")
        print("[->] empty-binary")

        # Finalize
        await ws.send(json.dumps({"type": "finalize"}))
        print("[->json] finalize")

        # Listen for responses
        try:
            while True:
                msg = await ws.recv()
                try:
                    data = json.loads(msg)
                    print("[<-]", data)
                except Exception:
                    print("[<-text]", msg)
        except websockets.exceptions.ConnectionClosedOK:
            print("✅ WS closed cleanly")
        except websockets.exceptions.ConnectionClosedError as e:
            print("❌ WS closed with error:", e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ws_file_tts_client_stable.py <wavfile>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
