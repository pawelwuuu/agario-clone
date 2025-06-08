import threading
import pygame
import math
import os
import sys
from pathlib import Path

import config
from .network import start_network_thread, shared_state, local_pos, local_pos_lock, sound_events, sound_lock
from .renderer import render
from .start_screen import show_start_screen

def get_asset_path(*path_parts):
    """Pobiera ścieżkę do zasobu, działa zarówno w dev jak i po kompilacji"""
    try:
        # Tryb PyInstaller - sprawdź folder _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Tryb developerski - użyj ścieżki względem pliku wykonywalnego
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # W trybie developerskim przejdź do folderu nadrzędnego (jeśli plik jest w client/)
    if not os.path.exists(os.path.join(base_path, *path_parts)):
        base_path = os.path.join(base_path, '..')
    
    full_path = os.path.join(base_path, *path_parts)
    
    # Debugowanie ścieżek
    if not os.path.exists(full_path):
        print(f"DEBUG: Nie znaleziono pliku: {full_path}")
        print(f"DEBUG: Szukane w: {base_path}")
        print(f"DEBUG: Bieżący katalog: {os.getcwd()}")
    
    return full_path

def calculate_speed(base_speed, radius):
    min_speed = 0.4
    speed = 1.381551 / math.log(radius / 6.309573)
    return max(min_speed, speed)

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.mixer.init()
    
    # Inicjalizacja dźwięku
    try:
        sound_path = get_asset_path("assets", "sounds", "Pop 1.mp3")
        pop_sound = pygame.mixer.Sound(sound_path)
        print(f"Loaded sound from: {sound_path}")
    except Exception as e:
        print(f"Could not load sound file: {e}")
        pop_sound = None
        
    try:
        music_path = get_asset_path("assets", "sounds", "muzyka1.mp3")
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        print(f"Playing background music from: {music_path}")
    except Exception as e:
        print(f"Could not load or play background music: {e}")

    nick = show_start_screen(screen)
    net_thread = threading.Thread(target=start_network_thread, args=(nick,), daemon=True)
    net_thread.start()
    
    clock = pygame.time.Clock()
    speed = 4
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        # Obsługa dźwięków
        with sound_lock:
            if sound_events:
                for event in sound_events:
                    if event == "food_eaten" and pop_sound:
                        pop_sound.set_volume(0.5)
                        pop_sound.play()
                sound_events.clear()

        pid = shared_state.get("player_id")
        if pid and pid in shared_state["players"]:
            with local_pos_lock:
                server_data = shared_state["players"][pid]
                local_pos["x"] = server_data["x"]
                local_pos["y"] = server_data["y"]
                local_pos["r"] = server_data["r"]
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]: local_pos["y"] -= speed
                if keys[pygame.K_s]: local_pos["y"] += speed
                if keys[pygame.K_a]: local_pos["x"] -= speed
                if keys[pygame.K_d]: local_pos["x"] += speed
                
                local_pos["x"] = max(local_pos["r"], min(config.WIDTH - local_pos["r"], local_pos["x"]))
                local_pos["y"] = max(local_pos["r"], min(config.HEIGHT - local_pos["r"], local_pos["y"]))

        render(screen, shared_state)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()