import pygame

from src.asset.tile.tile import AssetTile


def render_tile(surface: pygame.Surface, tile: AssetTile, position: tuple[int, int]):
    image = pygame.image.fromstring(tile.image.tobytes(), tile.image.size, "RGBA")
    surface.blit(image, position)


def render_tiles(
    surface: pygame.Surface,
    tiles: list[AssetTile],
    positions: list[tuple[int, int]],
):
    for tile, position in zip(tiles, positions):
        render_tile(surface, tile, position)
