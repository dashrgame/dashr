import pygame

from src.renderer.text import render_text


class UIComponent:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def handle_event(self, event):
        for child in self.children:
            child.handle_event(event)

    def render(self, surface):
        for child in self.children:
            child.render(surface)
