from aiohttp import web
import asyncio
import websockets
import config
from .handlers import handler, portal_manager

async def health_check(request):
    return web.Response(text="OK")

async def websocket_server():
    print(f"[Server] Starting WebSocket on port {config.WS_PORT}")
    asyncio.create_task(portal_manager())
    return await websockets.serve(handler, "0.0.0.0", config.WS_PORT)

async def http_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.HTTP_PORT)
    await site.start()
    print(f"[Server] HTTP server running on port {config.HTTP_PORT}")

async def main():
    await http_server()
    ws_server = await websocket_server()
    
    try:
        await asyncio.Future()  # Run forever
    finally:
        ws_server.close()
        await ws_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())