import asyncio
import websockets

arduino_socket = None

async def handle_client(ws, path):
    global arduino_socket

    print("Client connected")

    async for message in ws:
        print(f"Received: {message}")

        if message == "HELLO_FROM_ARDUINO":
            arduino_socket = ws
            print("Arduino registered")
            await ws.send("ACKNOWLEDGE")

async def send_command(cmd: str):
    global arduino_socket

    if arduino_socket is None:
        print("No Arduino connected")
        return

    try:
        await arduino_socket.send(cmd)
        print(f"Sent to Arduino: {cmd}")

    except:
        arduino_socket = None
        print("Lost connection to Arduino")