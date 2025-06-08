import asyncio
import websockets
from common.messages import encode, decode, MsgType
import config
import threading

shared_state = {
    "player_id": None,
    "players": {},
    "food": {}
}

local_pos = {"x": config.WIDTH/2, "y": config.HEIGHT/2, "r": 15}
local_pos_lock = threading.Lock()

async def network_loop(nick):
    uri = f"ws://localhost:{config.PORT}"
    try:
        async with websockets.connect(uri) as ws:
            # Wyślij nick zaraz po połączeniu
            await ws.send(encode(MsgType.JOIN, {"nick": nick}))
            
            # Odbierz potwierdzenie JOIN z id
            raw = await ws.recv()
            msg = decode(raw)
            if msg["type"] == MsgType.JOIN.name.lower():
                pid = msg["data"]["id"]
                shared_state["player_id"] = pid
                print(f"[Network] JOIN id = {pid}")
                await ws.send(encode(MsgType.MOVE, local_pos))

            async def send_loop():
                while True:
                    with local_pos_lock:
                        pos_to_send = local_pos.copy()
                        if shared_state["player_id"] and shared_state["player_id"] in shared_state["players"]:
                            pos_to_send["r"] = shared_state["players"][shared_state["player_id"]]["r"]
                    await ws.send(encode(MsgType.MOVE, pos_to_send))
                    await asyncio.sleep(1 / config.FPS)

            send_task = asyncio.create_task(send_loop())

            async for raw in ws:
                msg = decode(raw)
                if msg["type"] == MsgType.UPDATE.name.lower():
                    data = msg["data"]
                    shared_state["players"] = {p["id"]: p for p in data["players"]}
                    shared_state["food"] = {f["id"]: f for f in data["food"]}
                    shared_state["portals"] = {portal["id"]: portal for portal in data.get("portals", [])}
                elif msg["type"] == MsgType.FOOD_EATEN.name.lower():
                    data = msg["data"]
                    print(f"[Network] Player {data['player_id']} ate food, new size: {data['new_player_size']:.1f}")

            send_task.cancel()

    except Exception as e:
        print(f"[Network] błąd sieci: {e}")

def start_network_thread(nick):
    asyncio.run(network_loop(nick))
