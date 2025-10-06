from PIL import Image

from client.src.asset.font.character import FontCharacter


class Font:
    def __init__(self, size: int, characters: dict[str, FontCharacter]):
        self.size = size
        self.characters = characters  # Mapping from character to its FontCharacter

    def get_character_image(self, char: str) -> Image.Image | None:
        font_char = self.characters.get(char)
        return font_char.get_image() if font_char else None

    def get_text_width(self, text: str, ui_scale: int) -> int:
        return sum(
            self.characters[char].get_width(ui_scale) for char in text if char in self.characters
        )
