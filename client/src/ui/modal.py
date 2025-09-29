from typing import Callable, Any, Optional
import pygame

from client.src.ui.element import UIElement
from client.src.renderer.text import render_text


class Modal(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str,
        content: str,
        on_close: Optional[Callable[[], None]] = None,
        font=None,
        font_color=(255, 255, 255),
        font_scale=2,
        z_index: int = 100,
    ) -> None:
        super().__init__(x, y, width, height, z_index=z_index)
        self.title = title
        self.content = content
        self.on_close = on_close
        self.open = True
        self.font = font
        self.font_color = font_color
        self.font_scale = font_scale

    def render(self, surface: pygame.Surface) -> None:
        if not self.open:
            return
        # Draw modal background
        pygame.draw.rect(
            surface, (50, 50, 50), (self.x, self.y, self.width, self.height)
        )
        # Draw title and content using custom font
        if self.font:
            render_text(
                surface,
                self.title,
                self.font,
                (self.x + 10, self.y + 10),
                scale=self.font_scale,
                color=self.font_color,
            )
            render_text(
                surface,
                self.content,
                self.font,
                (self.x + 10, self.y + 50),
                scale=self.font_scale,
                color=(220, 220, 220),
            )
        # Draw close button
        btn_rect = pygame.Rect(self.x + self.width - 40, self.y + 10, 30, 30)
        pygame.draw.rect(surface, (200, 80, 80), btn_rect)
        if self.font:
            render_text(
                surface,
                "X",
                self.font,
                (btn_rect.x + 5, btn_rect.y + 1),
                scale=4,
                color=(255, 255, 255),
            )

    def handle_event(self, event: Any) -> None:
        if not self.open:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            btn_rect = pygame.Rect(self.x + self.width - 40, self.y + 10, 30, 30)
            if btn_rect.collidepoint(mouse_pos):
                self.close()

    def close(self) -> None:
        self.open = False
        if self.on_close:
            self.on_close()
