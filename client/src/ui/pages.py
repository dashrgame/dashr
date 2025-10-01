import pygame
from typing import Dict, Optional, Callable, Any
from abc import ABC, abstractmethod

from client.src.ui.core import UIComponent, UIEvent, Panel
from client.src.asset.font.font import Font


class UIPage(Panel):
    """Base class for UI pages"""

    def __init__(
        self, page_id: str, x: int = 0, y: int = 0, width: int = 800, height: int = 600
    ):
        super().__init__(x, y, width, height)
        self.page_id = page_id
        self.is_active = False
        self.transition_progress = 0.0  # 0.0 = hidden, 1.0 = fully visible
        self.transition_speed = 4.0  # transitions per second

    def activate(self):
        """Called when the page becomes active"""
        self.is_active = True
        self.visible = True

    def deactivate(self):
        """Called when the page becomes inactive"""
        self.is_active = False

    def on_enter(self):
        """Called when transitioning to this page"""
        pass

    def on_exit(self):
        """Called when transitioning away from this page"""
        pass

    def update(self, dt: float):
        # Handle transition animation
        if self.is_active and self.transition_progress < 1.0:
            self.transition_progress = min(
                1.0, self.transition_progress + self.transition_speed * dt
            )
        elif not self.is_active and self.transition_progress > 0.0:
            self.transition_progress = max(
                0.0, self.transition_progress - self.transition_speed * dt
            )
            if self.transition_progress <= 0.0:
                self.visible = False

        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        if not self.visible:
            return

        # Apply fade effect based on transition progress
        if self.transition_progress < 1.0:
            # Create a surface for the page with alpha
            page_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            super().render(page_surface, font)

            # Apply alpha to the entire page
            alpha = int(255 * self.transition_progress)
            page_surface.set_alpha(alpha)

            abs_x, abs_y = self.get_absolute_position()
            surface.blit(page_surface, (abs_x, abs_y))
        else:
            super().render(surface, font)


class PageManager:
    """Manages multiple UI pages and transitions between them"""

    def __init__(self):
        self.pages: Dict[str, UIPage] = {}
        self.current_page: Optional[UIPage] = None
        self.previous_page: Optional[UIPage] = None
        self.transition_callbacks: Dict[str, list] = {}

    def add_page(self, page: UIPage):
        """Add a page to the manager"""
        self.pages[page.page_id] = page
        page.visible = False
        page.is_active = False

    def remove_page(self, page_id: str):
        """Remove a page from the manager"""
        if page_id in self.pages:
            page = self.pages[page_id]
            if self.current_page == page:
                self.current_page = None
            del self.pages[page_id]

    def get_page(self, page_id: str) -> Optional[UIPage]:
        """Get a page by ID"""
        return self.pages.get(page_id)

    def set_current_page(self, page_id: str, immediate: bool = False):
        """Switch to a specific page"""
        if page_id not in self.pages:
            return False

        new_page = self.pages[page_id]
        if new_page == self.current_page:
            return True

        # Handle page transition
        self.previous_page = self.current_page

        if self.current_page:
            self.current_page.on_exit()
            if immediate:
                self.current_page.deactivate()
                self.current_page.transition_progress = 0.0
            else:
                self.current_page.deactivate()

        self.current_page = new_page
        new_page.on_enter()
        new_page.activate()

        if immediate:
            new_page.transition_progress = 1.0

        # Trigger transition callbacks
        self._trigger_transition_callbacks(
            "page_change",
            {
                "from_page": self.previous_page.page_id if self.previous_page else None,
                "to_page": page_id,
            },
        )

        return True

    def get_current_page(self) -> Optional[UIPage]:
        """Get the currently active page"""
        return self.current_page

    def add_transition_callback(self, event_type: str, callback: Callable):
        """Add a callback for page transitions"""
        if event_type not in self.transition_callbacks:
            self.transition_callbacks[event_type] = []
        self.transition_callbacks[event_type].append(callback)

    def remove_transition_callback(self, event_type: str, callback: Callable):
        """Remove a transition callback"""
        if (
            event_type in self.transition_callbacks
            and callback in self.transition_callbacks[event_type]
        ):
            self.transition_callbacks[event_type].remove(callback)

    def _trigger_transition_callbacks(self, event_type: str, data: Dict[str, Any]):
        """Trigger transition callbacks"""
        if event_type in self.transition_callbacks:
            for callback in self.transition_callbacks[event_type]:
                callback(data)

    def update(self, dt: float):
        """Update the page manager and active pages"""
        # Update all visible pages (for transitions)
        for page in self.pages.values():
            if page.visible or page.is_active:
                page.update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        """Render all visible pages"""
        # Render pages in order (previous page first for fade transitions)
        if (
            self.previous_page
            and self.previous_page.visible
            and self.previous_page != self.current_page
        ):
            self.previous_page.render(surface, font)

        if self.current_page and self.current_page.visible:
            self.current_page.render(surface, font)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the current page"""
        if self.current_page and self.current_page.visible:
            return self.current_page.handle_event(event)
        return False


class NavigationStack:
    """Stack-based navigation system for pages"""

    def __init__(self, page_manager: PageManager):
        self.page_manager = page_manager
        self.navigation_stack: list[str] = []

    def push_page(self, page_id: str, immediate: bool = False):
        """Push a new page onto the navigation stack"""
        if self.page_manager.current_page:
            self.navigation_stack.append(self.page_manager.current_page.page_id)

        self.page_manager.set_current_page(page_id, immediate)

    def pop_page(self, immediate: bool = False) -> bool:
        """Pop the current page and return to the previous one"""
        if not self.navigation_stack:
            return False

        previous_page_id = self.navigation_stack.pop()
        self.page_manager.set_current_page(previous_page_id, immediate)
        return True

    def pop_to_page(self, page_id: str, immediate: bool = False) -> bool:
        """Pop pages until we reach the specified page"""
        while self.navigation_stack:
            if self.navigation_stack[-1] == page_id:
                return self.pop_page(immediate)
            self.navigation_stack.pop()

        # If we didn't find the page in the stack, try to navigate to it directly
        return self.page_manager.set_current_page(page_id, immediate)

    def clear_stack(self):
        """Clear the navigation stack"""
        self.navigation_stack.clear()

    def get_stack_depth(self) -> int:
        """Get the current stack depth"""
        return len(self.navigation_stack)

    def can_go_back(self) -> bool:
        """Check if we can navigate back"""
        return len(self.navigation_stack) > 0


class TabContainer(UIComponent):
    """Container that displays pages as tabs"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        tab_height: int = 32,
        tab_spacing: int = 2,
    ):
        super().__init__(x, y, width, height)
        self.tab_height = tab_height
        self.tab_spacing = tab_spacing
        self.pages: Dict[str, UIPage] = {}
        self.tab_buttons: Dict[str, "TabButton"] = {}
        self.current_page_id: Optional[str] = None

        # Create tab area
        self.tab_area_height = tab_height + 4  # Add some padding
        self.content_area = Panel(
            0, self.tab_area_height, width, height - self.tab_area_height
        )
        self.add_child(self.content_area)

    def add_tab(self, page_id: str, page: UIPage, tab_text: str):
        """Add a tab with associated page"""
        self.pages[page_id] = page

        # Create tab button
        tab_x = len(self.tab_buttons) * (
            100 + self.tab_spacing
        )  # Fixed width tabs for now
        tab_button = TabButton(tab_x, 2, 100, self.tab_height, tab_text, page_id)
        tab_button.add_event_handler("click", self._on_tab_click)

        self.tab_buttons[page_id] = tab_button
        self.add_child(tab_button)

        # Add page to content area
        page.x = 0
        page.y = 0
        page.width = self.content_area.width
        page.height = self.content_area.height
        page.visible = False
        self.content_area.add_child(page)

        # If this is the first tab, make it active
        if self.current_page_id is None:
            self.set_active_tab(page_id)

    def remove_tab(self, page_id: str):
        """Remove a tab and its page"""
        if page_id in self.pages:
            page = self.pages[page_id]
            tab_button = self.tab_buttons[page_id]

            self.content_area.remove_child(page)
            self.remove_child(tab_button)

            del self.pages[page_id]
            del self.tab_buttons[page_id]

            # If this was the active tab, switch to another
            if self.current_page_id == page_id:
                remaining_tabs = list(self.pages.keys())
                if remaining_tabs:
                    self.set_active_tab(remaining_tabs[0])
                else:
                    self.current_page_id = None

    def set_active_tab(self, page_id: str):
        """Set the active tab"""
        if page_id not in self.pages:
            return

        # Hide current page
        if self.current_page_id:
            self.pages[self.current_page_id].visible = False
            self.tab_buttons[self.current_page_id].set_active(False)

        # Show new page
        self.current_page_id = page_id
        self.pages[page_id].visible = True
        self.tab_buttons[page_id].set_active(True)

    def _on_tab_click(self, event: UIEvent):
        """Handle tab button clicks"""
        if hasattr(event.source, "page_id") and event.source is not None:
            self.set_active_tab(event.source.page_id)

    def update(self, dt: float):
        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        super().render(surface, font)


# Import this here to avoid circular imports
from client.src.ui.components.button import Button


class TabButton(Button):
    """Button used for tab headers"""

    def __init__(
        self, x: int, y: int, width: int, height: int, text: str, page_id: str
    ):
        super().__init__(x, y, width, height, text)
        self.page_id = page_id
        self.is_active = False

    def set_active(self, active: bool):
        """Set the active state of the tab"""
        self.is_active = active

    def get_current_color(self):
        """Override to show active state"""
        if self.is_active:
            return self.hover_color
        else:
            return super().get_current_color()
