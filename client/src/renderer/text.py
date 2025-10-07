import pygame
import re
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

    # Parse text for icon tags
    icon_pattern = r"<icon:([^>]+)>"
    parts = re.split(r"(<icon:[^>]+>)", text)

    for part in parts:
        if not part:
            continue

        # Check if this part is an icon tag
        icon_match = re.match(icon_pattern, part)
        if icon_match:
            icon_id = icon_match.group(1)
            icon_char = font.get_icon(icon_id)

            if icon_char is None:
                # Render a tofu box for missing icons
                box_size = font.size * scale
                py_img = pygame.Surface(
                    (max(1, round(box_size)), max(1, round(box_size))), pygame.SRCALPHA
                )
                pygame.draw.rect(
                    py_img,
                    (255, 0, 255, 255),
                    py_img.get_rect(),
                    width=max(1, round(scale)),
                )
                surface.blit(py_img, (round(x), round(y)))
                x += font.size * scale
                x += spacing
                continue

            # Render icon without color override
            char_img = icon_char.image
            mode = char_img.mode
            size = char_img.size
            data = char_img.tobytes()

            if mode == "RGBA":
                py_img = pygame.image.fromstring(data, size, "RGBA")
            elif mode == "RGB":
                py_img = pygame.image.fromstring(data, size, "RGB")
            else:
                py_img = pygame.image.fromstring(data, size, "RGBA")

            # Calculate combined scale factor
            target_size = font.size  # Target icon size
            
            # Calculate final dimensions with combined scaling
            final_w = max(1, round(target_size * scale))
            final_h = max(1, round(target_size * scale))
            
            # Apply combined scale in one operation
            py_img = pygame.transform.scale(py_img, (final_w, final_h))

            # Blit icon without color override
            surface.blit(py_img, (round(x), round(y)))

            # Advance x position
            icon_width = final_w
            x += icon_width
            x += spacing
            continue

        # Regular text processing
        for i, char in enumerate(part):
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
                    py_img,
                    color,
                    py_img.get_rect(),
                    width=max(1, round(scale)),
                )
                surface.blit(py_img, (round(x), round(y)))
                x += font.size * scale
                # Add spacing after character (except for last character)
                if i < len(part) - 1:
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
            if i < len(part) - 1:
                x += spacing
