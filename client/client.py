import threading
import pygame
import math
import time

import config
from client.network import start_network_thread, shared_state, local_pos, local_pos_lock
from client.renderer import render

def calculate_speed(base_speed, radius):
    """Oblicza prędkość na podstawie rozmiaru kulki"""
    min_speed = 0.4
    speed = 1.381551 / math.log(radius / 6.309573)
    return max(min_speed, speed)

def main():
    net_thread = threading.Thread(target=start_network_thread, daemon=True)
    net_thread.start()

    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    clock = pygame.time.Clock()
    base_speed = 4
    running = True
    last_shrink_time = time.time()
    last_server_update = time.time()

    while running:
        current_time = time.time()
        dt = min(0.1, clock.get_time() / 1000.0)  # Delta time ograniczona do 100ms
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        pid = shared_state.get("player_id")
        if pid and pid in shared_state["players"]:
            with local_pos_lock:
                # Aktualizuj rozmiar tylko z serwera jeśli jest nowszy
                server_size = shared_state["players"][pid]["r"]
                if abs(server_size - local_pos["r"]) > 0.1:  # Tolerancja dla floatów
                    local_pos["r"] = server_size
                    last_server_update = current_time
                    print(f"[Sync] Updated size from server: {server_size:.2f}")
                
                # Zmniejszanie rozmiaru tylko jeśli nie było aktualizacji z serwera przez >1s
                elif current_time - last_server_update >= 1.0 and current_time - last_shrink_time >= 1.0:
                    if local_pos["r"] > 15.0:
                        local_pos["r"] = max(15.0, local_pos["r"] * 0.99)
                        last_shrink_time = current_time
                        print(f"[Shrink] Size: {local_pos['r']:.2f}")

                # Oblicz prędkość
                current_speed = calculate_speed(base_speed, local_pos["r"])
                
                # Obsługa ruchu
                keys = pygame.key.get_pressed()
                old_pos = local_pos.copy()
                if keys[pygame.K_w]: local_pos["y"] -= current_speed * dt * 60
                if keys[pygame.K_s]: local_pos["y"] += current_speed * dt * 60
                if keys[pygame.K_a]: local_pos["x"] -= current_speed * dt * 60
                if keys[pygame.K_d]: local_pos["x"] += current_speed * dt * 60
                
                # Ograniczenia ruchu
                local_pos["x"] = max(local_pos["r"], min(config.WIDTH - local_pos["r"], local_pos["x"]))
                local_pos["y"] = max(local_pos["r"], min(config.HEIGHT - local_pos["r"], local_pos["y"]))
                
                if old_pos != local_pos:
                    print(f"[Move] Pos: ({local_pos['x']:.1f}, {local_pos['y']:.1f}) Size: {local_pos['r']:.2f} Speed: {current_speed:.2f}")

        render(screen, shared_state)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()