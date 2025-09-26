import pygame

from src.ui.component import UIComponent
from src.renderer.text import render_text
from src.utils.autotile import compute_autotile_variations
from src.renderer.tile import render_tiles


class UIButton(UIComponent):
    def __init__(self, rect, text, callback, loaded_tiles, font):
        super().__init__(rect)
        self.text = text
        self.callback = callback
        self.loaded_tiles = loaded_tiles
        self.font = font
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.callback()
        super().handle_event(event)

    def render(self, surface):
        grid_w = self.rect.width // 16
        grid_h = self.rect.height // 16
        shape = [(x, y) for x in range(grid_w) for y in range(grid_h)]
        tile_variations = compute_autotile_variations(shape)

        tiles = []
        positions = []
        for (x, y), tile_id in tile_variations:
            tile = self.loaded_tiles[tile_id]

            tiles.append(tile)
            pos_x = self.rect.x + x * tile.image.width
            pos_y = self.rect.y + y * tile.image.height
            positions.append((pos_x, pos_y))

        render_tiles(surface, tiles, positions)
        render_text(surface, self.text, self.font, self.rect.center, 2)
        super().render(surface)
