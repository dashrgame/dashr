from PIL import Image


class AssetTile:
    def __init__(self, id: str, image: Image.Image):
        self.id = id
        self.image = image

        self.size = self.image.size  # (width, height)

    def get_image(self) -> Image.Image:
        return self.image

    def get_size(self) -> tuple[int, int]:
        return self.size
