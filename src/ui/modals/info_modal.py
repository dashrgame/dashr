import pygame
from src.ui.modal import UIModal
from src.ui.components.button import UIButton
from src.ui.component import UIComponent


class InfoModal(UIModal):
    def __init__(self, font, tile):
        root = UIComponent((60, 60, 200, 60))
        ok_button = UIButton((120, 90, 60, 32), "OK", self.on_ok, tile, font)
        root.add_child(ok_button)
        super().__init__(root, tile)

    def on_ok(self):
        print("Info acknowledged!")
