import pygame
from typing import Tuple
from enum import Enum

from client.src.ui.core import UIComponent, UIEvent, UIColors, UIConstants, Panel
from client.src.asset.font.font import Font
from client.src.renderer.text import render_text


class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Notification(Panel):
    """Notification/toast component for showing temporary messages"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        message: str,
        duration: float = 3.0,
        notification_type: str = "info",
        auto_dismiss: bool = True,
    ):

        # Set colors based on notification type
        type_colors = {
            "info": UIColors.INFO,
            "success": UIColors.SUCCESS,
            "warning": UIColors.WARNING,
            "error": UIColors.DANGER,
        }

        bg_color = type_colors.get(notification_type, UIColors.INFO)

        super().__init__(
            x, y, width, height, background_color=bg_color, border_color=UIColors.BORDER
        )

        self.message = message
        self.duration = duration
        self.notification_type = notification_type
        self.auto_dismiss = auto_dismiss

        # Animation and timing
        self.time_remaining = duration
        self.slide_progress = 0.0  # 0.0 = off-screen, 1.0 = fully visible
        self.slide_speed = 4.0  # slides per second
        self.original_x = x
        self.target_x = x

        # Start off-screen to the right
        self.x = x + width

    def show(self):
        """Show the notification with slide-in animation"""
        self.visible = True
        self.target_x = self.original_x

    def hide(self):
        """Hide the notification with slide-out animation"""
        self.target_x = self.original_x + self.width

    def update(self, dt: float):
        # Handle slide animation
        if abs(self.x - self.target_x) > 1:
            direction = 1 if self.target_x > self.x else -1
            move_distance = self.slide_speed * self.width * dt
            self.x += direction * move_distance

            # Clamp to target
            if direction > 0:
                self.x = min(self.x, self.target_x)
            else:
                self.x = max(self.x, self.target_x)
        else:
            self.x = self.target_x

        # Handle auto-dismiss timing
        if self.auto_dismiss and self.visible:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.hide()

        # Check if completely hidden
        if self.x >= self.original_x + self.width:
            self.visible = False
            self.trigger_event(UIEvent("expired", self))

        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        # Draw background with rounded corners (simplified)
        super().render(surface, font)

        # Draw message text
        if self.message and font:
            text_x = int(self.x + UIConstants.DEFAULT_PADDING)
            text_y = self.y + (self.height - font.size) // 2

            render_text(
                surface,
                self.message,
                font,
                (text_x, text_y),
                scale=1,
                color=UIColors.TEXT_PRIMARY,
            )

        # Draw progress bar if auto-dismiss
        if self.auto_dismiss and self.duration > 0:
            progress = max(0, self.time_remaining / self.duration)
            progress_width = int(self.width * progress)

            if progress_width > 0:
                progress_rect = pygame.Rect(
                    self.x, self.y + self.height - 3, progress_width, 3
                )
                pygame.draw.rect(surface, UIColors.TEXT_PRIMARY, progress_rect)
