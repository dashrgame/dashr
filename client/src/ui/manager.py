import pygame
from typing import Dict, List, Optional, Callable, Any

from client.src.ui.core import UIComponent, UIEvent
from client.src.ui.pages import PageManager, NavigationStack
from client.src.ui.components.notification import Notification
from client.src.asset.font.font import Font


class UIManager:
    """Main UI system manager that handles all UI components, pages, and events"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Core systems
        self.page_manager = PageManager()
        self.navigation_stack = NavigationStack(self.page_manager)

        # Global UI components (overlays, popups, etc.)
        self.global_components: List[UIComponent] = []

        # Event system
        self.global_event_handlers: Dict[str, List[Callable]] = {}

        # Input focus management
        self.focused_component: Optional[UIComponent] = None

        # UI state
        self.mouse_pos = (0, 0)
        self.mouse_pressed = [False, False, False]  # Left, Middle, Right
        self.keys_pressed = set()

        # Debug mode
        self.debug_mode = False
        self.show_bounds = False

    def add_global_component(self, component: UIComponent):
        """Add a global component (overlays, popups, etc.)"""
        self.global_components.append(component)

    def remove_global_component(self, component: UIComponent):
        """Remove a global component"""
        if component in self.global_components:
            self.global_components.remove(component)
            if self.focused_component == component:
                self.focused_component = None

    def add_global_event_handler(self, event_type: str, handler: Callable):
        """Add a global event handler"""
        if event_type not in self.global_event_handlers:
            self.global_event_handlers[event_type] = []
        self.global_event_handlers[event_type].append(handler)

    def remove_global_event_handler(self, event_type: str, handler: Callable):
        """Remove a global event handler"""
        if (
            event_type in self.global_event_handlers
            and handler in self.global_event_handlers[event_type]
        ):
            self.global_event_handlers[event_type].remove(handler)

    def trigger_global_event(self, event: UIEvent):
        """Trigger a global event"""
        if event.event_type in self.global_event_handlers:
            for handler in self.global_event_handlers[event.event_type]:
                handler(event)

    def set_focus(self, component: Optional[UIComponent]):
        """Set the focused component"""
        if self.focused_component:
            # Trigger focus lost event
            self.trigger_global_event(UIEvent("focus_lost", self.focused_component))

        self.focused_component = component

        if component:
            # Trigger focus gained event
            self.trigger_global_event(UIEvent("focus_gained", component))

    def find_component_at_position(
        self, pos: tuple[int, int], components: List[UIComponent]
    ) -> Optional[UIComponent]:
        """Find the topmost component at a given position"""
        # Search in reverse order for proper z-ordering
        for component in reversed(components):
            if component.visible and component.contains_point(pos):
                # Check children first
                child_component = self.find_component_at_position(
                    pos, component.children
                )
                if child_component:
                    return child_component
                return component
        return None

    def update(self, dt: float):
        """Update the UI system"""
        # Update input state
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = list(pygame.mouse.get_pressed())
        self.keys_pressed = set(pygame.key.get_pressed())

        # Update page manager
        self.page_manager.update(dt)

        # Update global components
        for component in self.global_components:
            component.update(dt)

        # Update focus management
        self._update_focus_management()

    def _update_focus_management(self):
        """Update focus management based on mouse position"""
        # This is a basic focus management - can be enhanced
        pass

    def render(self, surface: pygame.Surface, font: Font):
        """Render the entire UI system"""
        # Render pages
        self.page_manager.render(surface, font)

        # Render global components (overlays, popups, etc.)
        for component in self.global_components:
            component.render(surface, font)

        # Render debug information if enabled
        if self.debug_mode:
            self._render_debug_info(surface, font)

    def _render_debug_info(self, surface: pygame.Surface, font: Font):
        """Render debug information"""
        if self.show_bounds:
            # Draw component bounds
            self._draw_component_bounds(surface, self.page_manager.current_page)
            for component in self.global_components:
                self._draw_component_bounds(surface, component)

        # Draw UI stats
        stats_text = [
            f"Active Page: {self.page_manager.current_page.page_id if self.page_manager.current_page else 'None'}",
            f"Global Components: {len(self.global_components)}",
            f"Focused: {self.focused_component.__class__.__name__ if self.focused_component else 'None'}",
            f"Mouse: {self.mouse_pos}",
        ]

        y = 10
        for text in stats_text:
            if font:
                from client.src.renderer.text import render_text

                render_text(surface, text, font, (10, y), scale=1, color=(255, 255, 0))
                y += font.size + 2

    def _draw_component_bounds(
        self, surface: pygame.Surface, component: Optional[UIComponent]
    ):
        """Draw debug bounds for a component and its children"""
        if not component or not component.visible:
            return

        rect = component.get_rect()
        pygame.draw.rect(surface, (255, 0, 0), rect, 1)

        # Draw children bounds
        for child in component.children:
            self._draw_component_bounds(surface, child)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events and route them to UI components"""
        consumed = False

        # Handle global components first (they have higher priority)
        for component in reversed(self.global_components):
            if component.handle_event(event):
                consumed = True
                break

        # If not consumed, try the current page
        if not consumed:
            consumed = self.page_manager.handle_event(event)

        # Handle UI manager specific events
        if not consumed:
            consumed = self._handle_manager_events(event)

        return consumed

    def _handle_manager_events(self, event: pygame.event.Event) -> bool:
        """Handle events specific to the UI manager"""
        if event.type == pygame.KEYDOWN:
            # Global keyboard shortcuts
            if event.key == pygame.K_F1:
                self.debug_mode = not self.debug_mode
                return True
            elif event.key == pygame.K_F2 and self.debug_mode:
                self.show_bounds = not self.show_bounds
                return True
            elif event.key == pygame.K_ESCAPE:
                # Try to go back in navigation
                if self.navigation_stack.can_go_back():
                    self.navigation_stack.pop_page()
                    return True

        return False

    def show_popup(self, popup_component: UIComponent):
        """Show a popup component"""
        # Center the popup on screen
        popup_component.x = (self.screen_width - popup_component.width) // 2
        popup_component.y = (self.screen_height - popup_component.height) // 2

        self.add_global_component(popup_component)

    def hide_popup(self, popup_component: UIComponent):
        """Hide a popup component"""
        self.remove_global_component(popup_component)

    def create_notification(
        self, message: str, duration: float = 3.0, notification_type: str = "info"
    ) -> Notification:
        """Create and show a notification"""
        from client.src.ui.components.notification import Notification

        notification = Notification(
            x=self.screen_width - 320,
            y=20,
            width=300,
            height=60,
            message=message,
            duration=duration,
            notification_type=notification_type,
        )

        # Position notifications in a stack
        existing_notifications = [
            comp for comp in self.global_components if isinstance(comp, Notification)
        ]
        notification.y = 20 + len(existing_notifications) * 70

        self.add_global_component(notification)

        # Auto-remove after duration
        def remove_notification():
            self.remove_global_component(notification)

        # This would need a timer system - simplified for now
        notification.add_event_handler("expired", lambda e: remove_notification())

        return notification

    def save_ui_state(self) -> Dict[str, Any]:
        """Save UI state for persistence"""
        return {
            "current_page": (
                self.page_manager.current_page.page_id
                if self.page_manager.current_page
                else None
            ),
            "navigation_stack": self.navigation_stack.navigation_stack.copy(),
            "debug_mode": self.debug_mode,
            "show_bounds": self.show_bounds,
        }

    def load_ui_state(self, state: Dict[str, Any]):
        """Load UI state from saved data"""
        if "current_page" in state and state["current_page"]:
            self.page_manager.set_current_page(state["current_page"], immediate=True)

        if "navigation_stack" in state:
            self.navigation_stack.navigation_stack = state["navigation_stack"].copy()

        if "debug_mode" in state:
            self.debug_mode = state["debug_mode"]

        if "show_bounds" in state:
            self.show_bounds = state["show_bounds"]
