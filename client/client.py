import threading
import pygame
import math
import time

import config
from client.network import start_network_thread, shared_state, local_pos, local_pos_lock
from client.renderer import render

def calculate_speed(base_speed, radius):
    min_speed = 0.4
    speed = 1.381551 / math.log(radius / 6.309573)
    return max(min_speed, speed)

def main():
    net_thread = threading.Thread(target=start_network_thread, daemon=True)
    net_thread.start()

    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    clock = pygame.time.Clock()
    speed = 4
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        pid = shared_state.get("player_id")
        if pid and pid in shared_state["players"]:
            with local_pos_lock:
                # Pełna synchronizacja z serwerem
                server_data = shared_state["players"][pid]
                local_pos["x"] = server_data["x"]
                local_pos["y"] = server_data["y"]
                local_pos["r"] = server_data["r"]
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]: local_pos["y"] -= speed
                if keys[pygame.K_s]: local_pos["y"] += speed
                if keys[pygame.K_a]: local_pos["x"] -= speed
                if keys[pygame.K_d]: local_pos["x"] += speed
                
                # Ograniczenia ruchu
                local_pos["x"] = max(local_pos["r"], min(config.WIDTH - local_pos["r"], local_pos["x"]))
                local_pos["y"] = max(local_pos["r"], min(config.HEIGHT - local_pos["r"], local_pos["y"]))

        render(screen, shared_state)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()