from typing import Callable, Any, List, Optional
import pygame

from src.ui.element import UIElement
from src.asset.font.font import Font
from src.renderer.text import render_text


class Button(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Callable[[], None],
        font=None,
        font_color=(0, 0, 0),
        font_scale=2,
    ) -> None:
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.font = font
        self.font_color = font_color
        self.font_scale = font_scale

    def render(self, surface: pygame.Surface) -> None:
        color = (200, 200, 200) if self.hovered else (150, 150, 150)
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        if self.font:
            render_text(
                surface,
                self.text,
                self.font,
                (self.x + 10, self.y + 10),
                scale=self.font_scale,
                color=self.font_color,
            )

    def handle_event(self, event: Any) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = pygame.Rect(
                self.x, self.y, self.width, self.height
            ).collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.callback()


class TextInput(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = "",
        font=None,
        font_color=(0, 0, 0),
        font_scale=2,
    ) -> None:
        super().__init__(x, y, width, height)
        self.text = text
        self.active = False
        self.font = font
        self.font_color = font_color
        self.font_scale = font_scale

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface, (255, 255, 255), (self.x, self.y, self.width, self.height)
        )
        if self.font:
            render_text(
                surface,
                self.text,
                self.font,
                (self.x + 5, self.y + 5),
                scale=self.font_scale,
                color=self.font_color,
            )
        if self.active:
            pygame.draw.rect(
                surface, (0, 120, 255), (self.x, self.y, self.width, self.height), 2
            )

    def handle_event(self, event: Any) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = pygame.Rect(
                self.x, self.y, self.width, self.height
            ).collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode


class Dropdown(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        options: List[str],
        selected: int = 0,
        font=None,
        font_color=(0, 0, 0),
        font_scale=2,
        z_index: int = 80,
    ) -> None:
        super().__init__(x, y, width, height, z_index=z_index)
        self.options = options
        self.selected = selected
        self.open = False
        self.font = font
        self.font_color = font_color
        self.font_scale = font_scale

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface, (230, 230, 230), (self.x, self.y, self.width, self.height)
        )
        if self.font:
            render_text(
                surface,
                self.options[self.selected],
                self.font,
                (self.x + 5, self.y + 5),
                scale=self.font_scale,
                color=self.font_color,
            )
        pygame.draw.rect(
            surface,
            (100, 100, 100),
            (self.x + self.width - 20, self.y, 20, self.height),
        )

        self.render_dropdown(surface)

    def render_dropdown(self, surface: pygame.Surface) -> None:
        if self.open and self.font:
            for i, option in enumerate(self.options):
                opt_rect = pygame.Rect(
                    self.x, self.y + self.height * (i + 1), self.width, self.height
                )
                pygame.draw.rect(surface, (240, 240, 240), opt_rect)
                render_text(
                    surface,
                    option,
                    self.font,
                    (opt_rect.x + 5, opt_rect.y + 5),
                    scale=self.font_scale,
                    color=self.font_color,
                )

    def handle_event(self, event: Any) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            arrow_rect = pygame.Rect(self.x + self.width - 20, self.y, 20, self.height)
            if arrow_rect.collidepoint(event.pos):
                self.open = not self.open
                return

            if self.open:
                for i, option in enumerate(self.options):
                    opt_rect = pygame.Rect(
                        self.x, self.y + self.height * (i + 1), self.width, self.height
                    )
                    if opt_rect.collidepoint(event.pos):
                        self.selected = i
                        self.open = False
                        return


class NumberInput(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        value: int = 0,
        font=None,
        font_color=(0, 0, 0),
        font_scale=2,
    ) -> None:
        super().__init__(x, y, width, height)
        self.value = value
        self.active = False
        self.font = font
        self.font_color = font_color
        self.font_scale = font_scale

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface, (255, 255, 255), (self.x, self.y, self.width, self.height)
        )
        if self.font:
            render_text(
                surface,
                str(self.value),
                self.font,
                (self.x + 5, self.y + 5),
                scale=self.font_scale,
                color=self.font_color,
            )
        if self.active:
            pygame.draw.rect(
                surface, (0, 120, 255), (self.x, self.y, self.width, self.height), 2
            )

    def handle_event(self, event: Any) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = pygame.Rect(
                self.x, self.y, self.width, self.height
            ).collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.value = int(str(self.value)[:-1] or "0")
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif event.unicode.isdigit():
                self.value = int(str(self.value) + event.unicode)


class LoadingBar(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        progress: float = 0.0,
        font=None,
        font_color=(0, 0, 0),
        font_scale=2,
    ) -> None:
        super().__init__(x, y, width, height)
        self.progress = progress
        self.font = font
        self.font_color = font_color
        self.font_scale = font_scale

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface, (200, 200, 200), (self.x, self.y, self.width, self.height)
        )
        fill_width = int(self.width * self.progress)
        pygame.draw.rect(
            surface, (80, 200, 80), (self.x, self.y, fill_width, self.height)
        )
