import pygame
from PIL import Image, ImageFilter
import numpy as np
from collections import OrderedDict
import hashlib


_BLUR_CACHE_MAXSIZE = 32
_blur_cache = OrderedDict()


def clear_blur_cache() -> None:
    _blur_cache.clear()


def _surface_hash(surface: pygame.Surface) -> bytes:
    raw = pygame.image.tostring(surface, "RGBA")
    return hashlib.sha1(raw).digest()


def apply_blur_and_darken(
    surface: pygame.Surface, blur_strength: float = 2.0, darken_strength: float = 0.5
):
    # Fast-path: nothing to do
    if blur_strength <= 0 and darken_strength <= 0:
        return surface.copy()

    # Build cache key from pixel content + params
    try:
        key = (
            _surface_hash(surface),
            float(blur_strength),
            float(darken_strength),
            surface.get_size(),
        )
    except Exception:
        key = (
            id(surface),
            float(blur_strength),
            float(darken_strength),
            surface.get_size(),
        )

    cached = _blur_cache.get(key)
    if cached is not None:
        _blur_cache.move_to_end(key)
        return cached.copy()

    # Convert pygame surface to PIL Image
    surface_array = pygame.surfarray.array3d(surface)

    # Convert from pygame's (width, height, 3) to PIL's (height, width, 3)
    surface_array = np.transpose(surface_array, (1, 0, 2))

    # Create PIL Image
    pil_image = Image.fromarray(surface_array, "RGB")

    # Apply blur if needed
    if blur_strength > 0:
        pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=blur_strength))

    # Apply darkening if needed
    if darken_strength > 0:
        # Convert to numpy array for darkening
        darkened_array = np.array(pil_image, dtype=np.float32)
        darkened_array *= 1.0 - darken_strength
        darkened_array = np.clip(darkened_array, 0, 255).astype(np.uint8)
        pil_image = Image.fromarray(darkened_array, "RGB")

    # Convert back to pygame surface
    result_array = np.array(pil_image)
    result_array = np.transpose(result_array, (1, 0, 2))

    # Create new pygame surface
    result_surface = pygame.surfarray.make_surface(result_array)

    # Preserve alpha channel if original surface had one
    if surface.get_flags() & pygame.SRCALPHA:
        result_surface = result_surface.convert_alpha()
        # Copy alpha channel from original
        alpha_array = pygame.surfarray.array_alpha(surface)
        if darken_strength > 0:
            # Darken alpha channel too
            alpha_array = (alpha_array * (1.0 - darken_strength * 0.3)).astype(np.uint8)
        pygame.surfarray.pixels_alpha(result_surface)[:] = alpha_array
    else:
        result_surface = result_surface.convert()

    cache_value = result_surface.copy()
    _blur_cache[key] = cache_value
    if len(_blur_cache) > _BLUR_CACHE_MAXSIZE:
        _blur_cache.popitem(last=False)

    return cache_value.copy()
