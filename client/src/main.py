import pygame
import os
from collections import deque
import time

from client.src.asset.font.font_loader import FontLoader
from client.src.asset.tile.tile_loader import TileLoader
from client.src.renderer.text import render_text
from client.src.renderer.tile import render_tile
from client.src.input.manager import InputManager
from client.src.ui.page_manager import PageManager
from client.src.ui.pages.title import Title

# Debug flag
debug = False

# Set window properties before initializing pygame
os.environ["SDL_VIDEO_X11_WMCLASS"] = "Dashr"
os.environ["SDL_VIDEO_WINDOW_POS"] = "SDL_WINDOWPOS_CENTERED"

# Initialize pygame
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

# Set up display
width, height = 800, 480
screen = pygame.display.set_mode(size=(width, height))
pygame.display.set_caption("Dashr Demo")

# Set window icon
icon_path = os.path.join("client", "icons", "current.png")
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path).convert()
    pygame.display.set_icon(icon)

# Load font
font_dir = os.path.join("client", "assets", "font")
font = FontLoader.load_font_from_directory(font_dir)

# Load tiles
tiles_dir = os.path.join("client", "assets", "textures", "tiles", "default")
loaded_tiles = TileLoader.load_tiles_from_directory(tiles_dir)

# Page manager
page_manager = PageManager()
title_page = Title()
page_manager.set_page(title_page)

# Input manager
input_manager = InputManager()
input_manager.start()

# F5 + number combination state
f5_number_buffer = ""
f5_held = False


def handle_f5_press(key):
    global f5_held
    f5_held = True


def handle_f5_release(key):
    global f5_held, f5_number_buffer
    if f5_held and f5_number_buffer:
        try:
            line_number = int(f5_number_buffer)
            title_page.set_specific_splash(line_number)
        except ValueError:
            pass  # Invalid number, ignore
    f5_held = False
    f5_number_buffer = ""


def handle_number_key(key):
    global f5_held, f5_number_buffer
    if f5_held:
        # Map pygame key codes to numbers
        number_map = {
            pygame.K_0: "0",
            pygame.K_1: "1",
            pygame.K_2: "2",
            pygame.K_3: "3",
            pygame.K_4: "4",
            pygame.K_5: "5",
            pygame.K_6: "6",
            pygame.K_7: "7",
            pygame.K_8: "8",
            pygame.K_9: "9",
            pygame.K_KP0: "0",
            pygame.K_KP1: "1",
            pygame.K_KP2: "2",
            pygame.K_KP3: "3",
            pygame.K_KP4: "4",
            pygame.K_KP5: "5",
            pygame.K_KP6: "6",
            pygame.K_KP7: "7",
            pygame.K_KP8: "8",
            pygame.K_KP9: "9",
        }
        if key in number_map:
            f5_number_buffer += number_map[key]


input_manager.on_key_press(
    pygame.K_ESCAPE, lambda key: pygame.event.post(pygame.event.Event(pygame.QUIT))
)
input_manager.on_key_press(pygame.K_F3, lambda key: globals().update(debug=not debug))
input_manager.on_key_press(pygame.K_F4, lambda key: title_page.refresh_splash())
input_manager.on_key_press(pygame.K_F5, handle_f5_press)
input_manager.on_key_release(pygame.K_F5, handle_f5_release)

# Register number key handlers
for number_key in [
    pygame.K_0,
    pygame.K_1,
    pygame.K_2,
    pygame.K_3,
    pygame.K_4,
    pygame.K_5,
    pygame.K_6,
    pygame.K_7,
    pygame.K_8,
    pygame.K_9,
    pygame.K_KP0,
    pygame.K_KP1,
    pygame.K_KP2,
    pygame.K_KP3,
    pygame.K_KP4,
    pygame.K_KP5,
    pygame.K_KP6,
    pygame.K_KP7,
    pygame.K_KP8,
    pygame.K_KP9,
]:
    input_manager.on_key_press(number_key, handle_number_key)

# Clock for FPS
clock = pygame.time.Clock()

# FPS tracking
fps_history = deque()
last_time = time.time()

# UI variables
ui_scale = 1

# Main loop
running = True
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            input_manager.handle_event(event)

        screen.fill((255, 255, 255))  # White background

        # Render current page
        page_manager.render_current_page(screen, font, loaded_tiles, ui_scale)

        # FPS tracking (always enabled)
        current_time = time.time()
        current_fps = clock.get_fps()
        fps_history.append((current_time, current_fps))

        # Keep only FPS data from the last second
        while fps_history and current_time - fps_history[0][0] > 1.0:
            fps_history.popleft()

        # FPS display (only if debug is enabled)
        if debug:
            # Calculate stats and render FPS text
            if fps_history:
                fps_values = [fps for _, fps in fps_history if fps > 0]
                if fps_values:
                    avg_fps = sum(fps_values) / len(fps_values)
                    min_fps = min(fps_values)
                    max_fps = max(fps_values)

                    # Draw white background box for readability
                    pygame.draw.rect(screen, (255, 255, 255), (width - 75, 5, 70, 50))

                    # Render each FPS stat on separate lines
                    render_text(
                        screen,
                        f"FPS: {current_fps:.1f}",
                        font,
                        (width - 65, 10),
                        scale=ui_scale,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Avg: {avg_fps:.1f}",
                        font,
                        (width - 65, 20),
                        scale=ui_scale,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Min: {min_fps:.1f}",
                        font,
                        (width - 65, 30),
                        scale=ui_scale,
                        color=(0, 0, 0),
                    )
                    render_text(
                        screen,
                        f"Max: {max_fps:.1f}",
                        font,
                        (width - 65, 40),
                        scale=ui_scale,
                        color=(0, 0, 0),
                    )
                else:
                    # Draw white background box for readability
                    pygame.draw.rect(screen, (255, 255, 255), (width - 75, 5, 70, 15))

                    render_text(
                        screen,
                        f"FPS: {current_fps:.1f}",
                        font,
                        (width - 65, 10),
                        scale=ui_scale,
                        color=(0, 0, 0),
                    )
            else:
                # Draw white background box for readability
                pygame.draw.rect(screen, (255, 255, 255), (width - 130, 5, 125, 15))

                render_text(
                    screen,
                    f"FPS: {current_fps:.1f}",
                    font,
                    (width - 120, 10),
                    scale=ui_scale,
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
