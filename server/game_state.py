from typing import Dict, List
import uuid
import random
import math
import config
from common.messages import MsgType, encode

NICK_PREFIXES = ["Speedy", "Crazy", "Happy", "Lazy", "Smart", "Sly", "Brave", "Wild"]
NICK_ANIMALS = ["Tiger", "Eagle", "Shark", "Panda", "Wolf", "Fox", "Lion", "Bear"]
PORTAL_RADIUS = 10

class GameState:
    def __init__(self):
        self.players: Dict[str, dict] = {}
        self.food: Dict[str, dict] = {}
        self.portals: Dict[str, dict] = {}
        self.max_food = 50
        self._generate_initial_portal()
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

    def _generate_random_nick(self) -> str:
        return random.choice(NICK_PREFIXES) + random.choice(NICK_ANIMALS) + str(random.randint(1, 999))

    def add_player(self, nick: str = None) -> str:
        player_id = str(uuid.uuid4())
        if not nick:
            nick = self._generate_random_nick()
        self.players[player_id] = {
            "id": player_id,
            "nick": nick,
            "x": config.WIDTH / 2,
            "y": config.HEIGHT / 2,
            "r": 15
        }
        return player_id

    def remove_player(self, player_id: str):
        self.players.pop(player_id, None)

    def _check_player_collisions(self):
        players = list(self.players.values())
        for i, player1 in enumerate(players):
            for player2 in players[i+1:]:
                distance = math.sqrt((player1["x"] - player2["x"])**2 + 
                                     (player1["y"] - player2["y"])**2)
                min_r = min(player1["r"], player2["r"])
                if distance < min_r * 0.5:
                    if player1["r"] > player2["r"] * 1.1:
                        self._eat_player(player1["id"], player2["id"])
                    elif player2["r"] > player1["r"] * 1.1:
                        self._eat_player(player2["id"], player1["id"])

    def _eat_player(self, eater_id: str, eaten_id: str):
        eaten_size = self.players[eaten_id]["r"]
        self.players[eater_id]["r"] += eaten_size * 0.5
        self.remove_player(eaten_id)
        print(f"Player {eater_id} ate player {eaten_id} and grew to {self.players[eater_id]['r']:.1f}")

    def update_player(self, player_id: str, x: float, y: float, r: float) -> List[str]:
        if player_id not in self.players:
            return []
        self.players[player_id]["x"] = x
        self.players[player_id]["y"] = y
        eaten_food = self._check_food_collisions(player_id)
        self._check_player_collisions()
        self._check_portal_teleport()
        return eaten_food

    def _check_food_collisions(self, player_id: str) -> List[str]:
        player = self.players[player_id]
        eaten_food = []
        for food_id, food in list(self.food.items()):
            distance = math.sqrt((player["x"] - food["x"])**2 + (player["y"] - food["y"])**2)
            if distance < player["r"] + food["r"]:
                eaten_food.append(food_id)
                self.players[player_id]["r"] += 0.1
                del self.food[food_id]
                self._spawn_food()
        return eaten_food

    def get_state(self) -> dict:
        return {
            "players": list(self.players.values()),
            "food": list(self.food.values()),
            "portals": list(self.portals.values())
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

    def _is_position_free(self, x: float, y: float, r: float) -> bool:
        for p in self.players.values():
            dx = p["x"] - x
            dy = p["y"] - y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < p["r"] + r + 10:
                return False
        return True

    def _find_free_position(self, width: float, height: float, radius: float, max_attempts=100):
        for _ in range(max_attempts):
            x = random.uniform(radius, width - radius)
            y = random.uniform(radius, height - radius)
            if self._is_position_free(x, y, radius):
                return x, y
        return None, None

    def _generate_initial_portal(self):
        x, y = self._find_free_position(config.WIDTH, config.HEIGHT, PORTAL_RADIUS)
        if x is not None:
            portal_id = str(uuid.uuid4())
            self.portals[portal_id] = {
                "id": portal_id,
                "x": x,
                "y": y,
                "r": PORTAL_RADIUS
            }

    def _check_portal_teleport(self):
        to_remove = []
        for player_id, p in self.players.items():
            for portal_id, portal in self.portals.items():
                dx = p["x"] - portal["x"]
                dy = p["y"] - portal["y"]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < p["r"] + portal["r"]:
                    new_x, new_y = self._find_free_position(config.WIDTH, config.HEIGHT, p["r"])
                    if new_x is not None:
                        self.players[player_id]["x"] = new_x
                        self.players[player_id]["y"] = new_y
                    to_remove.append(portal_id)
                    break
        for pid in to_remove:
            del self.portals[pid]

    def generate_portal(self):
        x, y = self._find_free_position(config.WIDTH, config.HEIGHT, PORTAL_RADIUS)
        if x is not None:
            portal_id = str(uuid.uuid4())
            portal = {
                "id": portal_id,
                "x": x,
                "y": y,
                "r": PORTAL_RADIUS
            }
            self.portals[portal_id] = portal
            return portal
        return None