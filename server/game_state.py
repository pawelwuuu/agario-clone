from typing import Dict, List
import uuid
import random
import math
import config
from common.messages import MsgType, encode

class GameState:
    def __init__(self):
        self.players: Dict[str, dict] = {}
        self.food: Dict[str, dict] = {}
        self.max_food = 50
        self._generate_initial_food()

    def _generate_initial_food(self):
        for _ in range(self.max_food):
            self._spawn_food()

    def _spawn_food(self):
        food_id = str(uuid.uuid4())
        self.food[food_id] = {
            "id": food_id,
            "x": random.uniform(5, config.WIDTH - 5),
            "y": random.uniform(5, config.HEIGHT - 5),
            "r": random.uniform(2, 5)
        }

    def add_player(self) -> str:
        player_id = str(uuid.uuid4())
        self.players[player_id] = {
            "id": player_id,
            "x": config.WIDTH / 2,
            "y": config.HEIGHT / 2,
            "r": 15
        }
        return player_id

    def remove_player(self, player_id: str):
        self.players.pop(player_id, None)

    def _check_player_collisions(self):
        """Sprawdza kolizje między graczami i wykonuje zjadanie"""
        players = list(self.players.values())
        for i, player1 in enumerate(players):
            for player2 in players[i+1:]:
                distance = math.sqrt((player1["x"] - player2["x"])**2 + 
                              (player1["y"] - player2["y"])**2)
                
                # Sprawdź czy gracze się stykają
                if distance < player1["r"] + player2["r"]:
                    # Sprawdź warunek zjadania (10% różnicy)
                    if player1["r"] > player2["r"] * 1.1:
                        # Gracz1 zjada gracza2
                        self._eat_player(player1["id"], player2["id"])
                    elif player2["r"] > player1["r"] * 1.1:
                        # Gracz2 zjada gracza1
                        self._eat_player(player2["id"], player1["id"])

    def _eat_player(self, eater_id: str, eaten_id: str):
        """Realizuje mechanizm zjadania gracza"""
        eaten_size = self.players[eaten_id]["r"]
        
        # Zwiększ rozmiar zjadającego o 50% rozmiaru zjadanego
        self.players[eater_id]["r"] += eaten_size * 0.5
        
        # Usuń zjadanego gracza
        self.remove_player(eaten_id)
        
        # Możesz dodać dodatkowe efekty (punkty, powiadomienia itp.)
        print(f"Player {eater_id} ate player {eaten_id} and grew to {self.players[eater_id]['r']:.1f}")

    def update_player(self, player_id: str, x: float, y: float, r: float):
        if player_id not in self.players:
            return []
        
        # Aktualizuj tylko pozycję, rozmiar jest zarządzany przez kolizje
        self.players[player_id]["x"] = x
        self.players[player_id]["y"] = y
        
        # Sprawdź kolizje
        eaten_food = self._check_food_collisions(player_id)
        self._check_player_collisions()
        
        return eaten_food

    def _check_food_collisions(self, player_id: str) -> List[str]:
        player = self.players[player_id]
        eaten_food = []
        
        for food_id, food in list(self.food.items()):
            distance = math.sqrt((player["x"] - food["x"])**2 + 
                          (player["y"] - food["y"])**2)
            
            if distance < player["r"] + food["r"]:
                eaten_food.append(food_id)
                self.players[player_id]["r"] += 0.1  # Mały wzrost za jedzenie
                del self.food[food_id]
                self._spawn_food()
        
        return eaten_food

    def get_state(self) -> dict:
        return {
            "players": list(self.players.values()),
            "food": list(self.food.values())
        }

    def encode_update(self) -> str:
        return encode(MsgType.UPDATE, self.get_state())

    def encode_food_eaten(self, player_id: str, eaten_food_ids: List[str]) -> str:
        return encode(MsgType.FOOD_EATEN, {
            "player_id": player_id,
            "food_ids": eaten_food_ids,
            "new_player_size": self.players[player_id]["r"] if player_id in self.players else 0
        })

    def encode_player_eaten(self, eater_id: str, eaten_id: str) -> str:
        return encode(MsgType.PLAYER_EATEN, {
            "eater_id": eater_id,
            "eaten_id": eaten_id,
            "new_size": self.players[eater_id]["r"]
        })