import asyncio
import websockets

WS_URL = "ws://localhost:8000/ws/audio"
TOKEN  = "<paste-your-jwt-here>"  # ya env se inject karo

async def main():
    try:
        async with websockets.connect(
            WS_URL,
            extra_headers={"Authorization": f"Bearer {TOKEN}"}
        ) as ws:
            print("✅ Connected with JWT")

            # Test message
            await ws.send("hello with JWT")
            print("➡️ sent: hello with JWT")

            # Wait for response
            resp = await ws.recv()
            print("⬅️ received:", resp)

    except Exception as e:
        print("❌ Failed:", e)

if __name__ == "__main__":
    asyncio.run(main())

