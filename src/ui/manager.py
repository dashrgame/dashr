import pygame

from src.ui.screen import UIScreen
from src.ui.modal import UIModal


class UIManager:
    def __init__(self):
        self.screens = []  # Stack of UIScreen
        self.modals = []  # Stack of UIModal

    def push_screen(self, screen):
        self.screens.append(screen)

    def pop_screen(self):
        if self.screens:
            return self.screens.pop()
        return None

    def push_modal(self, modal):
        self.modals.append(modal)

    def pop_modal(self):
        if self.modals:
            return self.modals.pop()
        return None

    def handle_event(self, event):
        # Modals get priority
        if self.modals:
            self.modals[-1].handle_event(event)
        elif self.screens:
            self.screens[-1].handle_event(event)

    def render(self, surface):
        # Render screen(s)
        if self.screens:
            self.screens[-1].render(surface)
        # Render modal(s) on top
        if self.modals:
            self.modals[-1].render(surface)
