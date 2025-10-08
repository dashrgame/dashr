import pygame
from typing import Callable, Optional, Tuple
from client.src.renderer.text import render_text
from client.src.asset.font.font import Font


class Button:
    def __init__(
        self,
        text: str,
        position: tuple[float, float],
        width: int,
        height: int,
        on_click: Optional[Callable] = None,
        font_scale: float = 2.0,
        background_color: tuple[int, int, int] = (50, 50, 50),
        hover_color: tuple[int, int, int] = (70, 70, 70),
        text_color: tuple[int, int, int] = (255, 255, 255),
        border_color: tuple[int, int, int] = (100, 100, 100),
    ):
        self.text = text
        self.position = position
        self.width = width
        self.height = height
        self.on_click = on_click
        self.font_scale = font_scale

        # Colors
        self.background_color = background_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color

        # State
        self.is_hovered = False
        self.is_pressed = False

        # Cache
        self._cached_surface = None
        self._cached_hover_surface = None
        self._last_ui_scale = None

    def get_rect(self, ui_scale: int) -> pygame.Rect:
        x = self.position[0] - (self.width * ui_scale) // 2
        y = self.position[1] - (self.height * ui_scale) // 2
        return pygame.Rect(x, y, self.width * ui_scale, self.height * ui_scale)

    def is_point_inside(self, point: tuple[int, int], ui_scale: int) -> bool:
        rect = self.get_rect(ui_scale)
        return rect.collidepoint(point)

    def update(self, cursor_pos: tuple[int, int], ui_scale: int):
        self.is_hovered = self.is_point_inside(cursor_pos, ui_scale)

    def handle_click(self, click_pos: tuple[int, int], ui_scale: int) -> bool:
        if self.is_point_inside(click_pos, ui_scale):
            if self.on_click:
                self.on_click()
            return True
        return False

    def _create_button_surface(
        self, font: Font, ui_scale: int, hovered: bool
    ) -> pygame.Surface:
        scaled_width = self.width * ui_scale
        scaled_height = self.height * ui_scale

        # Create surface
        surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)

        # Choose colors based on hover state
        bg_color = self.hover_color if hovered else self.background_color

        # Draw background
        pygame.draw.rect(surface, bg_color, surface.get_rect())

        # Draw border
        pygame.draw.rect(
            surface,
            self.border_color,
            surface.get_rect(),
            width=2 * ui_scale,
        )

        # Calculate text position (centered)
        text_scale = self.font_scale * ui_scale
        text_width = font.get_text_width(self.text, text_scale)
        text_height = font.size * text_scale

        text_x = (scaled_width - text_width) / 2
        text_y = ((scaled_height - text_height) / 2) + (
            2 * ui_scale
        )  # Slightly adjust vertically

        # Render text
        render_text(
            surface, self.text, font, (text_x, text_y), text_scale, self.text_color
        )

        return surface

    def render(self, screen: pygame.Surface, font: Font, ui_scale: int):
        # Clear cache if UI scale changed
        if self._last_ui_scale != ui_scale:
            self._cached_surface = None
            self._cached_hover_surface = None
            self._last_ui_scale = ui_scale

        # Create cached surfaces if needed
        if self._cached_surface is None:
            self._cached_surface = self._create_button_surface(font, ui_scale, False)

        if self._cached_hover_surface is None:
            self._cached_hover_surface = self._create_button_surface(
                font, ui_scale, True
            )

        # Choose the appropriate surface
        surface = (
            self._cached_hover_surface if self.is_hovered else self._cached_surface
        )

        # Calculate position (button position is center, we need top-left for blitting)
        x = self.position[0] - (self.width * ui_scale) // 2
        y = self.position[1] - (self.height * ui_scale) // 2

        screen.blit(surface, (x, y))
