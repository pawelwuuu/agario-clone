import asyncio
import websockets
from common.messages import encode, decode, MsgType
import config

# Wspólny stan między siecią a resztą (importuj w main i renderer)
shared_state = {
    "player_id": None,
    "players": {},   # {id: {"id", "x","y","r"}}
    "food": {}       # {id: {"id", "x","y","r"}} - NOWE!
}

# Lokalna pozycja, którą będziemy wysyłać
local_pos = {"x": config.WIDTH/2, "y": config.HEIGHT/2, "r": 15}

# Dodaj lock dla bezpiecznego dostępu
import threading
local_pos_lock = threading.Lock()

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
                    with local_pos_lock:
                        pos_to_send = local_pos.copy()
                        # Dodaj aktualny rozmiar z shared_state jeśli jest dostępny
                        if shared_state["player_id"] and shared_state["player_id"] in shared_state["players"]:
                            pos_to_send["r"] = shared_state["players"][shared_state["player_id"]]["r"]
                    await ws.send(encode(MsgType.MOVE, pos_to_send))
                    await asyncio.sleep(1 / config.FPS)

            send_task = asyncio.create_task(send_loop())

            # 3) Odbiór UPDATE i FOOD_EATEN
            async for raw in ws:
                msg = decode(raw)
                if msg["type"] == MsgType.UPDATE.name.lower():
                    # Teraz data zawiera zarówno players jak i food
                    data = msg["data"]
                    shared_state["players"] = {
                        p["id"]: p for p in data["players"]
                    }
                    shared_state["food"] = {
                        f["id"]: f for f in data["food"]
                    }
                elif msg["type"] == MsgType.FOOD_EATEN.name.lower():
                    # Opcjonalnie: możesz dodać efekty dźwiękowe lub wizualne
                    data = msg["data"]
                    print(f"[Network] Player {data['player_id']} ate food, new size: {data['new_player_size']:.1f}")

            send_task.cancel()

    except Exception as e:
        print(f"[Network] błąd sieci: {e}")

def start_network_thread():
    asyncio.run(network_loop())