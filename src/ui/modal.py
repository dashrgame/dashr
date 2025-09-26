import pygame

from src.utils.autotile import compute_autotile_variations
from src.renderer.tile_renderer import render_tiles


class UIModal:
    def __init__(self, root, loaded_tiles):
        self.root = root  # Root UIComponent
        self.loaded_tiles = loaded_tiles

    def handle_event(self, event):
        self.root.handle_event(event)

    def render(self, surface):
        # Create a grid shape for the modal background
        grid_w = self.root.rect.width // 16
        grid_h = self.root.rect.height // 16
        shape = [(x, y) for x in range(grid_w) for y in range(grid_h)]
        tile_variations = compute_autotile_variations(shape)
        
        tiles = []
        positions = []
        for (x, y), tile_id in tile_variations:
            tile = self.loaded_tiles[tile_id]

            tiles.append(tile)
            pos_x = self.root.rect.x + x * tile.image.width
            pos_y = self.root.rect.y + y * tile.image.height
            positions.append((pos_x, pos_y))

        render_tiles(surface, tiles, positions)
        self.root.render(surface)
