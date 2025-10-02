import pygame
import os
from collections import deque
import time

from client.src.asset.font.font_loader import FontLoader
from client.src.asset.tile.tile_loader import TileLoader
from client.src.renderer.text import render_text
from client.src.renderer.tile import render_tile

# Debug flag
DEBUG = os.getenv("DASHR_DEBUG", "false").lower() == "true"

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dashr Demo" + (" [DEBUG]" if DEBUG else ""))

# Load font
font_dir = os.path.join("client", "assets", "fonts", "default")
font = FontLoader.load_font_from_directory(font_dir)

# Demo text
text = (
    "Hello, World! This is a font rendering demo. 1234567890. Also tiles test is below."
)

# Load tiles
tiles_dir = os.path.join("client", "assets", "textures", "tiles", "default")
loaded_tiles = TileLoader.load_tiles_from_directory(tiles_dir)

# Clock for FPS
clock = pygame.time.Clock()

# FPS tracking
fps_history = deque()
last_time = time.time()

# Main loop
running = True
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))  # White background

        # Render text
        render_text(screen, text, font, (50, 100), scale=2, color=(0, 0, 0))

        # Render some tiles for demonstration
        render_tile(screen, loaded_tiles["tile_green_full"], (50, 200), scale=2)
        render_tile(screen, loaded_tiles["tile_blue_full"], (100, 200), scale=2)
        render_tile(screen, loaded_tiles["tile_purple_full"], (150, 200), scale=2)
        render_tile(screen, loaded_tiles["tile_cream_full"], (200, 200), scale=2)
        render_tile(screen, loaded_tiles["tile_red_full"], (250, 200), scale=2)
        render_tile(screen, loaded_tiles["tile_sky_full"], (300, 200), scale=2)
        render_tile(screen, loaded_tiles["tile_pink_full"], (350, 200), scale=2)
        render_tile(screen, loaded_tiles["tile_grey_full"], (400, 200), scale=2)

        # FPS tracking and display (only if DEBUG is enabled)
        if DEBUG:
            # Update FPS tracking
            current_time = time.time()
            current_fps = clock.get_fps()
            fps_history.append((current_time, current_fps))

            # Keep only FPS data from the last second
            while fps_history and current_time - fps_history[0][0] > 1.0:
                fps_history.popleft()

            # Calculate stats and render FPS text
            if fps_history:
                fps_values = [fps for _, fps in fps_history if fps > 0]
                if fps_values:
                    avg_fps = sum(fps_values) / len(fps_values)
                    min_fps = min(fps_values)
                    max_fps = max(fps_values)
                    # Render each FPS stat on separate lines
                    render_text(
                        screen,
                        f"FPS: {current_fps:.1f}",
                        font,
                        (WIDTH - 65, 10),
                        scale=1,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Avg: {avg_fps:.1f}",
                        font,
                        (WIDTH - 65, 20),
                        scale=1,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Min: {min_fps:.1f}",
                        font,
                        (WIDTH - 65, 30),
                        scale=1,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Max: {max_fps:.1f}",
                        font,
                        (WIDTH - 65, 40),
                        scale=1,
                        color=(0, 0, 0),
                    )
                else:
                    render_text(
                        screen,
                        f"FPS: {current_fps:.1f}",
                        font,
                        (WIDTH - 65, 10),
                        scale=1,
                        color=(0, 0, 0),
                    )
            else:
                render_text(
                    screen,
                    f"FPS: {current_fps:.1f}",
                    font,
                    (WIDTH - 120, 10),
                    scale=1,
                    color=(0, 0, 0),
                )

        pygame.display.flip()

        clock.tick()

except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Exiting gracefully...")
    running = False

finally:
    pygame.quit()
