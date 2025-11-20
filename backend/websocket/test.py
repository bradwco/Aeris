import asyncio
import websockets

async def test():
    uri = "ws://0.0.0.0:8080"   # or ws://127.0.0.1:8080
    async with websockets.connect(uri) as ws:
        print("Connected to server!")

        await ws.send("HELLO_FROM_PI")
        print("Sent: HELLO_FROM_PI")

        reply = await ws.recv()
        print("Received:", reply)

asyncio.run(test())
