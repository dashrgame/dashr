import pygame
from typing import Tuple, Optional, Callable, Union

from client.src.ui.core import UIComponent, UIEvent, UIColors, UIConstants
from client.src.asset.font.font import Font
from client.src.renderer.text import render_text


class Slider(UIComponent):
    """Horizontal slider component for selecting numeric values"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = UIConstants.SLIDER_HEIGHT,
        min_value: Union[int, float] = 0,
        max_value: Union[int, float] = 100,
        value: Union[int, float] = 0,
        step: Union[int, float] = 1,
        background_color: Tuple[int, int, int] = UIColors.SURFACE,
        track_color: Tuple[int, int, int] = UIColors.BORDER,
        fill_color: Tuple[int, int, int] = UIColors.PRIMARY,
        knob_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        border_color: Tuple[int, int, int] = UIColors.BORDER,
        text_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        border_width: int = UIConstants.DEFAULT_BORDER_WIDTH,
        font_scale: int = UIConstants.DEFAULT_FONT_SCALE,
        show_value: bool = True,
        show_labels: bool = False,
        label_format: str = "{:.1f}",
        on_value_change: Optional[Callable] = None,
    ):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = max(min_value, min(max_value, value))
        self.step = step
        self.background_color = background_color
        self.track_color = track_color
        self.fill_color = fill_color
        self.knob_color = knob_color
        self.border_color = border_color
        self.text_color = text_color
        self.border_width = border_width
        self.font_scale = font_scale
        self.show_value = show_value
        self.show_labels = show_labels
        self.label_format = label_format

        # Slider dimensions
        self.track_height = 4
        self.knob_size = height - 4  # Leave some padding
        self.track_y_offset = (height - self.track_height) // 2

        # Interaction state
        self.is_dragging = False
        self.drag_offset = 0

        if on_value_change:
            self.add_event_handler("value_change", on_value_change)

    def set_value(self, value: Union[int, float]):
        """Set the slider value"""
        old_value = self.value
        self.value = max(self.min_value, min(self.max_value, value))

        # Snap to step
        if self.step > 0:
            steps = round((self.value - self.min_value) / self.step)
            self.value = self.min_value + steps * self.step

        if old_value != self.value:
            self.trigger_event(
                UIEvent("value_change", self, value=self.value, old_value=old_value)
            )

    def get_value_ratio(self) -> float:
        """Get the value as a ratio between 0 and 1"""
        if self.max_value == self.min_value:
            return 0
        return (self.value - self.min_value) / (self.max_value - self.min_value)

    def get_knob_position(self) -> int:
        """Get the knob's x position"""
        ratio = self.get_value_ratio()
        knob_range = self.width - self.knob_size
        return int(ratio * knob_range)

    def value_from_position(self, x: int) -> Union[int, float]:
        """Calculate value from x position"""
        abs_x, _ = self.get_absolute_position()
        relative_x = x - abs_x - self.knob_size // 2
        knob_range = self.width - self.knob_size

        if knob_range <= 0:
            return self.min_value

        ratio = max(0, min(1, relative_x / knob_range))
        return self.min_value + ratio * (self.max_value - self.min_value)

    def update(self, dt: float):
        if self.is_dragging and self.enabled:
            mouse_x, _ = pygame.mouse.get_pos()
            new_value = self.value_from_position(mouse_x - self.drag_offset)
            self.set_value(new_value)

        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()

        # Draw background
        if self.background_color != UIColors.SURFACE or self.border_width > 0:
            bg_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
            pygame.draw.rect(surface, self.background_color, bg_rect)
            if self.border_width > 0:
                pygame.draw.rect(surface, self.border_color, bg_rect, self.border_width)

        # Draw track
        track_y = abs_y + self.track_y_offset
        track_rect = pygame.Rect(abs_x, track_y, self.width, self.track_height)
        pygame.draw.rect(surface, self.track_color, track_rect)

        # Draw filled portion
        knob_pos = self.get_knob_position()
        if knob_pos > 0:
            fill_rect = pygame.Rect(
                abs_x, track_y, knob_pos + self.knob_size // 2, self.track_height
            )
            pygame.draw.rect(surface, self.fill_color, fill_rect)

        # Draw knob
        knob_x = abs_x + knob_pos
        knob_y = abs_y + (self.height - self.knob_size) // 2
        knob_rect = pygame.Rect(knob_x, knob_y, self.knob_size, self.knob_size)

        knob_color = self.knob_color if self.enabled else UIColors.TEXT_DISABLED
        pygame.draw.rect(surface, knob_color, knob_rect)
        pygame.draw.rect(surface, self.border_color, knob_rect, 1)

        # Draw value text
        if self.show_value and font:
            value_text = self.label_format.format(self.value)
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED

            # Position text above the slider
            text_y = abs_y - font.size * self.font_scale - 4
            text_x = abs_x + knob_pos + self.knob_size // 2

            # Center text horizontally on knob
            estimated_text_width = len(value_text) * font.size * self.font_scale
            text_x -= estimated_text_width // 2

            render_text(
                surface,
                value_text,
                font,
                (text_x, text_y),
                scale=self.font_scale,
                color=text_color,
            )

        # Draw min/max labels
        if self.show_labels and font:
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED
            label_y = abs_y + self.height + 4

            # Min label
            min_text = self.label_format.format(self.min_value)
            render_text(
                surface,
                min_text,
                font,
                (abs_x, label_y),
                scale=self.font_scale,
                color=text_color,
            )

            # Max label
            max_text = self.label_format.format(self.max_value)
            estimated_width = len(max_text) * font.size * self.font_scale
            render_text(
                surface,
                max_text,
                font,
                (abs_x + self.width - estimated_width, label_y),
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
                self.is_dragging = True
                # Calculate drag offset to prevent jumping
                knob_x = self.get_absolute_position()[0] + self.get_knob_position()
                self.drag_offset = event.pos[0] - knob_x - self.knob_size // 2

                # Set initial value from click position
                new_value = self.value_from_position(event.pos[0] - self.drag_offset)
                self.set_value(new_value)
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:  # Left click release
                self.is_dragging = False
                return True

        elif event.type == pygame.KEYDOWN and self.contains_point(
            pygame.mouse.get_pos()
        ):
            # Allow keyboard control when mouse is over slider
            if event.key == pygame.K_LEFT or event.key == pygame.K_DOWN:
                self.set_value(self.value - self.step)
                return True
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_UP:
                self.set_value(self.value + self.step)
                return True
            elif event.key == pygame.K_HOME:
                self.set_value(self.min_value)
                return True
            elif event.key == pygame.K_END:
                self.set_value(self.max_value)
                return True

        return False


class VerticalSlider(Slider):
    """Vertical slider component"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int = UIConstants.SLIDER_HEIGHT,
        height: int = 100,
        **kwargs
    ):
        super().__init__(x, y, width, height, **kwargs)

        # Override dimensions for vertical orientation
        self.track_width = 4
        self.knob_size = width - 4  # Leave some padding
        self.track_x_offset = (width - self.track_width) // 2

    def get_knob_position(self) -> int:
        """Get the knob's y position (from top)"""
        ratio = self.get_value_ratio()
        knob_range = self.height - self.knob_size
        return int((1 - ratio) * knob_range)  # Invert for vertical

    def value_from_position(self, x: int) -> Union[int, float]:
        """Calculate value from y position (x parameter represents y coordinate for vertical slider)"""
        _, abs_y = self.get_absolute_position()
        relative_y = x - abs_y - self.knob_size // 2
        knob_range = self.height - self.knob_size

        if knob_range <= 0:
            return self.min_value

        ratio = max(0, min(1, 1 - (relative_y / knob_range)))  # Invert for vertical
        return self.min_value + ratio * (self.max_value - self.min_value)

    def update(self, dt: float):
        if self.is_dragging and self.enabled:
            _, mouse_y = pygame.mouse.get_pos()
            new_value = self.value_from_position(mouse_y - self.drag_offset)
            self.set_value(new_value)

        # Skip Slider.update to avoid calling horizontal logic
        UIComponent.update(self, dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()

        # Draw background
        if self.background_color != UIColors.SURFACE or self.border_width > 0:
            bg_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
            pygame.draw.rect(surface, self.background_color, bg_rect)
            if self.border_width > 0:
                pygame.draw.rect(surface, self.border_color, bg_rect, self.border_width)

        # Draw track
        track_x = abs_x + self.track_x_offset
        track_rect = pygame.Rect(track_x, abs_y, self.track_width, self.height)
        pygame.draw.rect(surface, self.track_color, track_rect)

        # Draw filled portion
        knob_pos = self.get_knob_position()
        fill_height = self.height - knob_pos - self.knob_size // 2
        if fill_height > 0:
            fill_rect = pygame.Rect(
                track_x,
                abs_y + knob_pos + self.knob_size // 2,
                self.track_width,
                fill_height,
            )
            pygame.draw.rect(surface, self.fill_color, fill_rect)

        # Draw knob
        knob_x = abs_x + (self.width - self.knob_size) // 2
        knob_y = abs_y + knob_pos
        knob_rect = pygame.Rect(knob_x, knob_y, self.knob_size, self.knob_size)

        knob_color = self.knob_color if self.enabled else UIColors.TEXT_DISABLED
        pygame.draw.rect(surface, knob_color, knob_rect)
        pygame.draw.rect(surface, self.border_color, knob_rect, 1)

        # Draw value text
        if self.show_value and font:
            value_text = self.label_format.format(self.value)
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED

            # Position text to the right of the slider
            text_x = abs_x + self.width + 4
            text_y = (
                abs_y
                + knob_pos
                + self.knob_size // 2
                - font.size * self.font_scale // 2
            )

            render_text(
                surface,
                value_text,
                font,
                (text_x, text_y),
                scale=self.font_scale,
                color=text_color,
            )

        # Draw min/max labels
        if self.show_labels and font:
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED
            label_x = abs_x + self.width + 4

            # Max label (top)
            max_text = self.label_format.format(self.max_value)
            render_text(
                surface,
                max_text,
                font,
                (label_x, abs_y),
                scale=self.font_scale,
                color=text_color,
            )

            # Min label (bottom)
            min_text = self.label_format.format(self.min_value)
            min_y = abs_y + self.height - font.size * self.font_scale
            render_text(
                surface,
                min_text,
                font,
                (label_x, min_y),
                scale=self.font_scale,
                color=text_color,
            )

        # Render children
        UIComponent.render(self, surface, font)

    def _handle_event_internal(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(event.pos):  # Left click
                self.is_dragging = True
                # Calculate drag offset to prevent jumping
                knob_y = self.get_absolute_position()[1] + self.get_knob_position()
                self.drag_offset = event.pos[1] - knob_y - self.knob_size // 2

                # Set initial value from click position
                new_value = self.value_from_position(event.pos[1] - self.drag_offset)
                self.set_value(new_value)
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:  # Left click release
                self.is_dragging = False
                return True

        elif event.type == pygame.KEYDOWN and self.contains_point(
            pygame.mouse.get_pos()
        ):
            # Allow keyboard control when mouse is over slider
            if event.key == pygame.K_DOWN or event.key == pygame.K_LEFT:
                self.set_value(self.value - self.step)
                return True
            elif event.key == pygame.K_UP or event.key == pygame.K_RIGHT:
                self.set_value(self.value + self.step)
                return True
            elif event.key == pygame.K_HOME:
                self.set_value(self.max_value)  # Top for vertical
                return True
            elif event.key == pygame.K_END:
                self.set_value(self.min_value)  # Bottom for vertical
                return True

        return False
