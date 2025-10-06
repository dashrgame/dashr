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

    def get_width(self, ui_scale: float) -> float:
        # Find the leftmost and rightmost non-transparent pixels
        left_bound = self.size[0]
        right_bound = -1

        for x in range(self.size[0]):
            for y in range(self.size[1]):
                pixel = self.image.getpixel((x, y))
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

        # If no non-transparent pixels found, return scaled full width
        if right_bound == -1:
            return self.image.width * ui_scale

        # Calculate actual character width and scale it (keep as float for precision)
        actual_width = right_bound - left_bound + 1
        return actual_width * ui_scale
