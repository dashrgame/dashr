import pygame

from client.src.asset.tile.tile import AssetTile


def render_tile(
    surface: pygame.Surface,
    tile: AssetTile,
    position: tuple[int, int],
    scale: float = 1.0,
):
    image = pygame.image.fromstring(tile.image.tobytes(), tile.image.size, "RGBA")
    if scale != 1.0:
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
        image = pygame.transform.scale(image, new_size)
    surface.blit(image, position)


def render_tiles(
    surface: pygame.Surface,
    tiles: list[AssetTile],
    positions: list[tuple[int, int]],
    scale: float = 1.0,
):
    for tile, position in zip(tiles, positions):
        render_tile(surface, tile, position, scale)
