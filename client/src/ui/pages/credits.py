import pygame
import os
import time
import re
from typing import Optional

from client.src.renderer.text import render_text
from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile
from client.src.ui.page import Page
from client.src.constants import *


class Credits(Page):
    def __init__(self, current_version: Optional[str] = None):
        super().__init__(
            "credits", always_reinitialize=True, reinit_callback=self.page_init
        )

        self.current_version = current_version

    def page_init(self):
        # Load credits text
        self.credits_lines = []
        credits_file = os.path.join("client", "assets", "texts", "credits.txt")
        try:
            with open(credits_file, "r", encoding="utf-8") as f:
                version = f" ({self.current_version})" if self.current_version else ""
                self.credits_lines = [
                    line.rstrip().replace("&VERSION", version) for line in f.readlines()
                ]
                self.credits_lines.reverse()  # Reverse for bottom-up rendering
        except FileNotFoundError:
            self.credits_lines = ["Credits file not found!"]

        # Animation state
        self.scroll_offset = 0
        self.start_time = time.time()
        self.scroll_speed = CREDITS_SCROLL_SPEED  # pixels per second

        # Credits configuration
        self.line_height = 20  # pixels between lines
        self.section_spacing = 35  # extra spacing for section breaks

        # Performance optimization: pre-parse all lines
        self.parsed_lines = []
        for line in self.credits_lines:
            if line.strip():
                self.parsed_lines.append(
                    self._parse_color_tags(line, 1.0)
                )  # Parse with base scale
            else:
                self.parsed_lines.append([])  # Empty line

        # Cache for width calculations with size limit
        self.width_cache = {}
        self.surface_cache = {}  # Cache for pre-rendered text surfaces
        self.position_cache = {}  # Cache for line positions
        self.max_cache_size = 1000

        # Track current UI scale to detect changes
        self._last_ui_scale = None

        # Pre-calculate relative line positions (constant offsets)
        self._line_offsets = []
        current_offset = 0
        for parsed_segments in self.parsed_lines:
            self._line_offsets.append(current_offset)
            if not parsed_segments:  # Empty line
                current_offset += self.section_spacing
            else:
                current_offset += self.line_height

    def _clear_caches_if_needed(self, ui_scale):
        if (
            self._last_ui_scale != ui_scale
            or len(self.width_cache) > self.max_cache_size
        ):
            self.width_cache.clear()
            self.surface_cache.clear()
            self.position_cache.clear()
            self._last_ui_scale = ui_scale

    def _parse_color_tags(self, line, base_scale):
        # Color mapping
        color_map = {
            "gold": (255, 215, 0),
            "blue": (100, 200, 255),
            "grey": (160, 160, 160),
            "green": (100, 255, 100),
            "red": (255, 100, 100),
            "purple": (200, 100, 255),
            "yellow": (255, 255, 100),
        }

        segments = []
        current_pos = 0
        default_color = (255, 255, 255)  # White
        default_base_scale = base_scale

        # Find all color tags
        pattern = r"<(gold|blue|grey|green|red|purple|yellow)>(.*?)</\1>"
        matches = list(re.finditer(pattern, line))

        for match in matches:
            # Add text before the tag as default color
            if match.start() > current_pos:
                text_before = line[current_pos : match.start()]
                if text_before:
                    segments.append(
                        {
                            "text": text_before,
                            "color": default_color,
                            "base_scale": default_base_scale,
                        }
                    )

            # Add the colored text
            color_name = match.group(1)
            text_content = match.group(2)
            color = color_map.get(color_name, default_color)

            # Special scaling for different text types
            if text_content.lower() == "dashr":
                base_scale = 7.0
            elif text_content.lower() == "- proplayer919":
                base_scale = 3.0
            elif color_name == "gold":
                base_scale = 4.0
            else:
                base_scale = 2.0

            segments.append(
                {"text": text_content, "color": color, "base_scale": base_scale}
            )

            current_pos = match.end()

        # Add remaining text after last tag
        if current_pos < len(line):
            remaining_text = line[current_pos:]
            if remaining_text:
                segments.append(
                    {
                        "text": remaining_text,
                        "color": default_color,
                        "base_scale": default_base_scale,
                    }
                )

        # If no tags found, return the whole line as default
        if not segments:
            segments.append(
                {"text": line, "color": default_color, "base_scale": default_base_scale}
            )

        return segments

    def _get_or_create_surface(self, text, font, scale, color):
        cache_key = (text, scale, color)
        if cache_key not in self.surface_cache:
            # Create a temporary surface to render text on
            temp_width = font.get_text_width(text, scale)
            temp_height = int(font.size * scale)
            if temp_width <= 0 or temp_height <= 0:
                return None

            temp_surface = pygame.Surface((temp_width, temp_height), pygame.SRCALPHA)
            render_text(temp_surface, text, font, (0, 0), scale, color)
            self.surface_cache[cache_key] = temp_surface

        return self.surface_cache[cache_key]

    def _get_visible_line_range(
        self, start_y, scroll_offset, screen_height, ui_scale, visibility_margin
    ):
        if len(self._line_offsets) < 50:  # Use simple iteration for small lists
            return 0, len(self._line_offsets)

        # Binary search for first visible line
        first_visible = 0
        last_visible = len(self._line_offsets)

        for i, offset in enumerate(self._line_offsets):
            line_y = start_y - (offset * ui_scale) - scroll_offset
            if line_y < screen_height + visibility_margin:
                if line_y > -visibility_margin:
                    if first_visible == 0:
                        first_visible = max(0, i - 5)  # Small buffer
                else:
                    last_visible = min(len(self._line_offsets), i + 5)  # Small buffer
                    break

        return first_visible, last_visible

    def render(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        # Clear caches if needed
        self._clear_caches_if_needed(ui_scale)

        # Clear screen with black background
        screen.fill((0, 0, 0))

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Update scroll animation
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.scroll_offset = elapsed_time * self.scroll_speed * ui_scale

        # Calculate starting Y position
        start_y = screen_height + (30 * len(self.credits_lines)) * ui_scale
        visibility_margin = 200

        # Get visible line range for culling
        first_visible, last_visible = self._get_visible_line_range(
            start_y, self.scroll_offset, screen_height, ui_scale, visibility_margin
        )

        # Batch surface blits for better performance
        blit_operations = []

        # Render visible lines only
        for i in range(first_visible, last_visible):
            if i >= len(self.parsed_lines):
                break

            parsed_segments = self.parsed_lines[i]
            if not parsed_segments:  # Empty line
                continue

            # Calculate Y position using pre-calculated offsets
            text_y = start_y - (self._line_offsets[i] * ui_scale) - self.scroll_offset

            # Final visibility check
            if (
                text_y < -visibility_margin
                or text_y > screen_height + visibility_margin
            ):
                continue

            # Use cached width calculation
            cache_key = (i, ui_scale)
            if cache_key in self.width_cache:
                total_width = self.width_cache[cache_key]
            else:
                total_width = sum(
                    font.get_text_width(seg["text"], seg["base_scale"] * ui_scale)
                    for seg in parsed_segments
                )
                self.width_cache[cache_key] = total_width

            start_x = screen_width // 2 - total_width // 2
            current_x = start_x

            # Prepare surfaces for this line
            for segment in parsed_segments:
                if segment["text"]:
                    scale = segment["base_scale"] * ui_scale
                    surface = self._get_or_create_surface(
                        segment["text"], font, scale, segment["color"]
                    )

                    if surface:
                        blit_operations.append((surface, (current_x, text_y)))

                    current_x += font.get_text_width(segment["text"], scale) + (
                        2 * ui_scale
                    )

        # Batch blit all surfaces at once
        screen.blits(blit_operations)

        # Cache instruction surface and position
        instruction_cache_key = f"instruction_{ui_scale}"
        if instruction_cache_key not in self.position_cache:
            instruction_text = "Press F9/ESC to return to title"
            instruction_color = (128, 128, 128)
            instruction_scale = ui_scale * 1

            instruction_surface = self._get_or_create_surface(
                instruction_text, font, instruction_scale, instruction_color
            )

            if instruction_surface:
                instruction_width = instruction_surface.get_width()
                instruction_x = screen_width // 2 - instruction_width // 2
                instruction_y = screen_height - 30 * ui_scale

                self.position_cache[instruction_cache_key] = {
                    "surface": instruction_surface,
                    "pos": (instruction_x, instruction_y),
                }

        # Render cached instruction
        if instruction_cache_key in self.position_cache:
            cached_instruction = self.position_cache[instruction_cache_key]
            screen.blit(cached_instruction["surface"], cached_instruction["pos"])
