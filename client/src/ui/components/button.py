import pygame
from typing import Tuple, Optional, Callable
from enum import Enum

from client.src.ui.core import UIComponent, UIEvent, UIColors, UIConstants
from client.src.asset.font.font import Font
from client.src.renderer.text import render_text


class ButtonState(Enum):
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"


class Button(UIComponent):
    """Interactive button component"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = "",
        background_color: Tuple[int, int, int] = UIColors.BUTTON_NORMAL,
        hover_color: Tuple[int, int, int] = UIColors.BUTTON_HOVER,
        pressed_color: Tuple[int, int, int] = UIColors.BUTTON_PRESSED,
        disabled_color: Tuple[int, int, int] = UIColors.BUTTON_DISABLED,
        text_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        border_color: Tuple[int, int, int] = UIColors.BORDER,
        border_width: int = UIConstants.DEFAULT_BORDER_WIDTH,
        font_scale: int = UIConstants.DEFAULT_FONT_SCALE,
        on_click: Optional[Callable] = None,
    ):
        super().__init__(x, y, width, height)
        self.text = text
        self.background_color = background_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.disabled_color = disabled_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.font_scale = font_scale

        self.state = ButtonState.NORMAL
        self.is_pressed = False

        if on_click:
            self.add_event_handler("click", on_click)

    def set_text(self, text: str):
        """Update button text"""
        self.text = text

    def set_enabled(self, enabled: bool):
        """Enable or disable the button"""
        self.enabled = enabled
        if not enabled:
            self.state = ButtonState.DISABLED
        else:
            self.state = ButtonState.NORMAL

    def get_current_color(self) -> Tuple[int, int, int]:
        """Get the current background color based on state"""
        if not self.enabled:
            return self.disabled_color
        elif self.state == ButtonState.PRESSED:
            return self.pressed_color
        elif self.state == ButtonState.HOVER:
            return self.hover_color
        else:
            return self.background_color

    def update(self, dt: float):
        if not self.visible:
            return

        # Update state based on mouse position
        if self.enabled:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            if self.contains_point(mouse_pos):
                if mouse_pressed and not self.is_pressed:
                    self.state = ButtonState.PRESSED
                    self.is_pressed = True
                elif mouse_pressed and self.is_pressed:
                    self.state = ButtonState.PRESSED
                elif not mouse_pressed and self.is_pressed:
                    # Button was released over the button - trigger click
                    self.state = ButtonState.HOVER
                    self.is_pressed = False
                    self.trigger_event(UIEvent("click", self))
                else:
                    self.state = ButtonState.HOVER
                    self.is_pressed = False
            else:
                if mouse_pressed and self.is_pressed:
                    # Mouse dragged outside button while pressed
                    self.state = ButtonState.NORMAL
                elif not mouse_pressed:
                    self.state = ButtonState.NORMAL
                    self.is_pressed = False

        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, self.width, self.height)

        # Draw background
        current_color = self.get_current_color()
        pygame.draw.rect(surface, current_color, rect)

        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, rect, self.border_width)

        # Draw text centered
        if self.text and font:
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED

            # Calculate text position to center it
            # We'll estimate text size - this is approximate since we don't have exact metrics
            char_width = font.size * self.font_scale
            text_width = (
                len(self.text) * char_width + (len(self.text) - 1) * 2 * self.font_scale
            )  # 2px spacing
            text_height = font.size * self.font_scale

            text_x = abs_x + (self.width - text_width) // 2
            text_y = abs_y + (self.height - text_height) // 2

            render_text(
                surface,
                self.text,
                font,
                (text_x, text_y),
                scale=self.font_scale,
                color=text_color,
            )

        # Render children
        super().render(surface, font)

    def _handle_event_internal(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(event.pos):  # Left click
                self.is_pressed = True
                self.state = ButtonState.PRESSED
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:  # Left click release
                self.is_pressed = False
                if self.contains_point(event.pos):
                    self.state = ButtonState.HOVER
                    self.trigger_event(UIEvent("click", self))
                else:
                    self.state = ButtonState.NORMAL
                return True

        return False


class IconButton(Button):
    """Button that can display an icon alongside or instead of text"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        icon_surface: Optional[pygame.Surface] = None,
        text: str = "",
        **kwargs
    ):
        super().__init__(x, y, width, height, text, **kwargs)
        self.icon_surface = icon_surface
        self.icon_padding = 4

    def set_icon(self, icon_surface: pygame.Surface):
        """Set the icon surface"""
        self.icon_surface = icon_surface

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, self.width, self.height)

        # Draw background
        current_color = self.get_current_color()
        pygame.draw.rect(surface, current_color, rect)

        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, rect, self.border_width)

        # Calculate layout for icon and text
        content_x = abs_x + self.icon_padding
        content_y = (
            abs_y
            + (
                self.height
                - (self.icon_surface.get_height() if self.icon_surface else 0)
            )
            // 2
        )

        # Draw icon
        if self.icon_surface:
            if not self.enabled:
                # Create a darkened version of the icon for disabled state
                darkened_icon = self.icon_surface.copy()
                darkened_icon.fill((128, 128, 128), special_flags=pygame.BLEND_MULT)
                surface.blit(darkened_icon, (content_x, content_y))
            else:
                surface.blit(self.icon_surface, (content_x, content_y))
            content_x += self.icon_surface.get_width() + self.icon_padding

        # Draw text
        if self.text and font:
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED
            text_y = abs_y + (self.height - font.size * self.font_scale) // 2

            render_text(
                surface,
                self.text,
                font,
                (content_x, text_y),
                scale=self.font_scale,
                color=text_color,
            )

        # Render children (skip Button's render to avoid double-rendering background)
        for child in self.children:
            child.render(surface, font)
