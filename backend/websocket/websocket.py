import asyncio
import websockets

class WebSocket:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.pi_socket = None
        self.host = host
        self.port = port
        self.server = None
        asyncio.run(self.start())
    
    async def start(self):
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        print(f"WebSocket server listening on {self.host}:{self.port}")
        await self.server.wait_closed()

    async def handle_client(self, ws):
        print("Client connected")

        try:
            async for message in ws:
                print(f"Received: {message}")

                if message == "HELLO_FROM_PI":
                    self.pi_socket = ws
                    print("Raspberry Pi registered")
                    await ws.send("ACKNOWLEDGE")
                    continue

                print("Message from client:", message)

        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:
            if ws is self.pi_socket:
                print("Raspberry Pi connection lost")
                self.pi_socket = None

    async def send_command(self, cmd: str):
        if self.pi_socket is None:
            print("No Raspberry PI connected")
            return

        try:
            await self.pi_socket.send(cmd)
            print(f"Sent to Raspberry PI: {cmd}")

        except:
            self.pi_socket = None
            print("Lost connection to Raspberry PI")

async def main():
    socket = WebSocket()
    await socket.start()

if __name__ == "__main__":
    socket = WebSocket()