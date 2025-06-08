import asyncio
import websockets
import config
from .handlers import handler, portal_manager

async def main():
    print(f"[Server] Uruchamiam WebSocket na porcie {config.PORT}")
    asyncio.create_task(portal_manager())  # uruchamiamy portal_manager jako task
    async with websockets.serve(handler, "0.0.0.0", config.PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
