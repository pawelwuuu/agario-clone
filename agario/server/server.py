from aiohttp import web
import asyncio
import websockets
import config
from .handlers import handler, portal_manager

# Create HTTP app for health checks
http_app = web.Application()

async def health_check(request):
    return web.Response(text="OK")

http_app.router.add_get('/health', health_check)

async def websocket_server():
    print(f"[Server] Starting WebSocket on port {config.PORT}")
    asyncio.create_task(portal_manager())
    return await websockets.serve(handler, "0.0.0.0", config.PORT)

async def http_server():
    runner = web.AppRunner(http_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)  # Different port for HTTP
    await site.start()
    print(f"[Server] Health check at http://0.0.0.0:8080/health")

async def main():
    await http_server()
    await websocket_server()
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())