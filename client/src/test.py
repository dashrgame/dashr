import pygame
import os

from src.ui.manager import UIManager
from src.ui.page import UIPage
from src.ui.components import Button, TextInput, Dropdown, NumberInput, LoadingBar
from src.ui.modal import Modal
from src.ui.notification import Notification
from src.asset.font.font_loader import FontLoader

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Load font
font_dir = os.path.join("assets", "fonts", "default")
font = FontLoader.load_font_from_directory(font_dir)

# Create UI elements
button = Button(
    50, 50, 150, 40, "Click Me", lambda: print("Button clicked!"), font=font
)
text_input = TextInput(50, 110, 200, 40, font=font)
dropdown = Dropdown(50, 170, 200, 40, ["Option 1", "Option 2", "Option 3"], font=font)
number_input = NumberInput(50, 230, 200, 40, font=font)
loading_bar = LoadingBar(50, 290, 200, 30, 0.5, font=font)
modal = Modal(
    300, 100, 300, 200, "Modal Title", "Modal Content", lambda: print("Modal closed"), font=font
)
notification = Notification(50, 350, 300, 40, "Hello, Notification!", 3.0, font=font)

# Create a page and manager
page = UIPage()
page.add_element(button)
page.add_element(text_input)
page.add_element(dropdown)
page.add_element(number_input)
page.add_element(loading_bar)
page.add_element(modal)
page.add_element(notification)

ui_manager = UIManager()
ui_manager.register_page("main", page)
ui_manager.switch_to_page("main")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for el in page.elements:
            el.handle_event(event)
    screen.fill((30, 30, 30))
    ui_manager.render(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
