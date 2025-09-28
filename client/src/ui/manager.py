from typing import Dict, Optional
import pygame

from client.src.ui.page import UIPage


class UIManager:
    def __init__(self) -> None:
        self.pages: Dict[str, UIPage] = {}
        self.current_page: Optional[UIPage] = None

    def register_page(self, name: str, page: UIPage) -> None:
        self.pages[name] = page

    def switch_to_page(self, name: str) -> None:
        if name in self.pages:
            if self.current_page:
                self.current_page.on_hide()
            self.current_page = self.pages[name]
            self.current_page.on_show()

    def get_current_page(self) -> Optional[UIPage]:
        return self.current_page

    def render(self, surface: pygame.Surface) -> None:
        if self.current_page:
            self.current_page.render(surface)
