import pygame

from client.src.utils.splash_picker import pick_a_splash_any_splash
from client.src.renderer.text import render_text
from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile
from client.src.ui.page import Page


class Title(Page):
    def __init__(self):
        super().__init__("title")

        self.splash: str = pick_a_splash_any_splash()
        
    def refresh_splash(self):
        self.splash = pick_a_splash_any_splash()

    def render(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        ui_scale: int,
    ):
        screen.fill((0, 0, 0))

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Calculate text dimensions for proper centering
        title_scale = ui_scale * 7
        subtitle_scale = ui_scale * 3
        splash_scale = ui_scale * 2

        # Render title - centered horizontally and positioned at 1/8 screen height
        title_text = "Dashr"
        title_color = (255, 255, 255)
        title_width = font.get_text_width(title_text, title_scale)
        title_position = (screen_width // 2 - title_width // 2, screen_height // 8)
        render_text(screen, title_text, font, title_position, title_scale, title_color)

        # Render subtitle - centered below title with proper spacing
        subtitle_text = "Demo Edition"
        subtitle_color = (200, 200, 200)
        subtitle_width = font.get_text_width(subtitle_text, subtitle_scale)
        subtitle_y = title_position[1] + (font.size * title_scale) + ui_scale
        subtitle_position = (screen_width // 2 - subtitle_width // 2, subtitle_y)
        render_text(
            screen,
            subtitle_text,
            font,
            subtitle_position,
            subtitle_scale,
            subtitle_color,
        )

        # Render splash text - centered below subtitle with generous spacing
        splash_text = self.splash
        splash_color = (255, 215, 0)  # Gold color
        splash_width = font.get_text_width(splash_text, splash_scale)
        splash_y = subtitle_position[1] + (font.size * subtitle_scale) + (20 * ui_scale)
        splash_position = (screen_width // 2 - splash_width // 2, splash_y)
        render_text(
            screen, splash_text, font, splash_position, splash_scale, splash_color
        )
