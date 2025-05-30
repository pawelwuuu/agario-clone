import asyncio
import websockets
import config
from .handlers import handler

async def main():
    print(f"[Server] Uruchamiam WebSocket na porcie {config.PORT}")
    async with websockets.serve(handler, "0.0.0.0", config.PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
