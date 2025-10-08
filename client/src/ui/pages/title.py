import pygame
import math
import time
import os
from typing import Optional, Callable

from client.src.utils.splash_picker import pick_a_splash_any_splash, get_specific_splash
from client.src.renderer.text import render_text
from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile
from client.src.ui.page import Page
from client.src.ui.components.button import Button
from client.src.constants import *


class Title(Page):
    def __init__(
        self,
        no_splash_effect: bool = False,
        button_callbacks: Optional[dict[str, Callable]] = None,
    ):
        super().__init__("title")

        self.splash: str = pick_a_splash_any_splash()
        self.no_splash_effect = no_splash_effect
        self.animation_start_time = time.time()

        # Load the parallax background image
        self.background_image = pygame.image.load(
            os.path.join("client", "assets", "ui", "backgrounds", "title_bg.png")
        ).convert()

        # Cache for rendered text surfaces to avoid recalculating every frame
        self._cached_title_surface = None
        self._cached_subtitle_surface = None
        self._last_ui_scale = None

        # Cache for scaled background image
        self._cached_background_surface = None
        self._last_screen_dimensions = None

        # Cache for instruction text
        self._cached_instruction_surface = None

        # Initialize buttons
        self.buttons = []
        self._setup_buttons(button_callbacks or {})

    def _setup_buttons(self, button_callbacks: dict[str, Callable]):
        # Button dimensions and spacing
        button_width = 175
        button_height = 40
        button_spacing = 30

        # Button labels
        button_labels = ["Play", "Create", "Settings"]

        # Create buttons (positions will be calculated in render method)
        for i, label in enumerate(button_labels):
            callback = button_callbacks.get(label.lower())
            button = Button(
                text=label,
                position=(0, 0),  # Will be set during rendering
                width=button_width,
                height=button_height,
                on_click=callback,
                font_scale=3.0,
                background_color=(40, 40, 50),
                hover_color=(60, 60, 70),
                text_color=(255, 255, 255),
                border_color=(100, 100, 120),
            )
            self.buttons.append(button)

    def refresh_splash(self):
        self.splash = pick_a_splash_any_splash()

    def set_specific_splash(self, line_number: int):
        splash = get_specific_splash(line_number)
        if splash is not None:
            self.splash = splash

    def _clear_text_cache(self):
        self._cached_title_surface = None
        self._cached_subtitle_surface = None
        self._cached_instruction_surface = None

    def _clear_background_cache(self):
        self._cached_background_surface = None
        self._last_screen_dimensions = None

    def update_buttons(self, cursor_pos: tuple[int, int], ui_scale: int):
        for button in self.buttons:
            button.update(cursor_pos, ui_scale)

    def handle_click(self, click_pos: tuple[int, int], button_no: int):
        if button_no == 1:
            for button in self.buttons:
                button.handle_click(click_pos, self._last_ui_scale or 1)

    def _update_button_positions(
        self,
        screen_width: int,
        screen_height: int,
        ui_scale: int,
        subtitle_y: float,
        subtitle_height: float,
    ):
        if not self.buttons:
            return

        button_spacing = 15 * ui_scale
        total_buttons = len(self.buttons)

        # Calculate starting Y position (below subtitle + space for splash text + padding)
        # Use maximum splash scale to ensure buttons don't shift during animation
        max_splash_scale = ui_scale * SPLASH_MAX
        max_splash_height = 8 * max_splash_scale  # font.size is 8 pixels
        splash_padding = 10 * ui_scale
        button_padding = 50 * ui_scale

        buttons_start_y = (
            subtitle_y
            + subtitle_height
            + splash_padding
            + max_splash_height
            + button_padding
        )

        # Calculate total height needed for all buttons
        button_height = self.buttons[0].height * ui_scale
        total_height = (total_buttons * button_height) + (
            (total_buttons - 1) * button_spacing
        )

        # Center the buttons vertically in the remaining space
        available_space = (
            screen_height - buttons_start_y - (60 * ui_scale)
        )  # Leave space for instruction text
        if total_height < available_space:
            buttons_start_y += (
                available_space - total_height
            ) // 3  # Position in upper third of available space

        # Position each button
        for i, button in enumerate(self.buttons):
            button_x = screen_width // 2
            button_y = buttons_start_y + i * (button_height + button_spacing)
            button.position = (button_x, button_y)

    def render(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        screen.fill((0, 0, 0))

        screen_width = screen.get_width()
        screen_height = screen.get_height()
        current_screen_dimensions = (screen_width, screen_height)

        # Cache scaled background if screen dimensions changed
        if (
            self._last_screen_dimensions != current_screen_dimensions
            or self._cached_background_surface is None
        ):
            self._last_screen_dimensions = current_screen_dimensions
            self._cached_background_surface = pygame.transform.smoothscale(
                self.background_image, current_screen_dimensions
            )

        screen.blit(self._cached_background_surface, (0, 0))

        # Cache title and subtitle surfaces if UI scale changed
        if self._last_ui_scale != ui_scale:
            self._last_ui_scale = ui_scale
            self._cached_title_surface = None
            self._cached_subtitle_surface = None
            self._cached_instruction_surface = None

        # Calculate text dimensions for proper centering
        title_scale = ui_scale * TITLE_EXTRA_SCALE
        subtitle_scale = ui_scale * SUBTITLE_EXTRA_SCALE

        # Render title - use cached surface if available
        title_text = "<icon:logo> Dashr"
        title_color = TITLE_COLOR
        title_width = int(font.get_text_width(title_text, title_scale))
        title_position = (screen_width // 2 - title_width // 2, screen_height // 10)

        if self._cached_title_surface is None:
            # Create a surface for the title text
            title_surface = pygame.Surface(
                (title_width + 20, int(font.size * title_scale) + 10), pygame.SRCALPHA
            )
            render_text(
                title_surface, title_text, font, (10, 5), title_scale, title_color
            )
            self._cached_title_surface = title_surface

        screen.blit(
            self._cached_title_surface, (title_position[0] - 10, title_position[1] - 5)
        )

        # Render subtitle - use cached surface if available
        subtitle_text = "Demo Edition"
        subtitle_color = SUBTITLE_COLOR
        subtitle_width = int(font.get_text_width(subtitle_text, subtitle_scale))
        subtitle_x = (screen_width // 2 - subtitle_width // 2) + (37 * ui_scale)
        subtitle_y = title_position[1] + (font.size * title_scale) + (-5 * ui_scale)
        subtitle_position = (subtitle_x, subtitle_y)

        if self._cached_subtitle_surface is None:
            # Create a surface for the subtitle text
            subtitle_surface = pygame.Surface(
                (subtitle_width + 20, int(font.size * subtitle_scale) + 10),
                pygame.SRCALPHA,
            )
            render_text(
                subtitle_surface,
                subtitle_text,
                font,
                (10, 5),
                subtitle_scale,
                subtitle_color,
            )
            self._cached_subtitle_surface = subtitle_surface

        screen.blit(
            self._cached_subtitle_surface,
            (subtitle_position[0] - 10, subtitle_position[1] - 5),
        )

        # Calculate animated splash scale (only recalculate when needed)
        if self.no_splash_effect:
            splash_scale = ui_scale * SPLASH_EXTRA_SCALE
        else:
            # Create a smooth oscillation - quantize time to reduce calculations
            current_time = time.time()
            quantized_time = int(current_time * 30) / 30  # Update 30 times per second
            elapsed = quantized_time - self.animation_start_time
            # Use sine wave for smooth animation, complete cycle every SPLASH_ANIMATION_SPEED seconds
            animation_progress = (
                math.sin(elapsed * math.pi / SPLASH_ANIMATION_SPEED) + 1
            ) / 2  # 0 to 1
            splash_scale = (ui_scale * SPLASH_MIN) + (
                ui_scale * (SPLASH_MAX - SPLASH_MIN) * animation_progress
            )

        # Render splash text - this needs to animate so can't be cached
        splash_text = self.splash
        splash_color = SPLASH_COLOR
        splash_width = font.get_text_width(splash_text, splash_scale)
        splash_y = subtitle_position[1] + (font.size * subtitle_scale) + (10 * ui_scale)
        splash_position = (screen_width / 2 - splash_width / 2, splash_y)
        render_text(
            screen, splash_text, font, splash_position, splash_scale, splash_color
        )

        # Update and render menu buttons (use fixed position to prevent shifting)
        self._update_button_positions(
            screen_width,
            screen_height,
            ui_scale,
            subtitle_position[1],
            font.size * subtitle_scale,
        )
        self.update_buttons(cursor_pos, ui_scale)

        for button in self.buttons:
            button.render(screen, font, ui_scale)

        # Render instruction text - use cached surface if available
        instruction_text = "Press F9 to open credits"
        instruction_color = (255, 255, 255)
        instruction_scale = ui_scale * 1
        instruction_width = int(
            font.get_text_width(instruction_text, instruction_scale)
        )
        instruction_x = screen_width // 2 - instruction_width // 2
        instruction_y = screen_height - 30 * ui_scale
        instruction_position = (instruction_x, instruction_y)

        if self._cached_instruction_surface is None:
            # Create a surface for the instruction text
            instruction_surface = pygame.Surface(
                (instruction_width + 20, int(font.size * instruction_scale) + 10),
                pygame.SRCALPHA,
            )
            render_text(
                instruction_surface,
                instruction_text,
                font,
                (10, 5),
                instruction_scale,
                instruction_color,
            )
            self._cached_instruction_surface = instruction_surface

        screen.blit(
            self._cached_instruction_surface,
            (instruction_position[0] - 10, instruction_position[1] - 5),
        )
