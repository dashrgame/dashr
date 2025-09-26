import pygame

from src.ui.screen import UIScreen
from src.ui.components.button import UIButton
from src.ui.component import UIComponent


class SettingsScreen(UIScreen):
    def __init__(self, font, tile):
        root = UIComponent((0, 0, 320, 180))
        back_button = UIButton((110, 120, 100, 32), "Back", self.on_back, tile, font)
        root.add_child(back_button)
        super().__init__(root)

    def on_back(self):
        print("Back button pressed!")
