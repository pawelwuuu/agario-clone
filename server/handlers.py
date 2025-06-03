import asyncio
import logging
from websockets import WebSocketServerProtocol
from common.messages import decode, encode, MsgType
from .game_state import GameState

# logger
logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'
)

game = GameState()
clients: dict[str, WebSocketServerProtocol] = {}

async def broadcast_state():
    """Rozsyła wszystkim klientom komunikat UPDATE"""
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
    """Rozsyła informację o zjedzeniu jedzenia"""
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
    """Rozsyła informację o zjedzeniu gracza"""
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

async def handler(ws: WebSocketServerProtocol, path=None):
    # 1) Dołącz nowego gracza
    player_id = game.add_player()
    clients[player_id] = ws

    # 2) Potwierdź JOIN i zaloguj
    try:
        await ws.send(encode(MsgType.JOIN, {"id": player_id}))
        logging.info(f"Player {player_id} joined")
        
        # 3) Wyślij początkowy stan gry
        await broadcast_state()
        
    except Exception as e:
        logging.error(f"Error sending join confirmation to {player_id}: {e}")
        game.remove_player(player_id)
        clients.pop(player_id, None)
        return

    try:
        async for raw in ws:
            msg = decode(raw)
            if msg["type"] == MsgType.MOVE.name.lower():
                data = msg["data"]
                
                # 4) Aktualizuj stan gracza
                eaten_food = game.update_player(player_id, data["x"], data["y"], data["r"])
                
                # 5) Jeśli gracz zjadł jedzenie, poinformuj wszystkich
                if eaten_food:
                    logging.info(f"Player {player_id} ate {len(eaten_food)} food pellets")
                    await broadcast_food_eaten(player_id, eaten_food)
                
                # 6) Broadcast zaktualizowanego stanu gry
                await broadcast_state()
                
    except Exception as e:
        logging.error(f"Error in handler for {player_id}: {e}")
    finally:
        # 7) Usuń gracza z gry i z listy połączeń
        game.remove_player(player_id)
        clients.pop(player_id, None)
        logging.info(f"Player {player_id} left")
        
        # 8) Poinformuj pozostałych graczy o zmianie stanu
        await broadcast_state()