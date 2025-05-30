import threading
import pygame

import config
from client.network import start_network_thread, shared_state, local_pos
from client.renderer import render

def main():
    # 1) Start wątku sieci
    net_thread = threading.Thread(target=start_network_thread, daemon=True)
    net_thread.start()

    # 2) Init Pygame
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    clock = pygame.time.Clock()
    speed = 4
    running = True

    while running:
        # obsługa zdarzeń
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        # aktualizacja lokalnej pozycji (tylko gdy mamy player_id)
        pid = shared_state.get("player_id")
        if pid:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: local_pos["y"] -= speed
            if keys[pygame.K_s]: local_pos["y"] += speed
            if keys[pygame.K_a]: local_pos["x"] -= speed
            if keys[pygame.K_d]: local_pos["x"] += speed

        # render wg stanu pobranego z serwera
        render(screen, shared_state)

        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
