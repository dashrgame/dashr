from PIL import Image

from src.asset.font.character import FontCharacter

class Font:
    def __init__(self, size: int, characters: dict[str, FontCharacter]):
        self.size = size
        self.characters = characters  # Mapping from character to its FontCharacter

    def get_character_image(self, char: str) -> Image.Image | None:
        font_char = self.characters.get(char)
        return font_char.get_image() if font_char else None
