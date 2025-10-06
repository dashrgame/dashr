import pygame
from typing import Tuple

from client.src.asset.font.font import Font


def render_text(
    surface: pygame.Surface,
    text: str,
    font: Font,
    pos: Tuple[int | float, int | float],
    scale: int | float = 1.0,
    color: Tuple[int, int, int] = (0, 0, 0),
):
    if not text:
        return

    x, y = float(pos[0]), float(pos[1])
    spacing = 1.0 * scale
    extra_spacing = 3.0 * scale

    for i, char in enumerate(text):
        if char == " ":
            # Advance x by extra_spacing
            x += extra_spacing
            continue

        char_img = font.get_character_image(char)
        if char_img is None:
            # Render a tofu box for missing glyphs
            box_size = font.size * scale
            py_img = pygame.Surface(
                (max(1, round(box_size)), max(1, round(box_size))), pygame.SRCALPHA
            )

            # Draw "tofu"
            pygame.draw.rect(
                py_img, (0, 0, 0, 255), py_img.get_rect(), width=max(1, round(scale))
            )
            surface.blit(py_img, (round(x), round(y)))
            x += font.size * scale
            # Add spacing after character (except for last character)
            if i < len(text) - 1:
                x += spacing
            continue

        # Convert PIL image to pygame surface
        mode = char_img.mode
        size = char_img.size
        data = char_img.tobytes()
        # Only use valid format literals for pygame.image.fromstring
        if mode == "RGBA":
            py_img = pygame.image.fromstring(data, size, "RGBA")
        elif mode == "RGB":
            py_img = pygame.image.fromstring(data, size, "RGB")
        else:
            # fallback to RGBA
            py_img = pygame.image.fromstring(data, size, "RGBA")

        # Scale image with better precision handling
        if scale != 1.0:
            w, h = py_img.get_size()
            new_w = max(1, round(w * scale))
            new_h = max(1, round(h * scale))
            py_img = pygame.transform.scale(py_img, (new_w, new_h))

        # Recolor every pixel to the specified color, preserving alpha
        arr = pygame.surfarray.pixels3d(py_img)
        arr[:, :, :] = color
        del arr
        if py_img.get_bitsize() == 32:
            alpha_arr = pygame.surfarray.pixels_alpha(py_img)
            # alpha stays unchanged
            del alpha_arr

        # Blit to surface with consistent rounding
        surface.blit(py_img, (round(x), round(y)))

        # Advance x position using float precision to match get_text_width calculation
        char_width = (
            font.characters[char].get_width(scale)
            if char in font.characters
            else font.size * scale
        )
        x += char_width

        # Add spacing after character (except for last character)
        if i < len(text) - 1:
            x += spacing
