import asyncio
import websockets
from common.messages import encode, decode, MsgType
import config

# Wspólny stan między siecią a resztą (importuj w main i renderer)
shared_state = {
    "player_id": None,
    "players": {}   # {id: {"id", "x","y","r"}}
}

# Lokalna pozycja, którą będziemy wysyłać
local_pos = {"x": config.WIDTH/2, "y": config.HEIGHT/2, "r": 10}

async def network_loop():
    uri = f"ws://localhost:{config.PORT}"
    try:
        async with websockets.connect(uri) as ws:
            # 1) Odebranie JOIN
            raw = await ws.recv()
            msg = decode(raw)
            if msg["type"] == MsgType.JOIN.name.lower():
                pid = msg["data"]["id"]
                shared_state["player_id"] = pid
                print(f"[Network] JOIN id = {pid}")
                # Wyślij od razu pierwszą pozycję
                await ws.send(encode(MsgType.MOVE, local_pos))

            # 2) Task do ciągłego wysyłania MOVE
            async def send_loop():
                while True:
                    await ws.send(encode(MsgType.MOVE, local_pos))
                    await asyncio.sleep(1 / config.FPS)

            send_task = asyncio.create_task(send_loop())

            # 3) Odbiór UPDATE
            async for raw in ws:
                msg = decode(raw)
                if msg["type"] == MsgType.UPDATE.name.lower():
                    shared_state["players"] = {
                        p["id"]: p for p in msg["data"]["players"]
                    }

            send_task.cancel()

    except Exception as e:
        print(f"[Network] błąd sieci: {e}")

def start_network_thread():
    asyncio.run(network_loop())
