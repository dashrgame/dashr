from PIL import Image
import os
import json

from client.src.asset.tile.tile import AssetTile


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

        # Make sure tiles folder exists
        tiles_folder = os.path.join(directory, "tiles")
        if not os.path.isdir(tiles_folder):
            raise FileNotFoundError(
                f"'tiles' folder not found in directory: {directory}"
            )

        # Load each tile from the tiles folder
        for tile_filename in os.listdir(tiles_folder):
            if tile_filename.endswith(".png"):
                tile_name = os.path.splitext(tile_filename)[0]
                tile_path = os.path.join(tiles_folder, tile_filename)

                # Load image
                image = Image.open(tile_path).convert("RGBA")

                # Create AssetTile
                tile = AssetTile(id=tile_name, image=image)
                tiles[tile_name] = tile

        return tiles
