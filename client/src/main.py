import os
import time
from collections import deque

import pygame

from client.src.asset.font.font_loader import FontLoader
from client.src.asset.tile.tile_loader import TileLoader
from client.src.input.manager import InputManager
from client.src.renderer.text import render_text
from client.src.ui.page_manager import PageManager
from client.src.ui.pages.title import Title


class DashrGame:
    # Constants
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 480
    DEFAULT_UI_SCALE = 1
    BACKGROUND_COLOR = (255, 255, 255)
    DEBUG_BOX_COLOR = (255, 255, 255)
    DEBUG_TEXT_COLOR = (0, 0, 0)

    # Number key mappings for F5 combinations
    NUMBER_KEY_MAP = {
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

    def __init__(self):
        self.debug = False
        self.running = False
        self.ui_scale = self.DEFAULT_UI_SCALE

        # F5 combination state
        self.f5_number_buffer = ""
        self.f5_held = False

        # FPS tracking
        self.fps_history = deque()

        # Initialize pygame and create components
        self._initialize_pygame()
        self._load_assets()
        self._setup_ui()
        self._setup_input()

        # Game clock
        self.clock = pygame.time.Clock()

    def _initialize_pygame(self):
        # Set window properties before initializing pygame
        os.environ["SDL_VIDEO_X11_WMCLASS"] = "Dashr"
        os.environ["SDL_VIDEO_WINDOW_POS"] = "SDL_WINDOWPOS_CENTERED"

        # Initialize pygame
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        # Set up display
        self.width, self.height = self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT
        self.screen = pygame.display.set_mode(size=(self.width, self.height))
        pygame.display.set_caption("Dashr Demo")

        # Set window icon
        self._set_window_icon()

    def _set_window_icon(self):
        icon_path = os.path.join("client", "icons", "current.png")
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path).convert()
            pygame.display.set_icon(icon)

    def _load_assets(self):
        # Load font
        font_dir = os.path.join("client", "assets", "font")
        self.font = FontLoader.load_font_from_directory(font_dir)

        # Load tiles
        tiles_dir = os.path.join("client", "assets", "textures", "tiles", "default")
        self.loaded_tiles = TileLoader.load_tiles_from_directory(tiles_dir)

    def _setup_ui(self):
        self.page_manager = PageManager()
        self.title_page = Title()
        self.page_manager.set_page(self.title_page)

    def _setup_input(self):
        self.input_manager = InputManager()
        self.input_manager.start()

        # Register key handlers
        self._register_function_keys()
        self._register_number_keys()

    def _register_function_keys(self):
        self.input_manager.on_key_press(
            pygame.K_ESCAPE,
            lambda key: pygame.event.post(pygame.event.Event(pygame.QUIT)),
        )
        self.input_manager.on_key_press(pygame.K_F2, self._handle_screenshot_key)
        self.input_manager.on_key_press(pygame.K_F3, self._handle_debug_toggle_key)
        self.input_manager.on_key_press(pygame.K_F4, self._handle_splash_refresh_key)
        self.input_manager.on_key_press(pygame.K_F5, self._handle_f5_press)
        self.input_manager.on_key_release(pygame.K_F5, self._handle_f5_release)

    def _register_number_keys(self):
        for number_key in self.NUMBER_KEY_MAP.keys():
            self.input_manager.on_key_press(number_key, self._handle_number_key)

    def _handle_screenshot_key(self, key):
        self._take_screenshot()

    def _handle_debug_toggle_key(self, key):
        self.debug = not self.debug

    def _handle_splash_refresh_key(self, key):
        self.title_page.refresh_splash()

    def _handle_f5_press(self, key):
        self.f5_held = True

    def _handle_f5_release(self, key):
        if self.f5_held and self.f5_number_buffer:
            try:
                line_number = int(self.f5_number_buffer)
                self.title_page.set_specific_splash(line_number)
            except ValueError:
                pass  # Invalid number, ignore
        self.f5_held = False
        self.f5_number_buffer = ""

    def _handle_number_key(self, key):
        if self.f5_held and key in self.NUMBER_KEY_MAP:
            self.f5_number_buffer += self.NUMBER_KEY_MAP[key]

    def _take_screenshot(self):
        screenshots_dir = os.path.expanduser(
            os.path.join("~", "dashr-data", "screenshots")
        )
        os.makedirs(screenshots_dir, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")

        try:
            pygame.image.save(self.screen, screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            print(f"Failed to save screenshot: {e}")

    def _update_fps_tracking(self):
        current_time = time.time()
        current_fps = self.clock.get_fps()
        self.fps_history.append((current_time, current_fps))

        # Keep only FPS data from the last second
        while self.fps_history and current_time - self.fps_history[0][0] > 1.0:
            self.fps_history.popleft()

    def _render_fps_debug(self):
        if not self.debug or not self.fps_history:
            return

        current_fps = self.clock.get_fps()
        fps_values = [fps for _, fps in self.fps_history if fps > 0]

        if fps_values:
            avg_fps = sum(fps_values) / len(fps_values)
            min_fps = min(fps_values)
            max_fps = max(fps_values)

            # Draw background box for multi-line stats
            pygame.draw.rect(
                self.screen, self.DEBUG_BOX_COLOR, (self.width - 75, 5, 70, 50)
            )

            # Render FPS statistics
            stats = [
                f"FPS: {current_fps:.1f}",
                f"Avg: {avg_fps:.1f}",
                f"Min: {min_fps:.1f}",
                f"Max: {max_fps:.1f}",
            ]

            for i, stat in enumerate(stats):
                render_text(
                    self.screen,
                    stat,
                    self.font,
                    (self.width - 65, 10 + i * 10),
                    scale=self.ui_scale,
                    color=self.DEBUG_TEXT_COLOR,
                )
        else:
            # Single line FPS display
            pygame.draw.rect(
                self.screen, self.DEBUG_BOX_COLOR, (self.width - 130, 5, 125, 15)
            )
            render_text(
                self.screen,
                f"FPS: {current_fps:.1f}",
                self.font,
                (self.width - 120, 10),
                scale=self.ui_scale,
                color=self.DEBUG_TEXT_COLOR,
            )

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.input_manager.handle_event(event)

    def _update(self):
        self._update_fps_tracking()

    def _render(self):
        # Clear screen
        self.screen.fill(self.BACKGROUND_COLOR)

        # Render current page
        self.page_manager.render_current_page(
            self.screen, self.font, self.loaded_tiles, self.ui_scale
        )

        # Render debug information
        self._render_fps_debug()

        # Update display
        pygame.display.flip()

    def run(self):
        self.running = True

        try:
            while self.running:
                self._handle_events()
                self._update()
                self._render()
                self.clock.tick()

        except KeyboardInterrupt:
            print("\nReceived interrupt, exiting...")
            self.running = False

        finally:
            self._cleanup()

    def _cleanup(self):
        self.input_manager.stop()
        pygame.quit()


def main():
    game = DashrGame()
    game.run()


if __name__ == "__main__":
    main()
