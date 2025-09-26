import pygame


class UIScreen:
    def __init__(self, root):
        self.root = root  # Root UIComponent

    def handle_event(self, event):
        self.root.handle_event(event)

    def render(self, surface):
        self.root.render(surface)
