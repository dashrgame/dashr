import pygame
from src.ui.modal import UIModal
from src.ui.components.button import UIButton
from src.ui.component import UIComponent


class ConfirmModal(UIModal):
    def __init__(self, font, loaded_tiles):
        root = UIComponent((60, 60, 200, 60))
        yes_button = UIButton((70, 90, 60, 32), "Yes", self.on_yes, loaded_tiles, font)
        no_button = UIButton((140, 90, 60, 32), "No", self.on_no, loaded_tiles, font)
        root.add_child(yes_button)
        root.add_child(no_button)
        super().__init__(root, loaded_tiles)

    def on_yes(self):
        print("Confirmed!")

    def on_no(self):
        print("Cancelled!")
