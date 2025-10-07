import pygame
from typing import Dict, Optional

from client.src.ui.overlay import Overlay
from client.src.asset.font.font import Font
from client.src.asset.tile.tile import AssetTile


class OverlayManager:
    def __init__(self):
        self.overlays: Dict[str, Overlay] = {}
        self.render_order: list[str] = []

    def add_overlay(self, overlay: Overlay, render_order: Optional[int] = None):
        self.overlays[overlay.id] = overlay

        if render_order is not None:
            # Insert at specific position
            if render_order >= len(self.render_order):
                self.render_order.append(overlay.id)
            else:
                self.render_order.insert(render_order, overlay.id)
        else:
            # Add to end
            self.render_order.append(overlay.id)

    def remove_overlay(self, overlay_id: str):
        if overlay_id in self.overlays:
            del self.overlays[overlay_id]
            if overlay_id in self.render_order:
                self.render_order.remove(overlay_id)

    def get_overlay(self, overlay_id: str) -> Optional[Overlay]:
        return self.overlays.get(overlay_id)

    def toggle_overlay(self, overlay_id: str):
        overlay = self.get_overlay(overlay_id)
        if overlay:
            overlay.toggle()

    def show_overlay(self, overlay_id: str):
        overlay = self.get_overlay(overlay_id)
        if overlay:
            overlay.show()

    def hide_overlay(self, overlay_id: str):
        overlay = self.get_overlay(overlay_id)
        if overlay:
            overlay.hide()

    def handle_key_press(self, key: int):
        for overlay in self.overlays.values():
            if overlay.toggle_key == key:
                overlay.toggle()

    def render_all(
        self,
        screen: pygame.Surface,
        font: Font,
        loaded_tiles: dict[str, AssetTile],
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        for overlay_id in self.render_order:
            overlay = self.overlays.get(overlay_id)
            if overlay:
                overlay.render(screen, font, loaded_tiles, cursor_pos, ui_scale)

    def get_enabled_overlays(self) -> list[Overlay]:
        return [overlay for overlay in self.overlays.values() if overlay.enabled]

    def disable_all_overlays(self):
        for overlay in self.overlays.values():
            overlay.hide()

    def enable_all_overlays(self):
        for overlay in self.overlays.values():
            overlay.show()
