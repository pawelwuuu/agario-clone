import pygame
import config

def render(screen, shared_state):
    """Rysuje wszystkie kulki wg stanu z shared_state."""
    screen.fill((0, 0, 0))
    pid = shared_state.get("player_id")
    for other_id, p in shared_state["players"].items():
        color = (255, 0, 0) if other_id == pid else (0, 255, 0)
        pygame.draw.circle(
            screen,
            color,
            (int(p["x"]), int(p["y"])),
            int(p["r"])
        )
