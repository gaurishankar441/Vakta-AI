import asyncio
import websockets

WS_URL = "ws://localhost:8000/ws/audio"   # no-auth raw WS

async def main():
    try:
        async with websockets.connect(WS_URL) as ws:
            print(f"✅ Connected to {WS_URL}")

            # Send dummy text
            await ws.send("hello from client")
            print("➡️ sent: hello from client")

            # Listen for one response
            response = await ws.recv()
            print("⬅️ received:", response)

    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    asyncio.run(main())

