from typing import Dict, List
import uuid
import config
from common.messages import MsgType, encode

class GameState:
    def __init__(self):
        # player_id → {"id":…, "x":…, "y":…, "r":…}
        self.players: Dict[str, dict] = {}

    def add_player(self) -> str:
        """Dodaje nowego gracza i zwraca jego wygenerowane ID."""
        player_id = str(uuid.uuid4())
        self.players[player_id] = {
            "id": player_id,
            "x": config.WIDTH / 2,
            "y": config.HEIGHT / 2,
            "r": 10
        }
        return player_id

    def remove_player(self, player_id: str):
        """Usuwa gracza ze stanu."""
        self.players.pop(player_id, None)

    def update_player(self, player_id: str, x: float, y: float, r: float):
        """Aktualizuje pozycję i rozmiar gracza."""
        if player_id in self.players:
            self.players[player_id].update(x=x, y=y, r=r)

    def get_state(self) -> List[dict]:
        """Zwraca listę słowników z danymi wszystkich graczy."""
        return list(self.players.values())

    def encode_update(self) -> str:
        """Zwraca zakodowany komunikat UPDATE do broadcastu."""
        return encode(MsgType.UPDATE, {"players": self.get_state()})
