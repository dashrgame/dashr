import pygame
from typing import Tuple, Optional, Callable, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum

from client.src.asset.font.font import Font
from client.src.renderer.text import render_text


class UIEvent:
    """Base class for UI events"""

    def __init__(self, event_type: str, source=None, **kwargs):
        self.event_type = event_type
        self.source = source
        self.data = kwargs


class UIComponent(ABC):
    """Abstract base class for all UI components"""

    def __init__(self, x: int, y: int, width: int, height: int, visible: bool = True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = visible
        self.enabled = True
        self.parent = None
        self.children = []
        self.event_handlers: Dict[str, list] = {}

    def add_child(self, child: "UIComponent"):
        """Add a child component"""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "UIComponent"):
        """Remove a child component"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def get_absolute_position(self) -> Tuple[int, int]:
        """Get absolute position considering parent hierarchy"""
        if self.parent is None:
            return (self.x, self.y)
        parent_pos = self.parent.get_absolute_position()
        return (parent_pos[0] + self.x, parent_pos[1] + self.y)

    def get_rect(self) -> pygame.Rect:
        """Get the component's rectangle"""
        abs_x, abs_y = self.get_absolute_position()
        return pygame.Rect(abs_x, abs_y, self.width, self.height)

    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if a point is within this component"""
        return self.get_rect().collidepoint(point)

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler for a specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: str, handler: Callable):
        """Remove an event handler"""
        if (
            event_type in self.event_handlers
            and handler in self.event_handlers[event_type]
        ):
            self.event_handlers[event_type].remove(handler)

    def trigger_event(self, event: UIEvent):
        """Trigger an event and call all registered handlers"""
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                handler(event)

    @abstractmethod
    def update(self, dt: float):
        """Update the component's state"""
        if not self.visible:
            return

        for child in self.children:
            child.update(dt)

    @abstractmethod
    def render(self, surface: pygame.Surface, font: Font):
        """Render the component"""
        if not self.visible:
            return

        for child in self.children:
            child.render(surface, font)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if the event was consumed."""
        if not self.visible or not self.enabled:
            return False

        # Handle child events first (top-down)
        for child in reversed(self.children):  # Reversed for proper z-order
            if child.handle_event(event):
                return True

        return self._handle_event_internal(event)

    def _handle_event_internal(self, event: pygame.event.Event) -> bool:
        """Internal event handling to be overridden by subclasses"""
        return False


class Panel(UIComponent):
    """Basic panel component for grouping other components"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        background_color: Tuple[int, int, int] = (64, 64, 64),
        border_color: Optional[Tuple[int, int, int]] = (128, 128, 128),
        border_width: int = 1,
    ):
        super().__init__(x, y, width, height)
        self.background_color = background_color
        self.border_color = border_color
        self.border_width = border_width

    def update(self, dt: float):
        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, self.width, self.height)

        # Draw background
        pygame.draw.rect(surface, self.background_color, rect)

        # Draw border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, rect, self.border_width)

        # Render children
        super().render(surface, font)


class UIColors:
    """Standard color palette for the UI system"""

    PRIMARY = (70, 130, 180)  # Steel blue
    SECONDARY = (105, 105, 105)  # Dim gray
    SUCCESS = (34, 139, 34)  # Forest green
    DANGER = (220, 20, 60)  # Crimson
    WARNING = (255, 165, 0)  # Orange
    INFO = (30, 144, 255)  # Dodger blue

    BACKGROUND = (32, 32, 32)  # Dark gray
    SURFACE = (48, 48, 48)  # Slightly lighter gray
    BORDER = (80, 80, 80)  # Medium gray

    TEXT_PRIMARY = (255, 255, 255)  # White
    TEXT_SECONDARY = (192, 192, 192)  # Light gray
    TEXT_DISABLED = (128, 128, 128)  # Gray

    BUTTON_NORMAL = (60, 60, 60)
    BUTTON_HOVER = (80, 80, 80)
    BUTTON_PRESSED = (40, 40, 40)
    BUTTON_DISABLED = (30, 30, 30)


class UIConstants:
    """UI system constants"""

    DEFAULT_FONT_SIZE = 16
    DEFAULT_FONT_SCALE = 1
    DEFAULT_PADDING = 8
    DEFAULT_MARGIN = 4
    DEFAULT_BORDER_WIDTH = 1

    BUTTON_HEIGHT = 32
    INPUT_HEIGHT = 28
    SLIDER_HEIGHT = 20
    DROPDOWN_HEIGHT = 28

    ANIMATION_DURATION = 0.2  # seconds
