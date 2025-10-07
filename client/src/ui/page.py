import pygame
from typing import Optional, Callable

from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile


class Page:
    def __init__(
        self,
        id: str,
        always_reinitialize: bool = False,
        reinit_callback: Optional[Callable] = None,
    ):
        self.id = id
        self.always_reinitialize = always_reinitialize
        self.reinit_callback = reinit_callback

    def render(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        pass
