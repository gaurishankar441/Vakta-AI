import asyncio
import websockets
import os

# Apna JWT token paste karo ya env se lo
TOKEN = os.getenv("TOKEN", "<paste-your-jwt-here>")
WS_URL = "ws://localhost:8000/ws/audio"

async def main():
    try:
        async with websockets.connect(
            WS_URL,
            extra_headers=[("Authorization", f"Bearer {TOKEN}")]
        ) as ws:
            print("✅ Connected with JWT!")

            await ws.send("ping")
            reply = await ws.recv()
            print("🔊 Server reply:", reply)

    except Exception as e:
        print("❌ Connection failed:", e)

asyncio.run(main())

