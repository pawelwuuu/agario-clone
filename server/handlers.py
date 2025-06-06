import asyncio
import logging
from websockets import WebSocketServerProtocol
from common.messages import decode, encode, MsgType
from .game_state import GameState

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'
)

game = GameState()
clients: dict[str, WebSocketServerProtocol] = {}

async def portal_manager():
    while True:
        await asyncio.sleep(15)
        if not game.portals:
            new_portal = game.generate_portal()
            if new_portal:
                await broadcast_state()


async def broadcast_state():
    if not clients:
        return
    msg = game.encode_update()
    tasks = []
    for player_id, ws in list(clients.items()):
        try:
            tasks.append(ws.send(msg))
        except Exception as e:
            logging.warning(f"Failed to send to {player_id}: {e}")
            clients.pop(player_id, None)
            game.remove_player(player_id)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def broadcast_food_eaten(player_id: str, eaten_food_ids: list):
    if not clients or not eaten_food_ids:
        return
    msg = game.encode_food_eaten(player_id, eaten_food_ids)
    tasks = []
    for pid, ws in list(clients.items()):
        try:
            tasks.append(ws.send(msg))
        except Exception as e:
            logging.warning(f"Failed to send food_eaten to {pid}: {e}")
            clients.pop(pid, None)
            game.remove_player(pid)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def broadcast_player_eaten(eater_id: str, eaten_id: str):
    if not clients:
        return
    msg = game.encode_player_eaten(eater_id, eaten_id)
    tasks = []
    for pid, ws in list(clients.items()):
        try:
            tasks.append(ws.send(msg))
        except Exception as e:
            logging.warning(f"Failed to send player_eaten to {pid}: {e}")
            clients.pop(pid, None)
            game.remove_player(pid)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def respawn_portal_after_delay(portal_id: str, delay: int = 15):
    await asyncio.sleep(delay)
    game.spawn_portal(portal_id)
    await broadcast_state()

async def handler(ws: WebSocketServerProtocol, path=None):
    player_id = game.add_player()
    clients[player_id] = ws

    try:
        await ws.send(encode(MsgType.JOIN, {
            "id": player_id,
            "nick": game.players[player_id]["nick"]
        }))
        await broadcast_state()
    except Exception:
        game.remove_player(player_id)
        clients.pop(player_id, None)
        return

    try:
        async for raw in ws:
            msg = decode(raw)

            if msg["type"] == MsgType.MOVE.name.lower():
                data = msg["data"]
                eaten_food = game.update_player(player_id, data["x"], data["y"], data["r"])
                if eaten_food:
                    await broadcast_food_eaten(player_id, eaten_food)
                await broadcast_state()

            elif msg["type"] == "enter_portal":
                portal_id = msg["data"]["portal_id"]
                entered = game.player_enter_portal(player_id, portal_id)
                if entered:
                    await broadcast_state()
                    asyncio.create_task(respawn_portal_after_delay(portal_id, 15))

    finally:
        game.remove_player(player_id)
        clients.pop(player_id, None)
        await broadcast_state()
