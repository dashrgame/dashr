import os
import sys
import time
import threading

from client.src.ui.components import button

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from client.src.asset.font.font_loader import FontLoader
from client.src.asset.tile.tile_loader import TileLoader
from client.src.input.manager import InputManager
from client.src.renderer.text import render_text
from client.src.ui.page_manager import PageManager
from client.src.ui.overlay_manager import OverlayManager
from client.src.ui.overlays.debug_overlay import DebugOverlay
from client.src.ui.pages.title import Title
from client.src.ui.pages.credits import Credits
from client.src.ui.pages.play import PlayPage
from client.src.ui.pages.create import CreatePage
from client.src.ui.pages.settings import SettingsPage
from client.src.update.version import (
    get_version_number_github,
    get_version_number_local,
)
from client.src.update import autoupdate
from client.src.constants import *


class DashrGame:
    def __init__(self):
        self.running = False
        self.ui_scale = UI_SCALE
        self.is_fullscreen = FULLSCREEN

        # F5 combination state
        self.f5_number_buffer = ""
        self.f5_held = False

        # Cursor position
        self.cursor_pos = (0, 0)

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

        # Initialize pygame and create components
        self._initialize_pygame()
        self._load_assets()
        self._setup_ui()
        self._setup_input()

    def _initialize_pygame(self):
        # Set window properties before initializing pygame
        os.environ["SDL_VIDEO_X11_WMCLASS"] = "Dashr"
        os.environ["SDL_VIDEO_WINDOW_POS"] = "SDL_WINDOWPOS_CENTERED"

        # Initialize pygame
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        # Set up display
        self.width, self.height = DEFAULT_WIDTH, DEFAULT_HEIGHT
        flags = (
            (pygame.FULLSCREEN if FULLSCREEN else 0)
            | pygame.RESIZABLE
            | pygame.HWSURFACE
            | pygame.DOUBLEBUF
        )
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
        # Initialize page manager
        self.page_manager = PageManager()

        # Initialize overlay manager
        self.overlay_manager = OverlayManager()

        # Setup pages
        self.play_page = PlayPage()
        self.create_page = CreatePage()
        self.settings_page = SettingsPage()
        self.credits_page = Credits(self.current_version)

        # Setup title page with button callbacks
        button_callbacks = {
            "play": lambda: self.page_manager.set_page(self.play_page),
            "create": lambda: self.page_manager.set_page(self.create_page),
            "settings": lambda: self.page_manager.set_page(self.settings_page),
        }
        self.title_page = Title(button_callbacks=button_callbacks)

        # Set the initial page
        self.page_manager.set_page(self.title_page)

        # Setup overlays
        self.debug_overlay = DebugOverlay(
            self.clock, self.current_version, self.upstream_version
        )
        self.overlay_manager.add_overlay(self.debug_overlay)

    def _setup_input(self):
        self.input_manager = InputManager()
        self.input_manager.start()

        # Register key handlers
        self._register_action_keys()
        self._register_number_keys()

    def _register_action_keys(self):
        self.input_manager.on_key_press(
            pygame.K_ESCAPE,
            lambda key: self._handle_escape_key(key),
        )
        self.input_manager.on_key_press(pygame.K_F2, self._handle_screenshot_key)

        self.input_manager.on_key_press(pygame.K_F4, self._handle_splash_refresh_key)
        self.input_manager.on_key_press(pygame.K_F5, self._handle_f5_press)
        self.input_manager.on_key_release(pygame.K_F5, self._handle_f5_release)
        self.input_manager.on_key_press(pygame.K_F9, self._handle_credits_key)
        self.input_manager.on_key_press(pygame.K_F11, self._handle_fullscreen_toggle)

    def _register_number_keys(self):
        for number_key in NUMBER_KEY_MAP.keys():
            self.input_manager.on_key_press(number_key, self._handle_number_key)

    def _handle_screenshot_key(self, key):
        self._take_screenshot()

    def _handle_splash_refresh_key(self, key):
        self.title_page.refresh_splash()

    def _handle_escape_key(self, key):
        current_page = self.page_manager.get_current_page()
        if current_page and current_page.id != "title":
            self.page_manager.go_back()
        else:
            self.running = False

    def _handle_credits_key(self, key):
        current_page = self.page_manager.get_current_page()
        if current_page and current_page.id == "credits":
            # If already on credits page, go back
            self.page_manager.go_back()
        else:
            # Switch to credits page
            self.page_manager.set_page(self.credits_page)

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

    def _handle_mouse_click(self, click_pos: tuple[int, int], button_no: int):
        self.page_manager.handle_click(click_pos, button_no)

    def _handle_fullscreen_toggle(self, key):
        # Toggle fullscreen state
        self.is_fullscreen = not self.is_fullscreen

        # Update UI scale based on fullscreen state
        if self.is_fullscreen:
            self.ui_scale = DEFAULT_FULLSCREEN_UI_SCALE
        else:
            self.ui_scale = DEFAULT_UI_SCALE

        # Recreate the display with new flags
        flags = (
            (pygame.FULLSCREEN if self.is_fullscreen else 0)
            | pygame.RESIZABLE
            | pygame.HWSURFACE
            | pygame.DOUBLEBUF
        )
        self.screen = pygame.display.set_mode(
            size=(self.width, self.height), flags=flags
        )

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

    def _handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.cursor_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos, event.button)
        elif event.type == pygame.KEYDOWN:
            # Handle overlay toggle keys
            self.overlay_manager.handle_key_press(event.key)

        self.input_manager.handle_event(event)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self._handle_event(event)

    def _update(self):
        # Update FPS tracking for FPS overlay
        self.debug_overlay.update_fps_tracking()

        # Update overlay versions in case they changed
        self.debug_overlay.set_versions(self.current_version, self.upstream_version)

    def _render(self):
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)

        # Render current page
        self.page_manager.render_current_page(
            self.screen, self.font, self.loaded_tiles, self.cursor_pos, self.ui_scale
        )

        # Render overlays
        self.overlay_manager.render_all(
            self.screen, self.font, self.loaded_tiles, self.cursor_pos, self.ui_scale
        )

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
