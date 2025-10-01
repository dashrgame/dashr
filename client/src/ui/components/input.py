import pygame
import string
from typing import Tuple, Optional, Callable, Union

from client.src.ui.core import UIComponent, UIEvent, UIColors, UIConstants
from client.src.asset.font.font import Font
from client.src.renderer.text import render_text


class TextInput(UIComponent):
    """Text input field component"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = UIConstants.INPUT_HEIGHT,
        text: str = "",
        placeholder: str = "",
        max_length: int = 100,
        background_color: Tuple[int, int, int] = UIColors.SURFACE,
        border_color: Tuple[int, int, int] = UIColors.BORDER,
        focus_border_color: Tuple[int, int, int] = UIColors.PRIMARY,
        text_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        placeholder_color: Tuple[int, int, int] = UIColors.TEXT_SECONDARY,
        border_width: int = UIConstants.DEFAULT_BORDER_WIDTH,
        font_scale: int = UIConstants.DEFAULT_FONT_SCALE,
        padding: int = UIConstants.DEFAULT_PADDING,
        on_text_change: Optional[Callable] = None,
        on_enter: Optional[Callable] = None,
        password: bool = False,
    ):
        super().__init__(x, y, width, height)
        self.text = text
        self.placeholder = placeholder
        self.max_length = max_length
        self.background_color = background_color
        self.border_color = border_color
        self.focus_border_color = focus_border_color
        self.text_color = text_color
        self.placeholder_color = placeholder_color
        self.border_width = border_width
        self.font_scale = font_scale
        self.padding = padding
        self.password = password

        self.focused = False
        self.cursor_position = len(text)
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self.cursor_blink_rate = 0.5  # seconds

        # Text scrolling for long text
        self.text_offset = 0

        if on_text_change:
            self.add_event_handler("text_change", on_text_change)
        if on_enter:
            self.add_event_handler("enter", on_enter)

    def set_text(self, text: str):
        """Set the input text"""
        old_text = self.text
        self.text = text[: self.max_length]
        self.cursor_position = min(self.cursor_position, len(self.text))

        if old_text != self.text:
            self.trigger_event(
                UIEvent("text_change", self, text=self.text, old_text=old_text)
            )

    def get_display_text(self) -> str:
        """Get the text to display (with password masking if needed)"""
        if self.password and self.text:
            return "*" * len(self.text)
        return self.text

    def insert_text(self, new_text: str):
        """Insert text at cursor position"""
        if len(self.text) + len(new_text) <= self.max_length:
            self.text = (
                self.text[: self.cursor_position]
                + new_text
                + self.text[self.cursor_position :]
            )
            self.cursor_position += len(new_text)
            self.trigger_event(UIEvent("text_change", self, text=self.text))

    def delete_char(self, forward: bool = False):
        """Delete character at cursor position"""
        if forward and self.cursor_position < len(self.text):
            self.text = (
                self.text[: self.cursor_position]
                + self.text[self.cursor_position + 1 :]
            )
            self.trigger_event(UIEvent("text_change", self, text=self.text))
        elif not forward and self.cursor_position > 0:
            self.text = (
                self.text[: self.cursor_position - 1]
                + self.text[self.cursor_position :]
            )
            self.cursor_position -= 1
            self.trigger_event(UIEvent("text_change", self, text=self.text))

    def move_cursor(self, delta: int):
        """Move cursor by delta positions"""
        self.cursor_position = max(0, min(len(self.text), self.cursor_position + delta))

    def set_focus(self, focused: bool):
        """Set focus state"""
        self.focused = focused
        if focused:
            self.cursor_visible = True
            self.cursor_timer = 0.0

    def update(self, dt: float):
        if self.focused:
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_blink_rate:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0.0

        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, self.width, self.height)

        # Draw background
        pygame.draw.rect(surface, self.background_color, rect)

        # Draw border
        current_border_color = (
            self.focus_border_color if self.focused else self.border_color
        )
        pygame.draw.rect(surface, current_border_color, rect, self.border_width)

        # Prepare text to display
        display_text = self.get_display_text()

        # Draw text or placeholder
        text_x = abs_x + self.padding
        text_y = abs_y + (self.height - font.size * self.font_scale) // 2

        if display_text:
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED

            # Handle text scrolling for long text
            # This is a simplified approach - estimate character width
            char_width = font.size * self.font_scale + 2  # Approximate with spacing
            available_width = (
                self.width - 2 * self.padding - (10 if self.focused else 0)
            )  # Leave space for cursor

            if len(display_text) * char_width > available_width:
                # Calculate how many characters fit
                chars_that_fit = max(1, available_width // char_width)

                # Adjust text offset to keep cursor visible
                if (
                    self.cursor_position * char_width
                    > available_width + self.text_offset
                ):
                    self.text_offset = (
                        self.cursor_position * char_width - available_width
                    )
                elif self.cursor_position * char_width < self.text_offset:
                    self.text_offset = max(
                        0, self.cursor_position * char_width - char_width
                    )

                # Find the start and end positions for visible text
                start_char = max(0, self.text_offset // char_width)
                end_char = min(len(display_text), start_char + chars_that_fit)
                visible_text = display_text[start_char:end_char]

                render_text(
                    surface,
                    visible_text,
                    font,
                    (text_x - (self.text_offset % char_width), text_y),
                    scale=self.font_scale,
                    color=text_color,
                )
            else:
                render_text(
                    surface,
                    display_text,
                    font,
                    (text_x, text_y),
                    scale=self.font_scale,
                    color=text_color,
                )

        elif self.placeholder and not self.focused:
            render_text(
                surface,
                self.placeholder,
                font,
                (text_x, text_y),
                scale=self.font_scale,
                color=self.placeholder_color,
            )

        # Draw cursor
        if self.focused and self.cursor_visible and self.enabled:
            cursor_x = (
                text_x
                + (self.cursor_position * (font.size * self.font_scale + 2))
                - self.text_offset
            )
            if abs_x + self.padding <= cursor_x <= abs_x + self.width - self.padding:
                cursor_y1 = text_y
                cursor_y2 = text_y + font.size * self.font_scale
                pygame.draw.line(
                    surface,
                    self.text_color,
                    (cursor_x, cursor_y1),
                    (cursor_x, cursor_y2),
                    1,
                )

        # Render children
        super().render(surface, font)

    def _handle_event_internal(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.contains_point(event.pos):
                    self.set_focus(True)
                    # TODO: Set cursor position based on click location
                    return True
                else:
                    self.set_focus(False)

        elif event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.delete_char(False)
                return True
            elif event.key == pygame.K_DELETE:
                self.delete_char(True)
                return True
            elif event.key == pygame.K_LEFT:
                self.move_cursor(-1)
                return True
            elif event.key == pygame.K_RIGHT:
                self.move_cursor(1)
                return True
            elif event.key == pygame.K_HOME:
                self.cursor_position = 0
                return True
            elif event.key == pygame.K_END:
                self.cursor_position = len(self.text)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.trigger_event(UIEvent("enter", self, text=self.text))
                return True
            elif event.key == pygame.K_a and pygame.key.get_pressed()[pygame.K_LCTRL]:
                # Select all (move cursor to end for now)
                self.cursor_position = len(self.text)
                return True

        elif event.type == pygame.TEXTINPUT and self.focused:
            # Filter printable characters
            if event.text and event.text.isprintable():
                self.insert_text(event.text)
                return True

        return False


class NumberInput(TextInput):
    """Numeric input field that only accepts numbers"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = UIConstants.INPUT_HEIGHT,
        value: Union[int, float] = 0,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        decimal_places: int = 0,
        step: Union[int, float] = 1,
        **kwargs,
    ):
        self.numeric_value = value
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_places = decimal_places
        self.step = step
        self.is_float = decimal_places > 0 or isinstance(value, float)

        # Initialize with formatted text
        text = self._format_value(value)
        super().__init__(x, y, width, height, text=text, **kwargs)

        # Override text change handler
        self.add_event_handler("text_change", self._on_text_change)

    def _format_value(self, value: Union[int, float]) -> str:
        """Format numeric value as string"""
        if self.is_float:
            return f"{float(value):.{self.decimal_places}f}"
        else:
            return str(int(value))

    def _parse_value(self, text: str) -> Union[int, float, None]:
        """Parse string to numeric value"""
        try:
            if self.is_float:
                return float(text)
            else:
                return int(text)
        except ValueError:
            return None

    def _clamp_value(self, value: Union[int, float]) -> Union[int, float]:
        """Clamp value to min/max bounds"""
        if self.min_value is not None:
            value = max(self.min_value, value)
        if self.max_value is not None:
            value = min(self.max_value, value)
        return value

    def _on_text_change(self, event: UIEvent):
        """Handle text change and validate numeric input"""
        parsed_value = self._parse_value(self.text)
        if parsed_value is not None:
            clamped_value = self._clamp_value(parsed_value)
            if clamped_value != parsed_value:
                # Value was clamped, update text
                self.text = self._format_value(clamped_value)
            self.numeric_value = clamped_value
            self.trigger_event(UIEvent("value_change", self, value=self.numeric_value))

    def set_value(self, value: Union[int, float]):
        """Set the numeric value"""
        clamped_value = self._clamp_value(value)
        self.numeric_value = clamped_value
        self.set_text(self._format_value(clamped_value))

    def get_value(self) -> Union[int, float]:
        """Get the current numeric value"""
        return self.numeric_value

    def increment(self):
        """Increment value by step"""
        new_value = self.numeric_value + self.step
        self.set_value(new_value)

    def decrement(self):
        """Decrement value by step"""
        new_value = self.numeric_value - self.step
        self.set_value(new_value)

    def _handle_event_internal(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        # Handle number input specific keys
        if event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_UP:
                self.increment()
                return True
            elif event.key == pygame.K_DOWN:
                self.decrement()
                return True

        # Handle text input, but filter non-numeric characters
        if event.type == pygame.TEXTINPUT and self.focused:
            allowed_chars = "0123456789"
            if self.is_float and "." not in self.text:
                allowed_chars += "."
            if self.min_value is None or self.min_value < 0:
                allowed_chars += "-"

            if event.text in allowed_chars:
                # Let parent handle the insertion
                return super()._handle_event_internal(event)
            return True  # Consume the event even if we don't use it

        return super()._handle_event_internal(event)
