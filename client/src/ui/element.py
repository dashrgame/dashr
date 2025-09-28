from typing import Any
import pygame


class UIElement:
    def __init__(
        self, x: int, y: int, width: int, height: int, z_index: int = 0
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.visible: bool = True
        self.z_index: int = z_index

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError()

    def handle_event(self, event: Any) -> None:
        pass
