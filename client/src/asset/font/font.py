from PIL import Image

from client.src.asset.font.character import FontCharacter


class Font:
    def __init__(self, size: int, characters: dict[str, FontCharacter]):
        self.size = size
        self.characters = characters  # Mapping from character to its FontCharacter

    def get_character_image(self, char: str) -> Image.Image | None:
        font_char = self.characters.get(char)
        return font_char.get_image() if font_char else None

    def get_text_width(self, text: str, ui_scale: float) -> float:
        if not text:
            return 0.0

        total_width = 0.0
        spacing = 1.0 * ui_scale
        extra_spacing = 3.0 * ui_scale

        for i, char in enumerate(text):
            if char == " ":
                total_width += extra_spacing
            elif char in self.characters:
                char_width = self.characters[char].get_width(ui_scale)
                total_width += char_width
                # Add spacing after each character except the last one
                if i < len(text) - 1:
                    total_width += spacing
            else:
                # Missing glyph - use font size as fallback width
                total_width += self.size * ui_scale
                if i < len(text) - 1:
                    total_width += spacing

        return total_width
