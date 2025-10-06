import pygame
from typing import Optional

from client.src.ui.page import Page
from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile


class PageManager:
    def __init__(self):
        self.navigation_stack: list[Page] = []
        self.current_page: Optional[Page] = None

    def set_page(self, page: Page):
        if self.current_page:
            self.navigation_stack.append(self.current_page)
        self.current_page = page

    def go_back(self):
        if self.navigation_stack:
            self.current_page = self.navigation_stack.pop()
        else:
            self.current_page = None

    def get_current_page(self) -> Optional[Page]:
        return self.current_page

    def render_current_page(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        if self.current_page:
            self.current_page.render(screen, font, loaded_tiles, cursor_pos, ui_scale)
