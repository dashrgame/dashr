import pygame
import os

from src.asset.font.font_loader import FontLoader
from src.renderer.text import render_text

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 1500, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Font Render Demo")

# Load font
font_dir = os.path.join(
    os.path.dirname(__file__),
    "/media/proplayer919/Data Drive/Coding/dashr/client/assets/fonts/default",
)
font = FontLoader.load_font_from_directory(font_dir)

# Demo text
text = "Hello, World! This is a font rendering demo. 1234567890"

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))  # White background

    # Render text
    render_text(screen, text, font, (50, 100), scale=2, color=(0, 0, 0))

    pygame.display.flip()

pygame.quit()
