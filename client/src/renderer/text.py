import pygame
from typing import Tuple

from client.src.asset.font.font import Font


def render_text(
    surface: pygame.Surface,
    text: str,
    font: Font,
    pos: Tuple[int, int],
    scale: int = 1,
    color: Tuple[int, int, int] = (0, 0, 0),
):
    """
    Renders text onto a pygame surface at the given position using the provided Font.
    Each character is rendered next to each other with 2px spacing, and 6px after punctuation or space.
    All pixels in the character image are recolored to the specified color.
    Args:
            surface: pygame.Surface to render onto
            text: string to render
            font: Font object
            pos: (x, y) position to start rendering
            scale: scale factor for font size
            color: (r, g, b) color to render text (default black)
    """
    x, y = pos
    spacing = 2
    extra_spacing = 2
    space = " "

    for i, char in enumerate(text):
        if char == space:
            # Advance x by extra_spacing
            x += int(extra_spacing * scale)
            continue

        char_img = font.get_character_image(char)
        if char_img is None:
            # Render a tofu box for missing glyphs
            box_size = int(font.size * scale)
            py_img = pygame.Surface((box_size, box_size), pygame.SRCALPHA)
            # Draw "tofu"
            pygame.draw.rect(py_img, (0, 0, 0, 255), py_img.get_rect(), width=scale)
            surface.blit(py_img, (x, y))
            x += box_size + (spacing * scale)
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

        # Scale image
        if scale != 1.0:
            w, h = py_img.get_size()
            py_img = pygame.transform.scale(py_img, (int(w * scale), int(h * scale)))

        # Recolor every pixel to the specified color, preserving alpha
        arr = pygame.surfarray.pixels3d(py_img)
        arr[:, :, :] = color
        del arr
        if py_img.get_bitsize() == 32:
            alpha_arr = pygame.surfarray.pixels_alpha(py_img)
            # alpha stays unchanged
            del alpha_arr

        # Blit to surface
        surface.blit(py_img, (x, y))

        # Advance x position
        w = py_img.get_width()
        x += w + (spacing * scale)
