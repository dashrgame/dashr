import pygame
import time
from collections import deque
from typing import Optional, Tuple

from client.src.ui.overlay import Overlay
from client.src.renderer.text import render_text
from client.src.constants import DEBUG_BOX_COLOR, DEBUG_TEXT_COLOR


class DebugOverlay(Overlay):
    def __init__(
        self,
        clock: pygame.time.Clock,
        current_version: str = "unknown",
        upstream_version: str = "unknown",
    ):
        super().__init__("debug", enabled=False, toggle_key=pygame.K_F3)
        self.clock = clock
        self.fps_history = deque()
        self.current_version = current_version
        self.upstream_version = upstream_version
        # Cache for the rendered overlay surface to avoid rebuilding every frame
        self._cached_surface: Optional[pygame.Surface] = None
        # A key representing the last rendered stats (to detect changes)
        self._cached_key: Optional[Tuple] = None
        # Throttle re-renders to at most 5Hz (200ms)
        self._last_render_time: float = 0.0
        self._min_update_interval: float = 0.2

    def set_versions(self, current_version: str, upstream_version: str):
        self.current_version = current_version
        self.upstream_version = upstream_version

    def update_fps_tracking(self):
        current_time = time.time()
        current_fps = self.clock.get_fps()
        self.fps_history.append((current_time, current_fps))

        # Keep only FPS data from the last second
        while self.fps_history and current_time - self.fps_history[0][0] > 1.0:
            self.fps_history.popleft()

    def _render_content(
        self,
        screen: pygame.Surface,
        font,
        loaded_tiles,
        cursor_pos: tuple[int, int],
        ui_scale: int,
    ):
        current_fps = self.clock.get_fps()
        fps_values = [fps for _, fps in self.fps_history if fps > 0]

        # Calculate text dimensions based on UI scale and font
        # Use font.size to align with actual glyph dimensions
        line_height = max(1, round(font.size * ui_scale))
        margin = max(1, round(5 * ui_scale))

        if fps_values:
            avg_fps = sum(fps_values) / len(fps_values)
            min_fps = min(fps_values)
            max_fps = max(fps_values)

            # Compute ms per frame (use current FPS when available, otherwise avg)
            selected_fps = current_fps if current_fps > 0 else avg_fps
            if selected_fps > 0:
                mspf = 1000.0 / selected_fps
            else:
                mspf = 0.0

            # Prepare stats with version info
            stats = [
                f"- FPS: {current_fps:.1f}",
                f"| Avg: {avg_fps:.1f}",
                f"| Min: {min_fps:.1f}",
                f"| Max: {max_fps:.1f}",
                f"| MSPF: {mspf:.1f} ms",
                "",
                f"- Ver: {self.current_version}",
                f"| Up: {self.upstream_version}",
            ]
        else:
            # Fallback stats when no FPS history
            # Compute mspf from current FPS if possible
            if current_fps > 0:
                mspf = 1000.0 / current_fps
            else:
                mspf = 0.0

            stats = [
                f"- FPS: {current_fps:.1f}",
                f"| mspf: {mspf:.1f} ms",
                "",
                f"- Ver: {self.current_version}",
                f"| Up: {self.upstream_version}",
            ]

        # Calculate box dimensions based on content and scale using font measurements
        max_text_width = 0.0
        for stat in stats:
            w = font.get_text_width(stat, ui_scale)
            if w > max_text_width:
                max_text_width = w

        box_width = max(1, round(max_text_width)) + (margin * 2)
        box_height = len(stats) * line_height + (margin * 2)

        # Position box in top-right corner with margin
        screen_width = screen.get_width()
        box_x = screen_width - box_width - margin
        box_y = margin

        # Build a key summarizing what is being displayed. Quantize numeric values
        # to avoid re-rendering for tiny fluctuations.
        def _quant(v: float) -> float:
            # quantize to 1 decimal place
            try:
                return round(float(v), 1)
            except Exception:
                return v

        # Create a tuple key from the stats so we can detect changes cheaply
        stats_key = tuple(
            _quant(s) if isinstance(s, (int, float)) else s for s in stats
        ) + (ui_scale,)

        now = time.time()
        should_rerender = False
        if self._cached_surface is None or self._cached_key != stats_key:
            # content changed
            should_rerender = True
        elif now - self._last_render_time > self._min_update_interval:
            # force an occasional refresh even if key matches (in case of stale cache)
            should_rerender = True

        if should_rerender:
            # Create an offscreen surface to render the box once
            surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            # Draw background box onto the offscreen surface
            pygame.draw.rect(surf, DEBUG_BOX_COLOR, (0, 0, box_width, box_height))

            # Render each stat into the offscreen surface
            for i, stat in enumerate(stats):
                text_x = margin
                text_y = margin + (i * line_height)
                render_text(
                    surf,
                    stat,
                    font,
                    (text_x, text_y),
                    scale=ui_scale,
                    color=DEBUG_TEXT_COLOR,
                )

            # Cache results
            self._cached_surface = surf
            self._cached_key = stats_key
            self._last_render_time = now

        # Blit cached surface to screen at calculated position
        if self._cached_surface:
            screen.blit(self._cached_surface, (box_x, box_y))
