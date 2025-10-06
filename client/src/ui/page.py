import pygame

from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile


class Page:
    def __init__(self, id: str):
        self.id = id

    def render(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        ui_scale: int,
    ):
        pass
