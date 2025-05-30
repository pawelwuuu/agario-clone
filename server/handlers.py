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
    msg = game.encode_update()
    # gather tasków, żeby nie wyrzucać błędu o korutynach
    await asyncio.gather(*(ws.send(msg) for ws in clients.values()))

async def handler(ws: WebSocketServerProtocol, path=None):
    # 1) Dołącz nowego gracza
    player_id = game.add_player()
    clients[player_id] = ws

    # 2) Potwierdź JOIN i zaloguj
    await ws.send(encode(MsgType.JOIN, {"id": player_id}))
    logging.info(f"Player {player_id} joined")

    try:
        async for raw in ws:
            msg = decode(raw)
            if msg["type"] == MsgType.MOVE.name.lower():
                data = msg["data"]
                # 3) Aktualizuj stan gracza przez GameState
                game.update_player(player_id, data["x"], data["y"], data["r"])
                logging.info(f"Player {player_id} moved to x={data['x']:.1f}, y={data['y']:.1f}")
                # 4) Broadcast stanu gry
                await broadcast_state()
    except Exception as e:
        logging.error(f"Error in handler for {player_id}: {e}")
    finally:
        # 5) Usuń gracza z gry i z listy połączeń
        game.remove_player(player_id)
        clients.pop(player_id, None)
        logging.info(f"Player {player_id} left")
