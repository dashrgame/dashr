import pygame
from collections import OrderedDict
import hashlib


_PARALLAX_CACHE_MAXSIZE = 64
_parallax_cache = OrderedDict()


def clear_parallax_cache() -> None:
    _parallax_cache.clear()


def _surface_hash(surface: pygame.Surface) -> bytes:
    raw = pygame.image.tostring(surface, "RGBA")
    return hashlib.sha1(raw).digest()


def create_parallax_surface(
    surface: pygame.Surface,
    screen_size: tuple,
    cursor_pos: tuple,
    parallax_strength: float = 0.05,
) -> pygame.Surface:
    screen_width, screen_height = screen_size
    cursor_x, cursor_y = cursor_pos

    # Calculate normalized cursor position (-0.5 to 0.5)
    norm_x = (cursor_x / screen_width) - 0.5
    norm_y = (cursor_y / screen_height) - 0.5

    # Calculate available movement space (can be negative if surface is smaller)
    surface_width = surface.get_width()
    surface_height = surface.get_height()

    max_offset_x = (surface_width - screen_width) // 2
    max_offset_y = (surface_height - screen_height) // 2

    # Calculate offset based on cursor position and parallax strength
    offset_x = int(norm_x * max_offset_x * parallax_strength)
    offset_y = int(norm_y * max_offset_y * parallax_strength)

    # Calculate starting position (center by default, then apply offset)
    start_x = max_offset_x + offset_x
    start_y = max_offset_y + offset_y

    # Try to use cache. Key is surface content hash + sizes + cursor + strength
    try:
        key = (
            _surface_hash(surface),
            surface.get_size(),
            screen_size,
            int(cursor_x),
            int(cursor_y),
            float(parallax_strength),
        )
    except Exception:
        # Worst-case fallback to id-based key
        key = (
            id(surface),
            surface.get_size(),
            screen_size,
            int(cursor_x),
            int(cursor_y),
            float(parallax_strength),
        )

    cached = _parallax_cache.get(key)
    if cached is not None:
        # Move to end to mark as recently used
        _parallax_cache.move_to_end(key)
        return cached.copy()

    # Create a new surface with black background
    result_surface = pygame.Surface(screen_size)
    result_surface.fill((0, 0, 0))  # Black background

    # Calculate position to blit the source surface
    blit_x = max(0, -start_x)
    blit_y = max(0, -start_y)

    # Calculate source rect
    source_x = max(0, start_x)
    source_y = max(0, start_y)

    # Blit the surface portion
    source_rect = pygame.Rect(
        source_x,
        source_y,
        min(surface_width - source_x, screen_width - blit_x),
        min(surface_height - source_y, screen_height - blit_y),
    )

    if source_rect.width > 0 and source_rect.height > 0:
        result_surface.blit(surface, (blit_x, blit_y), source_rect)

    # Cache a copy and enforce LRU max size
    cache_value = result_surface.copy()
    _parallax_cache[key] = cache_value
    if len(_parallax_cache) > _PARALLAX_CACHE_MAXSIZE:
        _parallax_cache.popitem(last=False)

    return cache_value.copy()
