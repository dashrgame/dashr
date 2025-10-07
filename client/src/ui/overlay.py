import pygame
from typing import Optional, Callable

from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile


class Overlay:
    def __init__(
        self,
        id: str,
        enabled: bool = False,
        toggle_key: Optional[int] = None,
    ):
        self.id = id
        self.enabled = enabled
        self.toggle_key = toggle_key

    def toggle(self):
        self.enabled = not self.enabled

    def show(self):
        self.enabled = True

    def hide(self):
        self.enabled = False

    def render(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        if self.enabled:
            self._render_content(screen, font, loaded_tiles, cursor_pos, ui_scale)

    def _render_content(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        pass
