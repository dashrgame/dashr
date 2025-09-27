import pygame
import time

from src.ui.element import UIElement
from src.renderer.text import render_text


class Notification(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        message: str,
        timeout: float = 2.0,
        font=None,
        font_color=(255, 255, 255),
        font_scale=2,
        z_index: int = 90,
    ) -> None:
        super().__init__(x, y, width, height, z_index=z_index)
        self.message = message
        self.timeout = timeout
        self.start_time = time.time()
        self.sliding = True
        self.font = font
        self.font_color = font_color
        self.font_scale = font_scale

    def render(self, surface: pygame.Surface) -> None:
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout:
            self.visible = False
        if self.visible:
            offset = min(1.0, elapsed / 0.5) * self.width if self.sliding else 0
            pygame.draw.rect(
                surface,
                (80, 80, 200),
                (self.x + offset, self.y, self.width, self.height),
            )
            if self.font:
                render_text(
                    surface,
                    self.message,
                    self.font,
                    (int(self.x + offset + 10), self.y + 10),
                    scale=self.font_scale,
                    color=self.font_color,
                )

    def show(self) -> None:
        self.visible = True
        self.start_time = time.time()
        self.sliding = True
