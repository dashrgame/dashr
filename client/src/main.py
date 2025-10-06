import pygame
import os
from collections import deque
import time

from client.src.asset.font.font_loader import FontLoader
from client.src.asset.tile.tile_loader import TileLoader
from client.src.renderer.text import render_text
from client.src.renderer.tile import render_tile
from client.src.input.manager import InputManager

# Debug flag
DEBUG = False

# Set window properties before initializing pygame
os.environ["SDL_VIDEO_X11_WMCLASS"] = "Dashr"
os.environ["SDL_VIDEO_WINDOW_POS"] = "SDL_WINDOWPOS_CENTERED"

# Initialize pygame
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode(size=(WIDTH, HEIGHT))
pygame.display.set_caption("Dashr Demo")

# Set window icon
icon_path = os.path.join("client", "icons", "current.png")
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path).convert()
    pygame.display.set_icon(icon)

# Load font
font_dir = os.path.join("client", "assets", "fonts", "default")
font = FontLoader.load_font_from_directory(font_dir)

# Load tiles
tiles_dir = os.path.join("client", "assets", "textures", "tiles", "default")
loaded_tiles = TileLoader.load_tiles_from_directory(tiles_dir)

# Input manager
input_manager = InputManager()
input_manager.start()

input_manager.on_key_press(
    pygame.K_ESCAPE, lambda key: pygame.event.post(pygame.event.Event(pygame.QUIT))
)
input_manager.on_key_press(pygame.K_F3, lambda key: globals().update(DEBUG=not DEBUG))

# Clock for FPS
clock = pygame.time.Clock()

# FPS tracking
fps_history = deque()
last_time = time.time()

# UI variables
UI_SCALE = 1

# Main loop
running = True
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            input_manager.handle_event(event)

        screen.fill((255, 255, 255))  # White background

        # FPS tracking (always enabled)
        current_time = time.time()
        current_fps = clock.get_fps()
        fps_history.append((current_time, current_fps))

        # Keep only FPS data from the last second
        while fps_history and current_time - fps_history[0][0] > 1.0:
            fps_history.popleft()

        # FPS display (only if DEBUG is enabled)
        if DEBUG:
            # Calculate stats and render FPS text
            if fps_history:
                fps_values = [fps for _, fps in fps_history if fps > 0]
                if fps_values:
                    avg_fps = sum(fps_values) / len(fps_values)
                    min_fps = min(fps_values)
                    max_fps = max(fps_values)

                    # Draw white background box for readability
                    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 75, 5, 70, 50))

                    # Render each FPS stat on separate lines
                    render_text(
                        screen,
                        f"FPS: {current_fps:.1f}",
                        font,
                        (WIDTH - 65, 10),
                        scale=UI_SCALE,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Avg: {avg_fps:.1f}",
                        font,
                        (WIDTH - 65, 20),
                        scale=UI_SCALE,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Min: {min_fps:.1f}",
                        font,
                        (WIDTH - 65, 30),
                        scale=UI_SCALE,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Max: {max_fps:.1f}",
                        font,
                        (WIDTH - 65, 40),
                        scale=UI_SCALE,
                        color=(0, 0, 0),
                    )
                else:
                    # Draw white background box for readability
                    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 75, 5, 70, 15))

                    render_text(
                        screen,
                        f"FPS: {current_fps:.1f}",
                        font,
                        (WIDTH - 65, 10),
                        scale=UI_SCALE,
                        color=(0, 0, 0),
                    )
            else:
                # Draw white background box for readability
                pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 130, 5, 125, 15))

                render_text(
                    screen,
                    f"FPS: {current_fps:.1f}",
                    font,
                    (WIDTH - 120, 10),
                    scale=UI_SCALE,
                    color=(0, 0, 0),
                )

        pygame.display.flip()

        clock.tick()

except KeyboardInterrupt:
    print("\nRecieved interrupt, exiting...")
    running = False

finally:
    input_manager.stop()
    pygame.quit()
