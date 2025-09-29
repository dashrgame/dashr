from PIL import Image
import hashlib


class AssetTile:
    def __init__(self, id: str, image: Image.Image):
        self.id = id
        self.image = image

        self.size = self.image.size  # (width, height)

    def get_image(self) -> Image.Image:
        return self.image

    def get_size(self) -> tuple[int, int]:
        return self.size

    def compute_hash(self) -> str:
        # Compute a hash of the image data for unique identification
        img_bytes = self.image.tobytes()
        return hashlib.md5(img_bytes).hexdigest()
