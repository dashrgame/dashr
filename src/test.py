import pygame

from src.ui.manager import UIManager
from src.ui.pages.title_screen import TitleScreen
from src.ui.pages.settings_screen import SettingsScreen
from src.ui.modals.confirm_modal import ConfirmModal
from src.ui.modals.info_modal import InfoModal
from src.asset.font.font_loader import FontLoader
from src.asset.tile.tile_loader import TileLoader

pygame.init()
screen = pygame.display.set_mode((320, 180))
clock = pygame.time.Clock()

# Load font and tile (replace with your actual asset loading)
font = FontLoader.load_font_from_directory(
    "/media/proplayer919/Data Drive/Coding/dashr/client/assets/fonts/default"
)
loaded_tiles = TileLoader.load_tiles_from_directory(
    "/media/proplayer919/Data Drive/Coding/dashr/client/assets/textures/tiles/default"
)

ui_manager = UIManager()
title_screen = TitleScreen(font, loaded_tiles)
settings_screen = SettingsScreen(font, loaded_tiles)
confirm_modal = ConfirmModal(font, loaded_tiles)
info_modal = InfoModal(font, loaded_tiles)

ui_manager.push_screen(title_screen)
ui_manager.push_modal(confirm_modal)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ui_manager.handle_event(event)

    screen.fill((50, 50, 50))
    ui_manager.render(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
