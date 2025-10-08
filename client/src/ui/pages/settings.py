import pygame
from client.src.ui.page import Page
from client.src.renderer.text import render_text
from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile


class SettingsPage(Page):
    def __init__(self):
        super().__init__("settings")

    def render(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        # Clear screen with dark blue background
        screen.fill((20, 20, 40))

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Render title
        title_text = "Settings Menu"
        title_color = (100, 150, 255)
        title_scale = ui_scale * 6
        title_width = font.get_text_width(title_text, title_scale)
        title_x = screen_width // 2 - title_width // 2
        title_y = screen_height // 6
        render_text(
            screen, title_text, font, (title_x, title_y), title_scale, title_color
        )

        # Render placeholder content
        content_lines = [
            "- Graphics Settings",
            "- Audio Settings",
            "- Controls",
            "- Account",
            "- About",
        ]

        content_color = (200, 200, 255)
        content_scale = ui_scale * 3
        line_height = int(font.size * content_scale * 1.5)

        start_y = title_y + int(font.size * title_scale) + 50 * ui_scale

        for i, line in enumerate(content_lines):
            line_width = font.get_text_width(line, content_scale)
            line_x = screen_width // 2 - line_width // 2
            line_y = start_y + i * line_height
            render_text(
                screen, line, font, (line_x, line_y), content_scale, content_color
            )

        # Render back instruction
        instruction_text = "Press ESC to go back"
        instruction_color = (128, 128, 128)
        instruction_scale = ui_scale * 2
        instruction_width = font.get_text_width(instruction_text, instruction_scale)
        instruction_x = screen_width // 2 - instruction_width // 2
        instruction_y = screen_height - 50 * ui_scale
        render_text(
            screen,
            instruction_text,
            font,
            (instruction_x, instruction_y),
            instruction_scale,
            instruction_color,
        )
