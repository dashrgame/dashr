from PIL import Image


class FontCharacter:
    def __init__(self, char: str, image: Image.Image):
        self.char = char
        self.image = image

        self.size = self.image.size  # (width, height)
        self._cached_actual_width = None  # Cache the computed width

    def get_image(self) -> Image.Image:
        return self.image

    def get_size(self) -> tuple[int, int]:
        return self.size

    def get_width(self, ui_scale: float) -> float:
        # Use cached width if available
        if self._cached_actual_width is None:
            self._compute_actual_width()

        # _cached_actual_width is guaranteed to be set after _compute_actual_width()
        return self._cached_actual_width * ui_scale  # type: ignore

    def _compute_actual_width(self):
        # Find the leftmost and rightmost non-transparent pixels
        left_bound = self.size[0]
        right_bound = -1

        # Use PIL's more efficient pixel access
        pixels = self.image.load()

        for x in range(self.size[0]):
            for y in range(self.size[1]):
                pixel = pixels[x, y] if pixels else self.image.getpixel((x, y))
                # Check if pixel has alpha channel and is not transparent
                if isinstance(pixel, tuple) and len(pixel) == 4 and pixel[3] > 0:
                    left_bound = min(left_bound, x)
                    right_bound = max(right_bound, x)

                # For RGB images, check if pixel is not black (assuming black is transparent)
                elif (
                    isinstance(pixel, tuple) and len(pixel) == 3 and pixel != (0, 0, 0)
                ):
                    left_bound = min(left_bound, x)
                    right_bound = max(right_bound, x)

        # If no non-transparent pixels found, cache full width
        if right_bound == -1:
            self._cached_actual_width = float(self.image.width)
        else:
            # Calculate actual character width and cache it
            self._cached_actual_width = float(right_bound - left_bound + 1)
