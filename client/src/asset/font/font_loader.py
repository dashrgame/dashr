from PIL import Image
import os
import json

from client.src.asset.font.character import FontCharacter
from client.src.asset.font.font import Font
from client.src.asset.font.icon import IconCharacter


class FontLoader:
    @staticmethod
    def load_font_from_directory(directory: str) -> Font:
        # Find font.json
        font_json_path = os.path.join(directory, "font.json")
        if not os.path.isfile(font_json_path):
            raise FileNotFoundError(f"font.json not found in directory: {directory}")

        with open(font_json_path, "r", encoding="utf-8") as f:
            font_data = json.load(f)

        chars: str = font_data.get("chars", "")
        if not chars:
            raise ValueError(
                "font.json must contain a 'chars' field with the characters mapping."
            )

        size = font_data.get("size")
        if not size:
            raise ValueError("font.json must contain a 'size' field.")

        # Load font characters (font.png image)
        font_image_path = os.path.join(directory, "font.png")
        if not os.path.isfile(font_image_path):
            raise FileNotFoundError(f"font.png not found in directory: {directory}")

        font_image = Image.open(font_image_path).convert("RGBA")
        img_width, img_height = font_image.size

        # Split the image into individual character images (e.g 8x8 pixels each would go each row and column)
        char_width = size
        char_height = size
        cols = img_width // char_width
        rows = img_height // char_height

        if len(chars) > cols * rows:
            raise ValueError(
                "The number of characters exceeds the number of available slots in font.png"
            )

        characters: dict[str, FontCharacter] = {}

        for index, char in enumerate(chars):
            col = index % cols
            row = index // cols

            if row >= rows:
                break  # No more space in the image

            left = col * char_width
            upper = row * char_height
            right = left + char_width
            lower = upper + char_height

            # Helper to get alpha value safely
            def get_alpha(x, y):
                pixel = font_image.getpixel((x, y))
                if isinstance(pixel, tuple) and len(pixel) == 4:
                    return pixel[3]
                return 255  # treat as opaque if not RGBA

            # Trim horizontal padding but keep vertical padding
            while left < right and all(
                get_alpha(left, y) == 0 for y in range(upper, lower)
            ):
                left += 1
            while right > left and all(
                get_alpha(right - 1, y) == 0 for y in range(upper, lower)
            ):
                right -= 1

            char_image = font_image.crop((left, upper, right, lower))
            characters[char] = FontCharacter(char, char_image)

        # Load icons (icons/*.png images)
        icons_dir = os.path.join(directory, "icons")
        icons: dict[str, IconCharacter] = {}
        if os.path.isdir(icons_dir):
            for filename in os.listdir(icons_dir):
                if filename.lower().endswith(".png"):
                    icon_id = os.path.splitext(filename)[0]
                    icon_path = os.path.join(icons_dir, filename)
                    icon_image = Image.open(icon_path).convert("RGBA")
                    icons[icon_id] = IconCharacter(icon_id, icon_image)

        font = Font(size=size, characters=characters, icons=icons)

        return font
