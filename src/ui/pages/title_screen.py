import pygame

from src.ui.screen import UIScreen
from src.ui.components.button import UIButton
from src.ui.component import UIComponent


class TitleScreen(UIScreen):
    def __init__(self, font, tile):
        root = UIComponent((0, 0, 320, 180))
        play_button = UIButton((110, 80, 100, 32), "Play", self.on_play, tile, font)
        root.add_child(play_button)
        super().__init__(root)

    def on_play(self):
        print("Play button pressed!")
