import pygame
import config
import random

def render(screen, shared_state):
    screen.fill((0, 0, 0))
    
    for food_id, food in shared_state.get("food", {}).items():
        random.seed(hash(food_id) % 1000000)
        color = (
            random.randint(100, 255),
            random.randint(100, 255), 
            random.randint(100, 255)
        )
        pygame.draw.circle(screen, color, (int(food["x"]), int(food["y"])), int(food["r"]))
    
    pid = shared_state.get("player_id")
    player_size = 0
    font = pygame.font.Font(None, 24)  # stwórz font tylko raz

    for other_id, p in shared_state.get("players", {}).items():
        color = (255, 0, 0) if other_id == pid else (0, 255, 0)
        pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), int(p["r"]))
        pygame.draw.circle(screen, (255, 255, 255), (int(p["x"]), int(p["y"])), int(p["r"]), 2)
        
        # Rysowanie nicku nad kulką
        nick = p.get("nick", "Unknown")
        text_surface = font.render(nick, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(int(p["x"]), int(p["y"]) - int(p["r"]) - 10))
        screen.blit(text_surface, text_rect)
        
        if other_id == pid:
            player_size = p["r"]
    
    if pid and player_size > 0:
        size_text = font.render(f"Rozmiar: {player_size:.1f}", True, (255, 255, 255))
        screen.blit(size_text, (10, config.HEIGHT - 40))