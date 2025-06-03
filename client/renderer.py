import pygame
import config
import random

def render(screen, shared_state):
    """Rysuje wszystkie kulki wg stanu z shared_state."""
    screen.fill((0, 0, 0))
    
    # 1) Rysuj jedzenie (małe kolorowe kulki)
    for food_id, food in shared_state.get("food", {}).items():
        # Generuj kolor na podstawie ID (żeby był stały dla danej kulki)
        random.seed(hash(food_id) % 1000000)  # Deterministic color based on ID
        color = (
            random.randint(100, 255),
            random.randint(100, 255), 
            random.randint(100, 255)
        )
        pygame.draw.circle(
            screen,
            color,
            (int(food["x"]), int(food["y"])),
            int(food["r"])
        )
    
    # 2) Rysuj graczy (większe kulki)
    pid = shared_state.get("player_id")
    player_size = 0  # Do wyświetlenia rozmiaru
    
    for other_id, p in shared_state.get("players", {}).items():
        # Czerwony dla naszego gracza, zielony dla innych
        color = (255, 0, 0) if other_id == pid else (0, 255, 0)
        pygame.draw.circle(
            screen,
            color,
            (int(p["x"]), int(p["y"])),
            int(p["r"])
        )
        
        # Zapamiętaj rozmiar naszego gracza
        if other_id == pid:
            player_size = p["r"]
        
        # Opcjonalnie: dodaj obramowanie dla lepszej widoczności
        pygame.draw.circle(
            screen,
            (255, 255, 255),  # białe obramowanie
            (int(p["x"]), int(p["y"])),
            int(p["r"]),
            2  # grubość obramowania
        )
    
    # 3) Wyświetl rozmiar gracza w lewym dolnym rogu
    if pid and player_size > 0:
        font = pygame.font.Font(None, 36)
        size_text = font.render(f"Rozmiar: {player_size:.1f}", True, (255, 255, 255))
        screen.blit(size_text, (10, config.HEIGHT - 40))