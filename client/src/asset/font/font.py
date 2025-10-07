from PIL import Image

from client.src.asset.font.character import FontCharacter
from client.src.asset.font.icon import IconCharacter


class Font:
    def __init__(
        self,
        size: int,
        characters: dict[str, FontCharacter],
        icons: dict[str, IconCharacter],
    ):
        self.size = size
        self.characters = characters  # Mapping from character to its FontCharacter
        self.icons = icons  # Mapping from icon ID to its IconCharacter
        self._text_width_cache = {}  # Cache for text width calculations

    def get_character_image(self, char: str) -> Image.Image | None:
        font_char = self.characters.get(char)
        return font_char.get_image() if font_char else None

    def get_icon(self, icon_id: str) -> IconCharacter | None:
        return self.icons.get(icon_id)

    def get_text_width(self, text: str, ui_scale: float) -> float:
        if not text:
            return 0.0

        # Use cache key based on text and scale
        cache_key = (text, ui_scale)
        if cache_key in self._text_width_cache:
            return self._text_width_cache[cache_key]

        total_width = 0.0
        spacing = 1.0 * ui_scale
        extra_spacing = 3.0 * ui_scale

        i = 0
        while i < len(text):
            # Check for icon syntax
            if text[i : i + 6] == "<icon:" and ">" in text[i + 6 :]:
                end_pos = text.find(">", i + 6)

                total_width += self.size * ui_scale

                # Add spacing after icon if not the last element
                if end_pos + 1 < len(text):
                    total_width += spacing

                i = end_pos + 1
            elif text[i] == " ":
                total_width += extra_spacing
                i += 1
            elif text[i] in self.characters:
                char_width = self.characters[text[i]].get_width(ui_scale)
                total_width += char_width
                # Add spacing after each character except the last one
                if i < len(text) - 1:
                    total_width += spacing
                i += 1
            else:
                # Missing glyph - use font size as fallback width
                total_width += self.size * ui_scale
                if i < len(text) - 1:
                    total_width += spacing
                i += 1

        # Cache the result for future use
        self._text_width_cache[cache_key] = total_width
        return total_width
