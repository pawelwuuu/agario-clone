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
    """Locate an asset both in dev mode and when bundled with PyInstaller."""
    try:
        # PyInstaller mode – look inside _MEIPASS
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        # Dev mode – derive path relative to the running script
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    # In dev mode, jump one level up if we are inside client/
    if not os.path.exists(os.path.join(base_path, *path_parts)):
        base_path = os.path.join(base_path, "..")

    full_path = os.path.join(base_path, *path_parts)

    # Debug asset‑path issues
    if not os.path.exists(full_path):
        print(f"DEBUG: Asset not found: {full_path}")
        print(f"DEBUG: Searched in: {base_path}")
        print(f"DEBUG: CWD is: {os.getcwd()}")

    return full_path


def calculate_speed(base_speed: float, radius: float) -> float:
    """Optional helper that scales speed with player radius (unused in main loop)."""
    min_speed = 0.4
    speed = 1.381551 / math.log(radius / 6.309573)
    return max(min_speed, speed)


# ---------------------------------------------------------------------------
# Movement tuning
# ---------------------------------------------------------------------------
# Feel free to tweak these two constants to taste.
BASE_SPEED = 4        # normal movement speed
BOOST_FACTOR = 2      # multiplier while the SPACE key is held down


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.mixer.init()

    # ---------------------------------------------------------------------
    # Audio: one‑off pop and looping background music
    # ---------------------------------------------------------------------
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

    # ---------------------------------------------------------------------
    # Networking and game loop initialisation
    # ---------------------------------------------------------------------
    nick = show_start_screen(screen)
    net_thread = threading.Thread(
        target=start_network_thread,
        args=(nick,),
        daemon=True,
    )
    net_thread.start()

    clock = pygame.time.Clock()
    running = True

    while running:
        # -----------------------------------------------------------------
        # Event pump & quit handling
        # -----------------------------------------------------------------
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        # -----------------------------------------------------------------
        # Sound effects queued by the networking thread
        # -----------------------------------------------------------------
        with sound_lock:
            if sound_events:
                for event in sound_events:
                    if event == "food_eaten" and pop_sound:
                        pop_sound.set_volume(0.5)
                        pop_sound.play()
                sound_events.clear()

        # -----------------------------------------------------------------
        # Player movement & server‑authoritative position sync
        # -----------------------------------------------------------------
        pid = shared_state.get("player_id")
        if pid and pid in shared_state["players"]:
            with local_pos_lock:
                server_data = shared_state["players"][pid]
                local_pos["x"] = server_data["x"]
                local_pos["y"] = server_data["y"]
                local_pos["r"] = server_data["r"]

                # Keyboard state snapshot --------------------------------------------------
                keys = pygame.key.get_pressed()

                # Determine current frame's speed.  Holding SPACE == boost.
                move_speed = BASE_SPEED * BOOST_FACTOR if keys[pygame.K_SPACE] else BASE_SPEED

                # Movement WASD -------------------------------------------------------------
                if keys[pygame.K_w]:
                    local_pos["y"] -= move_speed
                if keys[pygame.K_s]:
                    local_pos["y"] += move_speed
                if keys[pygame.K_a]:
                    local_pos["x"] -= move_speed
                if keys[pygame.K_d]:
                    local_pos["x"] += move_speed

                # Keep the local copy inside the viewport ----------------------------------
                local_pos["x"] = max(local_pos["r"], min(config.WIDTH  - local_pos["r"], local_pos["x"]))
                local_pos["y"] = max(local_pos["r"], min(config.HEIGHT - local_pos["r"], local_pos["y"]))

        # -----------------------------------------------------------------
        # Render – draw everything based on the shared state
        # -----------------------------------------------------------------
        render(screen, shared_state)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
