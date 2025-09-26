from PIL import Image
import os
import json

from src.asset.tile.tile import AssetTile


class TileLoader:
    @staticmethod
    def load_tiles_from_directory(directory: str) -> dict[str, AssetTile]:
        tiles = {}

        # Find tileset.json
        tileset_json_path = os.path.join(directory, "tileset.json")
        if not os.path.isfile(tileset_json_path):
            raise FileNotFoundError(f"tileset.json not found in directory: {directory}")

        with open(tileset_json_path, "r", encoding="utf-8") as f:
            tileset_data = json.load(f)

        # Find tileset.png
        tileset_image_path = os.path.join(directory, "tileset.png")
        if not os.path.isfile(tileset_image_path):
            raise FileNotFoundError(f"tileset.png not found in directory: {directory}")

        tileset_image = Image.open(tileset_image_path).convert("RGBA")

        tiles_info = tileset_data.get("tiles", {})
        for tile_position, tile_id in tiles_info.items():
            x_str, y_str = tile_position.split(",")
            x, y = int(x_str), int(y_str)

            tile_image = tileset_image.crop(
                (x * 16, y * 16, (x + 1) * 16, (y + 1) * 16)
            )

            tile = AssetTile(tile_id, tile_image)
            tiles[tile_id] = tile

        return tiles
