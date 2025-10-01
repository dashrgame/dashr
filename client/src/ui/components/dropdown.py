import pygame
from typing import List, Tuple, Optional, Callable, Any

from client.src.ui.core import UIComponent, UIEvent, UIColors, UIConstants
from client.src.asset.font.font import Font
from client.src.renderer.text import render_text


class DropdownOption:
    """Represents an option in a dropdown"""

    def __init__(self, value: Any, text: str, enabled: bool = True):
        self.value = value
        self.text = text
        self.enabled = enabled


class Dropdown(UIComponent):
    """Dropdown/combobox component for selecting from a list of options"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = UIConstants.DROPDOWN_HEIGHT,
        options: Optional[List[DropdownOption]] = None,
        selected_index: int = -1,
        background_color: Tuple[int, int, int] = UIColors.SURFACE,
        border_color: Tuple[int, int, int] = UIColors.BORDER,
        text_color: Tuple[int, int, int] = UIColors.TEXT_PRIMARY,
        dropdown_bg_color: Tuple[int, int, int] = UIColors.BACKGROUND,
        hover_color: Tuple[int, int, int] = UIColors.BUTTON_HOVER,
        selected_color: Tuple[int, int, int] = UIColors.PRIMARY,
        border_width: int = UIConstants.DEFAULT_BORDER_WIDTH,
        font_scale: int = UIConstants.DEFAULT_FONT_SCALE,
        max_visible_options: int = 8,
        placeholder: str = "Select...",
        on_selection_change: Optional[Callable] = None,
    ):
        super().__init__(x, y, width, height)
        self.options = options or []
        self.selected_index = (
            selected_index if 0 <= selected_index < len(self.options) else -1
        )
        self.background_color = background_color
        self.border_color = border_color
        self.text_color = text_color
        self.dropdown_bg_color = dropdown_bg_color
        self.hover_color = hover_color
        self.selected_color = selected_color
        self.border_width = border_width
        self.font_scale = font_scale
        self.max_visible_options = max_visible_options
        self.placeholder = placeholder

        # Dropdown state
        self.is_open = False
        self.hover_index = -1
        self.scroll_offset = 0

        # Calculate dropdown dimensions
        self.option_height = height
        self.dropdown_height = (
            min(len(self.options), max_visible_options) * self.option_height
        )

        if on_selection_change:
            self.add_event_handler("selection_change", on_selection_change)

    def add_option(self, option: DropdownOption):
        """Add an option to the dropdown"""
        self.options.append(option)
        self.dropdown_height = (
            min(len(self.options), self.max_visible_options) * self.option_height
        )

    def remove_option(self, index: int):
        """Remove an option by index"""
        if 0 <= index < len(self.options):
            self.options.pop(index)
            if self.selected_index == index:
                self.selected_index = -1
            elif self.selected_index > index:
                self.selected_index -= 1
            self.dropdown_height = (
                min(len(self.options), self.max_visible_options) * self.option_height
            )

    def set_selected_index(self, index: int):
        """Set the selected option by index"""
        old_index = self.selected_index
        if -1 <= index < len(self.options):
            self.selected_index = index
            if old_index != self.selected_index:
                selected_option = (
                    self.options[self.selected_index]
                    if self.selected_index >= 0
                    else None
                )
                self.trigger_event(
                    UIEvent(
                        "selection_change",
                        self,
                        index=self.selected_index,
                        option=selected_option,
                        old_index=old_index,
                    )
                )

    def get_selected_option(self) -> Optional[DropdownOption]:
        """Get the currently selected option"""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None

    def get_selected_value(self) -> Any:
        """Get the value of the currently selected option"""
        option = self.get_selected_option()
        return option.value if option else None

    def open_dropdown(self):
        """Open the dropdown"""
        if not self.is_open and self.options:
            self.is_open = True

    def close_dropdown(self):
        """Close the dropdown"""
        if self.is_open:
            self.is_open = False
            self.hover_index = -1

    def get_visible_options_start(self) -> int:
        """Get the start index of visible options"""
        return self.scroll_offset

    def get_visible_options_end(self) -> int:
        """Get the end index of visible options"""
        return min(len(self.options), self.scroll_offset + self.max_visible_options)

    def scroll_to_option(self, index: int):
        """Scroll to make an option visible"""
        if index < self.scroll_offset:
            self.scroll_offset = index
        elif index >= self.scroll_offset + self.max_visible_options:
            self.scroll_offset = index - self.max_visible_options + 1

    def get_dropdown_rect(self) -> pygame.Rect:
        """Get the rectangle for the dropdown area"""
        abs_x, abs_y = self.get_absolute_position()
        return pygame.Rect(abs_x, abs_y + self.height, self.width, self.dropdown_height)

    def get_option_rect(self, index: int) -> pygame.Rect:
        """Get the rectangle for a specific option"""
        visible_index = index - self.scroll_offset
        abs_x, abs_y = self.get_absolute_position()
        option_y = abs_y + self.height + visible_index * self.option_height
        return pygame.Rect(abs_x, option_y, self.width, self.option_height)

    def get_option_at_position(self, pos: Tuple[int, int]) -> int:
        """Get the option index at a given position, or -1 if none"""
        if not self.is_open:
            return -1

        dropdown_rect = self.get_dropdown_rect()
        if not dropdown_rect.collidepoint(pos):
            return -1

        relative_y = pos[1] - dropdown_rect.y
        option_index = self.scroll_offset + (relative_y // self.option_height)

        if 0 <= option_index < len(self.options):
            return option_index
        return -1

    def update(self, dt: float):
        if self.is_open:
            # Update hover state
            mouse_pos = pygame.mouse.get_pos()
            self.hover_index = self.get_option_at_position(mouse_pos)

        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        main_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)

        # Draw main button background
        pygame.draw.rect(surface, self.background_color, main_rect)
        pygame.draw.rect(surface, self.border_color, main_rect, self.border_width)

        # Draw selected text or placeholder
        text_x = abs_x + UIConstants.DEFAULT_PADDING
        text_y = abs_y + (self.height - font.size * self.font_scale) // 2

        if self.selected_index >= 0:
            selected_option = self.options[self.selected_index]
            text_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED
            render_text(
                surface,
                selected_option.text,
                font,
                (text_x, text_y),
                scale=self.font_scale,
                color=text_color,
            )
        elif self.placeholder:
            render_text(
                surface,
                self.placeholder,
                font,
                (text_x, text_y),
                scale=self.font_scale,
                color=UIColors.TEXT_SECONDARY,
            )

        # Draw dropdown arrow
        arrow_size = 8
        arrow_x = abs_x + self.width - arrow_size - UIConstants.DEFAULT_PADDING
        arrow_y = abs_y + self.height // 2

        if self.is_open:
            # Up arrow
            points = [
                (arrow_x + arrow_size // 2, arrow_y - arrow_size // 2),
                (arrow_x, arrow_y + arrow_size // 2),
                (arrow_x + arrow_size, arrow_y + arrow_size // 2),
            ]
        else:
            # Down arrow
            points = [
                (arrow_x, arrow_y - arrow_size // 2),
                (arrow_x + arrow_size, arrow_y - arrow_size // 2),
                (arrow_x + arrow_size // 2, arrow_y + arrow_size // 2),
            ]

        arrow_color = self.text_color if self.enabled else UIColors.TEXT_DISABLED
        pygame.draw.polygon(surface, arrow_color, points)

        # Draw dropdown if open
        if self.is_open and self.options:
            dropdown_rect = self.get_dropdown_rect()

            # Draw dropdown background
            pygame.draw.rect(surface, self.dropdown_bg_color, dropdown_rect)
            pygame.draw.rect(
                surface, self.border_color, dropdown_rect, self.border_width
            )

            # Draw options
            start_index = self.get_visible_options_start()
            end_index = self.get_visible_options_end()

            for i in range(start_index, end_index):
                option = self.options[i]
                option_rect = self.get_option_rect(i)

                # Draw option background
                if i == self.hover_index:
                    pygame.draw.rect(surface, self.hover_color, option_rect)
                elif i == self.selected_index:
                    pygame.draw.rect(surface, self.selected_color, option_rect)

                # Draw option text
                option_text_x = option_rect.x + UIConstants.DEFAULT_PADDING
                option_text_y = (
                    option_rect.y
                    + (self.option_height - font.size * self.font_scale) // 2
                )

                text_color = (
                    self.text_color if option.enabled else UIColors.TEXT_DISABLED
                )
                render_text(
                    surface,
                    option.text,
                    font,
                    (option_text_x, option_text_y),
                    scale=self.font_scale,
                    color=text_color,
                )

            # Draw scrollbar if needed
            if len(self.options) > self.max_visible_options:
                scrollbar_width = 4
                scrollbar_x = abs_x + self.width - scrollbar_width - 1
                scrollbar_height = dropdown_rect.height

                # Calculate scrollbar thumb position and size
                thumb_height = max(
                    20,
                    int(
                        scrollbar_height * self.max_visible_options / len(self.options)
                    ),
                )
                thumb_y = dropdown_rect.y + int(
                    (scrollbar_height - thumb_height)
                    * self.scroll_offset
                    / (len(self.options) - self.max_visible_options)
                )

                # Draw scrollbar track
                scrollbar_rect = pygame.Rect(
                    scrollbar_x, dropdown_rect.y, scrollbar_width, scrollbar_height
                )
                pygame.draw.rect(surface, UIColors.BORDER, scrollbar_rect)

                # Draw scrollbar thumb
                thumb_rect = pygame.Rect(
                    scrollbar_x, thumb_y, scrollbar_width, thumb_height
                )
                pygame.draw.rect(surface, UIColors.TEXT_SECONDARY, thumb_rect)

        # Render children
        super().render(surface, font)

    def _handle_event_internal(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                main_rect = pygame.Rect(
                    *self.get_absolute_position(), self.width, self.height
                )

                if main_rect.collidepoint(event.pos):
                    # Click on main button
                    if self.is_open:
                        self.close_dropdown()
                    else:
                        self.open_dropdown()
                    return True
                elif self.is_open:
                    # Click in dropdown area
                    option_index = self.get_option_at_position(event.pos)
                    if option_index >= 0 and self.options[option_index].enabled:
                        self.set_selected_index(option_index)
                        self.close_dropdown()
                        return True
                    else:
                        # Click outside dropdown - close it
                        self.close_dropdown()
                        return False  # Allow other components to handle the click

        elif event.type == pygame.KEYDOWN:
            if self.is_open:
                if event.key == pygame.K_ESCAPE:
                    self.close_dropdown()
                    return True
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if (
                        0 <= self.hover_index < len(self.options)
                        and self.options[self.hover_index].enabled
                    ):
                        self.set_selected_index(self.hover_index)
                        self.close_dropdown()
                        return True
                elif event.key == pygame.K_UP:
                    # Navigate up
                    new_hover = (
                        self.hover_index - 1
                        if self.hover_index > 0
                        else len(self.options) - 1
                    )
                    while new_hover >= 0 and not self.options[new_hover].enabled:
                        new_hover -= 1
                    if new_hover >= 0:
                        self.hover_index = new_hover
                        self.scroll_to_option(self.hover_index)
                    return True
                elif event.key == pygame.K_DOWN:
                    # Navigate down
                    new_hover = (
                        self.hover_index + 1
                        if self.hover_index < len(self.options) - 1
                        else 0
                    )
                    while (
                        new_hover < len(self.options)
                        and not self.options[new_hover].enabled
                    ):
                        new_hover += 1
                    if new_hover < len(self.options):
                        self.hover_index = new_hover
                        self.scroll_to_option(self.hover_index)
                    return True
            else:
                # Dropdown closed - handle main button keys
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.contains_point(pygame.mouse.get_pos()):
                        self.open_dropdown()
                        return True

        elif event.type == pygame.MOUSEWHEEL and self.is_open:
            # Handle scrolling in dropdown
            dropdown_rect = self.get_dropdown_rect()
            if dropdown_rect.collidepoint(pygame.mouse.get_pos()):
                old_offset = self.scroll_offset
                self.scroll_offset -= event.y  # Negative for natural scrolling
                self.scroll_offset = max(
                    0,
                    min(
                        self.scroll_offset, len(self.options) - self.max_visible_options
                    ),
                )
                return old_offset != self.scroll_offset

        return False
