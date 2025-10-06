import pygame


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

    return result_surface
