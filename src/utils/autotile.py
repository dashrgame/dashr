import json
import os

def compute_autotile_variations(shape, color="green"):
    variations = []
    if isinstance(shape, list) and all(isinstance(pos, tuple) for pos in shape):
        for pos in shape:
            tile_data = get_tile_variation(pos, shape, color)
            variations.append((pos, tile_data["tile_id"]))
    else:
        raise ValueError("Shape must be a list of positions (tuples).")
    return variations


def get_tile_variation(pos, shape, color="green"):
    x, y = pos
    max_y = len(shape)
    max_x = len(shape[0]) if max_y > 0 else 0

    def filled(nx, ny):
        return 0 <= ny < max_y and 0 <= nx < max_x and bool(shape[ny][nx])

    sides = {
        "up": filled(x, y - 1),
        "down": filled(x, y + 1),
        "left": filled(x - 1, y),
        "right": filled(x + 1, y),
    }
    filled_count = sum(sides.values())

    # Determine the tile type string
    if filled_count == 4:
        type_str = "full"
    elif filled_count == 3:
        empty_side = [k for k, v in sides.items() if not v][0]
        if empty_side == "up":
            type_str = "bottom_left_right"
        elif empty_side == "down":
            type_str = "top_left_right"
        elif empty_side == "left":
            type_str = "top_right_bottom"
        elif empty_side == "right":
            type_str = "top_left_bottom"
        else:
            type_str = "center"
    elif filled_count == 2:
        filled_sides = [k for k, v in sides.items() if v]
        if set(filled_sides) == {"up", "down"}:
            type_str = "top_bottom"
        elif set(filled_sides) == {"left", "right"}:
            type_str = "left_right"
        elif set(filled_sides) == {"up", "left"}:
            type_str = "top_left"
        elif set(filled_sides) == {"up", "right"}:
            type_str = "top_right"
        elif set(filled_sides) == {"down", "left"}:
            type_str = "bottom_left"
        elif set(filled_sides) == {"down", "right"}:
            type_str = "bottom_right"
        else:
            type_str = "center"
    elif filled_count == 1:
        filled_side = [k for k, v in sides.items() if v][0]
        if filled_side == "up":
            type_str = "top"
        elif filled_side == "down":
            type_str = "bottom"
        elif filled_side == "left":
            type_str = "left"
        elif filled_side == "right":
            type_str = "right"
        else:
            type_str = "center"
    else:
        type_str = "center"

    # Compute the tile id using color and type_str
    tile_id = f"tile_{color}_{type_str}"

    return {
        "tile_id": tile_id,
        "type_str": type_str,
        "sides": sides,
    }
