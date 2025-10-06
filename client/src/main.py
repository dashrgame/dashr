import os
import sys
import time
from collections import deque
import threading

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from client.src.asset.font.font_loader import FontLoader
from client.src.asset.tile.tile_loader import TileLoader
from client.src.input.manager import InputManager
from client.src.renderer.text import render_text
from client.src.ui.page_manager import PageManager
from client.src.ui.pages.title import Title
from client.src.update.version import (
    get_version_number_github,
    get_version_number_local,
)
from client.src.update import autoupdate
from client.src.constants import *


class DashrGame:
    def __init__(self):
        self.debug = False
        self.running = False
        self.ui_scale = UI_SCALE

        # F5 combination state
        self.f5_number_buffer = ""
        self.f5_held = False

        # FPS tracking
        self.fps_history = deque()

        # Cursor position
        self.cursor_pos = (0, 0)

        # Initialize pygame and create components
        self._initialize_pygame()
        self._load_assets()
        self._setup_ui()
        self._setup_input()

        # Game clock
        self.clock = pygame.time.Clock()

        # Get version number
        def get_versions():
            try:
                self.current_version = get_version_number_local(".")
            except Exception as e:
                print(f"Failed to get version number: {e}")
                self.current_version = "unknown"

            try:
                self.upstream_version = get_version_number_github(UPSTREAM_REPO_URL)
            except Exception as e:
                print(f"Failed to get upstream version: {e}")
                self.upstream_version = "unknown"

        # Initialize versions to avoid attribute errors
        self.current_version = "loading..."
        self.upstream_version = "loading..."

        # Start version check in background thread
        version_thread = threading.Thread(target=get_versions, daemon=True)
        version_thread.start()

    def _initialize_pygame(self):
        # Set window properties before initializing pygame
        os.environ["SDL_VIDEO_X11_WMCLASS"] = "Dashr"
        os.environ["SDL_VIDEO_WINDOW_POS"] = "SDL_WINDOWPOS_CENTERED"

        # Initialize pygame
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        # Set up display
        self.width, self.height = DEFAULT_WIDTH, DEFAULT_HEIGHT
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.screen = pygame.display.set_mode(
            size=(self.width, self.height), flags=flags
        )
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
        for number_key in NUMBER_KEY_MAP.keys():
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
        if self.f5_held and key in NUMBER_KEY_MAP:
            self.f5_number_buffer += NUMBER_KEY_MAP[key]

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

    def _render_debug(self):
        if not self.debug:
            return

        current_fps = self.clock.get_fps()
        fps_values = [fps for _, fps in self.fps_history if fps > 0]

        # Calculate text dimensions based on UI scale
        line_height = 10 * self.ui_scale
        char_width = 6 * self.ui_scale  # Approximate character width
        margin = 5 * self.ui_scale

        if fps_values:
            avg_fps = sum(fps_values) / len(fps_values)
            min_fps = min(fps_values)
            max_fps = max(fps_values)

            # Prepare stats with version info
            stats = [
                f"- FPS: {current_fps:.1f}",
                f"| Avg: {avg_fps:.1f}",
                f"| Min: {min_fps:.1f}",
                f"| Max: {max_fps:.1f}",
                "",
                f"- Ver: {self.current_version}",
                f"| Up: {self.upstream_version}",
            ]
        else:
            # Fallback stats when no FPS history
            stats = [
                f"- FPS: {current_fps:.1f}",
                "",
                f"- Ver: {self.current_version}",
                f"| Up: {self.upstream_version}",
            ]

        # Calculate box dimensions based on content and scale
        max_text_width = max(len(stat) for stat in stats) * char_width
        box_width = max_text_width + (margin * 2)
        box_height = len(stats) * line_height + (margin * 2)

        # Position box in top-right corner with margin
        box_x = self.width - box_width - margin
        box_y = margin

        # Draw background box
        pygame.draw.rect(
            self.screen, DEBUG_BOX_COLOR, (box_x, box_y, box_width, box_height)
        )

        # Render all statistics
        for i, stat in enumerate(stats):
            text_x = box_x + margin
            text_y = box_y + margin + (i * line_height)
            render_text(
                self.screen,
                stat,
                self.font,
                (text_x, text_y),
                scale=self.ui_scale,
                color=DEBUG_TEXT_COLOR,
            )

    def _handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.cursor_pos = event.pos

        self.input_manager.handle_event(event)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self._handle_event(event)

    def _update(self):
        self._update_fps_tracking()

    def _render(self):
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)

        # Render current page
        self.page_manager.render_current_page(
            self.screen, self.font, self.loaded_tiles, self.cursor_pos, self.ui_scale
        )

        # Render debug information
        self._render_debug()

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
    should_always_restart = os.environ.get("DASHR_ALWAYS_RESTART", "false") == "true"

    try:
        result = autoupdate.run_autoupdate()

        if result or should_always_restart:
            print("Restarting application to apply updates...")
            install_dir = os.path.expanduser("~/dashr")
            if os.path.exists(install_dir):
                os.chdir(install_dir)

            # If should_always_restart is true, reset for the next run
            if should_always_restart:
                os.environ["DASHR_ALWAYS_RESTART"] = "false"

            os.execv(sys.executable, [sys.executable, "-m", "client.src.main"])
    except Exception as e:
        print(f"Autoupdate error: {e}")

    game = DashrGame()
    game.run()


if __name__ == "__main__":
    main()
