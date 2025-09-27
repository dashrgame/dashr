from PIL import Image


class FontCharacter:
    def __init__(self, char: str, image: Image.Image):
        self.char = char
        self.image = image

        self.size = self.image.size  # (width, height)

    def get_image(self) -> Image.Image:
        return self.image

    def get_size(self) -> tuple[int, int]:
        return self.size
