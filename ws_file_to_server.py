import os, sys, json, asyncio, wave
import websockets

WS_URL = os.getenv("WS_URL", "ws://localhost:8000/ws/audio")

async def run(path: str):
    # Open WAV
    with wave.open(path, "rb") as w:
        nch, sampwidth, fr, nframes = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        print(json.dumps({"status":"ok","wav":{"channels":nch,"sampwidth":sampwidth,"rate":fr,"frames":nframes}}), flush=True)

        # Connect
        async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
            # reader task (print every server message)
            async def reader():
                async for msg in ws:
                    print("↩︎", msg, flush=True)
            reader_task = asyncio.create_task(reader())

            # Send a "start" control (server will just echo it)
            start = {"type":"start","sample_rate":fr,"channels":nch,"format":"pcm_s16le"}
            await ws.send(json.dumps(start))

            # Send audio bytes in chunks
            CHUNK = 3200  # ~100ms @16k mono 16bit
            sent = 0
            while True:
                data = w.readframes(CHUNK // (sampwidth or 2))
                if not data:
                    break
                await ws.send(data)   # bytes => binary frame
                sent += len(data)

            # Send an "end" control (server will just echo it)
            await ws.send("end")

            # small grace to receive last acks
            await asyncio.sleep(0.5)
            reader_task.cancel()
            try:
                await reader_task
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ws_file_to_server.py <path.wav>", file=sys.stderr)
        sys.exit(2)
    asyncio.run(run(sys.argv[1]))
