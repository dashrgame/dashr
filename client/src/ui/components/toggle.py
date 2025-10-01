import pygame
from typing import Tuple, Optional, Callable

from client.src.ui.core import UIComponent, UIEvent, UIColors, UIConstants
from client.src.asset.font.font import Font
from client.src.renderer.text import render_text


class Toggle(UIComponent):
    """Toggle/checkbox component"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        checked: bool = False,
        text: str = "",
        background_color: Tuple[int, int, int] = UIColors.SURFACE,
        checked_color: Tuple[int, int, int] = UIColors.PRIMARY,
        border_color: Tuple[int, int, int] = UIColors.BORDER,
        text_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        border_width: int = UIConstants.DEFAULT_BORDER_WIDTH,
        font_scale: int = UIConstants.DEFAULT_FONT_SCALE,
        on_toggle: Optional[Callable] = None,
    ):
        super().__init__(x, y, width, height)
        self.checked = checked
        self.text = text
        self.background_color = background_color
        self.checked_color = checked_color
        self.border_color = border_color
        self.text_color = text_color
        self.border_width = border_width
        self.font_scale = font_scale

        # Toggle box dimensions
        self.toggle_size = min(height - 4, 20)  # Leave some padding
        self.text_offset = self.toggle_size + 8  # Space between toggle and text

        if on_toggle:
            self.add_event_handler("toggle", on_toggle)

    def set_checked(self, checked: bool):
        """Set the checked state"""
        if self.checked != checked:
            self.checked = checked
            self.trigger_event(UIEvent("toggle", self, checked=self.checked))

    def toggle_state(self):
        """Toggle the current state"""
        self.set_checked(not self.checked)

    def update(self, dt: float):
        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()

        # Calculate toggle box position
        toggle_y = abs_y + (self.height - self.toggle_size) // 2
        toggle_rect = pygame.Rect(abs_x, toggle_y, self.toggle_size, self.toggle_size)

        # Draw toggle box background
        pygame.draw.rect(surface, self.background_color, toggle_rect)

        # Draw toggle box border
        pygame.draw.rect(surface, self.border_color, toggle_rect, self.border_width)

        # Draw check mark if checked
        if self.checked:
            # Draw a filled rectangle for the checked state
            check_padding = 3
            check_rect = pygame.Rect(
                abs_x + check_padding,
                toggle_y + check_padding,
                self.toggle_size - 2 * check_padding,
                self.toggle_size - 2 * check_padding,
            )
            pygame.draw.rect(surface, self.checked_color, check_rect)

        # Draw text
        if self.text and font:
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED
            text_x = abs_x + self.text_offset
            text_y = abs_y + (self.height - font.size * self.font_scale) // 2

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
                self.toggle_state()
                return True

        return False


class Switch(UIComponent):
    """iOS-style switch component"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int = 50,
        height: int = 25,
        checked: bool = False,
        text: str = "",
        background_color: Tuple[int, int, int] = UIColors.SURFACE,
        checked_color: Tuple[int, int, int] = UIColors.SUCCESS,
        knob_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        border_color: Tuple[int, int, int] = UIColors.BORDER,
        text_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        border_width: int = UIConstants.DEFAULT_BORDER_WIDTH,
        font_scale: int = UIConstants.DEFAULT_FONT_SCALE,
        on_toggle: Optional[Callable] = None,
    ):
        super().__init__(x, y, width, height)
        self.checked = checked
        self.text = text
        self.background_color = background_color
        self.checked_color = checked_color
        self.knob_color = knob_color
        self.border_color = border_color
        self.text_color = text_color
        self.border_width = border_width
        self.font_scale = font_scale

        # Animation properties
        self.knob_position = width - height + 2 if checked else 2
        self.target_position = self.knob_position
        self.animation_speed = 200  # pixels per second

        # Switch dimensions
        self.switch_width = width
        self.switch_height = height
        self.knob_size = height - 4  # Leave some padding
        self.text_offset = width + 8  # Space between switch and text

        if on_toggle:
            self.add_event_handler("toggle", on_toggle)

    def set_checked(self, checked: bool):
        """Set the checked state with animation"""
        if self.checked != checked:
            self.checked = checked
            self.target_position = (
                self.switch_width - self.switch_height + 2 if checked else 2
            )
            self.trigger_event(UIEvent("toggle", self, checked=self.checked))

    def toggle_state(self):
        """Toggle the current state"""
        self.set_checked(not self.checked)

    def update(self, dt: float):
        # Animate knob position
        if abs(self.knob_position - self.target_position) > 1:
            direction = 1 if self.target_position > self.knob_position else -1
            self.knob_position += direction * self.animation_speed * dt

            # Clamp to target
            if direction > 0:
                self.knob_position = min(self.knob_position, self.target_position)
            else:
                self.knob_position = max(self.knob_position, self.target_position)
        else:
            self.knob_position = self.target_position

        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()

        # Draw switch background
        switch_rect = pygame.Rect(abs_x, abs_y, self.switch_width, self.switch_height)
        current_bg_color = self.checked_color if self.checked else self.background_color

        # Draw rounded rectangle (approximate with regular rect for now)
        pygame.draw.rect(surface, current_bg_color, switch_rect)
        pygame.draw.rect(surface, self.border_color, switch_rect, self.border_width)

        # Draw knob
        knob_rect = pygame.Rect(
            abs_x + int(self.knob_position), abs_y + 2, self.knob_size, self.knob_size
        )
        pygame.draw.rect(surface, self.knob_color, knob_rect)

        # Draw text
        if self.text and font:
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED
            text_x = abs_x + self.text_offset
            text_y = abs_y + (self.height - font.size * self.font_scale) // 2

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
                self.toggle_state()
                return True

        return False


class RadioButton(UIComponent):
    """Radio button component - part of a group where only one can be selected"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        group_id: str,
        value: str,
        text: str = "",
        selected: bool = False,
        background_color: Tuple[int, int, int] = UIColors.SURFACE,
        selected_color: Tuple[int, int, int] = UIColors.PRIMARY,
        border_color: Tuple[int, int, int] = UIColors.BORDER,
        text_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        border_width: int = UIConstants.DEFAULT_BORDER_WIDTH,
        font_scale: int = UIConstants.DEFAULT_FONT_SCALE,
        on_select: Optional[Callable] = None,
    ):
        super().__init__(x, y, width, height)
        self.group_id = group_id
        self.value = value
        self.text = text
        self.selected = selected
        self.background_color = background_color
        self.selected_color = selected_color
        self.border_color = border_color
        self.text_color = text_color
        self.border_width = border_width
        self.font_scale = font_scale

        # Radio button dimensions
        self.radio_size = min(height - 4, 20)  # Leave some padding
        self.text_offset = self.radio_size + 8  # Space between radio and text

        if on_select:
            self.add_event_handler("select", on_select)

    def set_selected(self, selected: bool):
        """Set the selected state"""
        if self.selected != selected:
            self.selected = selected
            if selected:
                self.trigger_event(
                    UIEvent("select", self, group_id=self.group_id, value=self.value)
                )

    def update(self, dt: float):
        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()

        # Calculate radio button position
        radio_y = abs_y + (self.height - self.radio_size) // 2
        radio_center = (abs_x + self.radio_size // 2, radio_y + self.radio_size // 2)
        radio_radius = self.radio_size // 2

        # Draw radio button background (circle)
        pygame.draw.circle(surface, self.background_color, radio_center, radio_radius)

        # Draw radio button border
        pygame.draw.circle(
            surface, self.border_color, radio_center, radio_radius, self.border_width
        )

        # Draw selection indicator if selected
        if self.selected:
            inner_radius = max(1, radio_radius - 4)
            pygame.draw.circle(surface, self.selected_color, radio_center, inner_radius)

        # Draw text
        if self.text and font:
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED
            text_x = abs_x + self.text_offset
            text_y = abs_y + (self.height - font.size * self.font_scale) // 2

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
                if not self.selected:
                    self.set_selected(True)
                return True

        return False
