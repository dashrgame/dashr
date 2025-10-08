import pygame
import time
from collections import deque

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

        # Calculate text dimensions based on UI scale
        line_height = 10 * ui_scale
        char_width = 6 * ui_scale  # Approximate character width
        margin = 5 * ui_scale

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

        # Calculate box dimensions based on content and scale
        max_text_width = max(len(stat) for stat in stats) * char_width
        box_width = max_text_width + (margin * 2)
        box_height = len(stats) * line_height + (margin * 2)

        # Position box in top-right corner with margin
        screen_width = screen.get_width()
        box_x = screen_width - box_width - margin
        box_y = margin

        # Draw background box
        pygame.draw.rect(screen, DEBUG_BOX_COLOR, (box_x, box_y, box_width, box_height))

        # Render all statistics
        for i, stat in enumerate(stats):
            text_x = box_x + margin
            text_y = box_y + margin + (i * line_height)
            render_text(
                screen,
                stat,
                font,
                (text_x, text_y),
                scale=ui_scale,
                color=DEBUG_TEXT_COLOR,
            )
