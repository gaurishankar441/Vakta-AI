import asyncio
import websockets
import os

TOKEN = os.getenv("TOKEN", "<paste-your-jwt-here>")
WS_URL = "ws://localhost:8000/ws/audio"

async def main():
    try:
        async with websockets.connect(
            WS_URL,
            additional_headers={"Authorization": f"Bearer {TOKEN}"}
        ) as ws:
            print("✅ Connected with JWT!")

            await ws.send("ping")
            reply = await ws.recv()
            print("🔊 Server reply:", reply)

    except Exception as e:
        print("❌ Connection failed:", e)

asyncio.run(main())
