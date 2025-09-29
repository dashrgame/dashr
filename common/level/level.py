from common.level.tile import Tile

from typing import Optional


class Level:
    def __init__(self, tiles: list[Tile]):
        self.tiles = tiles if tiles is not None else []

        # Calculate width and height based on tiles positions
        max_x = max(tile.position[0] for tile in self.tiles)
        max_y = max(tile.position[1] for tile in self.tiles)
        self.width = max_x + 1
        self.height = max_y + 1

    def get_tile_at(self, position: tuple[int, int]) -> Optional[Tile]:
        for tile in self.tiles:
            if tile.position == position:
                return tile
        return None
