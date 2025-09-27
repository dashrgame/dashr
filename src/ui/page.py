from typing import List
import pygame

from src.ui.element import UIElement


class UIPage:
    def __init__(self) -> None:
        self.elements: List[UIElement] = []

    def add_element(self, element: UIElement) -> None:
        self.elements.append(element)

    def on_show(self) -> None:
        # Custom logic for when the page is shown
        pass

    def on_hide(self) -> None:
        # Custom logic for when the page is hidden
        pass

    def render(self, surface: pygame.Surface) -> None:
        # Sort elements by z_index before rendering
        for el in sorted(self.elements, key=lambda e: getattr(e, "z_index", 0)):
            if el.visible:
                el.render(surface)
