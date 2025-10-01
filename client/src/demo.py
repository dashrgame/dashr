import pygame
import os
import sys

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from client.src.asset.font.font_loader import FontLoader
from client.src.ui.manager import UIManager
from client.src.ui.pages import UIPage
from client.src.ui.components.button import Button, IconButton
from client.src.ui.components.toggle import Toggle, Switch, RadioButton
from client.src.ui.components.input import TextInput, NumberInput
from client.src.ui.components.slider import Slider, VerticalSlider
from client.src.ui.components.dropdown import Dropdown, DropdownOption
from client.src.ui.layouts.layout import LinearLayout, GridLayout, FlexLayout, LayoutDirection, Alignment
from client.src.ui.core import UIEvent, UIColors


class MainMenuPage(UIPage):
    """Main menu page demonstrating various UI components"""
    
    def __init__(self):
        super().__init__("main_menu", 0, 0, 800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        main_layout = LinearLayout(20, 20, 760, 560, 
                                 direction=LayoutDirection.VERTICAL,
                                 spacing=20, padding=20,
                                 background_color=UIColors.BACKGROUND)
        self.add_child(main_layout)
        
        # Title
        title_button = Button(0, 0, 300, 40, "Dashr UI System Demo",
                            background_color=UIColors.PRIMARY,
                            text_color=UIColors.TEXT_PRIMARY)
        main_layout.add_child(title_button, weight=0)
        
        # Button showcase
        button_layout = LinearLayout(0, 0, 720, 60,
                                   direction=LayoutDirection.HORIZONTAL,
                                   spacing=10)
        
        normal_btn = Button(0, 0, 120, 40, "Normal",
                          on_click=lambda e: self.show_notification("Normal button clicked!"))
        button_layout.add_child(normal_btn)
        
        primary_btn = Button(0, 0, 120, 40, "Primary",
                           background_color=UIColors.PRIMARY,
                           on_click=lambda e: self.show_notification("Primary button clicked!", "success"))
        button_layout.add_child(primary_btn)
        
        danger_btn = Button(0, 0, 120, 40, "Danger",
                          background_color=UIColors.DANGER,
                          on_click=lambda e: self.show_notification("Danger button clicked!", "error"))
        button_layout.add_child(danger_btn)
        
        disabled_btn = Button(0, 0, 120, 40, "Disabled")
        disabled_btn.set_enabled(False)
        button_layout.add_child(disabled_btn)
        
        main_layout.add_child(button_layout, weight=0)
        
        # Toggle controls
        toggle_layout = LinearLayout(0, 0, 720, 40,
                                   direction=LayoutDirection.HORIZONTAL,
                                   spacing=20)
        
        self.checkbox = Toggle(0, 0, 150, 30, text="Checkbox",
                              on_toggle=lambda e: self.show_notification(f"Checkbox: {e.data['checked']}"))
        toggle_layout.add_child(self.checkbox)
        
        self.switch = Switch(0, 0, 50, 25, text="Switch",
                           on_toggle=lambda e: self.show_notification(f"Switch: {e.data['checked']}"))
        toggle_layout.add_child(self.switch)
        
        self.radio1 = RadioButton(0, 0, 100, 30, "group1", "option1", "Option 1")
        self.radio2 = RadioButton(0, 0, 100, 30, "group1", "option2", "Option 2")
        toggle_layout.add_child(self.radio1)
        toggle_layout.add_child(self.radio2)
        
        main_layout.add_child(toggle_layout, weight=0)
        
        # Input controls
        input_layout = LinearLayout(0, 0, 720, 80,
                                  direction=LayoutDirection.VERTICAL,
                                  spacing=10)
        
        input_row1 = LinearLayout(0, 0, 720, 30,
                                direction=LayoutDirection.HORIZONTAL,
                                spacing=10)
        
        self.text_input = TextInput(0, 0, 200, 30, placeholder="Enter text...")
        self.number_input = NumberInput(0, 0, 150, 30, value=42, min_value=0, max_value=100)
        
        input_row1.add_child(self.text_input)
        input_row1.add_child(self.number_input)
        
        input_layout.add_child(input_row1)
        
        # Sliders
        slider_row = LinearLayout(0, 0, 720, 40,
                                direction=LayoutDirection.HORIZONTAL,
                                spacing=20)
        
        self.h_slider = Slider(0, 0, 200, 20, min_value=0, max_value=100, value=50,
                             show_value=True, label_format="{:.0f}")
        self.v_slider = VerticalSlider(0, 0, 20, 80, min_value=0, max_value=100, value=25,
                                     show_value=True)
        
        slider_row.add_child(self.h_slider)
        slider_row.add_child(self.v_slider)
        
        input_layout.add_child(slider_row)
        main_layout.add_child(input_layout, weight=0)
        
        # Dropdown
        dropdown_layout = LinearLayout(0, 0, 720, 40,
                                     direction=LayoutDirection.HORIZONTAL,
                                     spacing=10)
        
        options = [
            DropdownOption("option1", "First Option"),
            DropdownOption("option2", "Second Option"),
            DropdownOption("option3", "Third Option"),
            DropdownOption("disabled", "Disabled Option", enabled=False),
        ]
        
        self.dropdown = Dropdown(0, 0, 200, 30, options=options, placeholder="Choose...")
        dropdown_layout.add_child(self.dropdown)
        
        main_layout.add_child(dropdown_layout, weight=0)
        
        # Navigation buttons
        nav_layout = LinearLayout(0, 0, 720, 60,
                                direction=LayoutDirection.HORIZONTAL,
                                spacing=10)
        
        layout_demo_btn = Button(0, 0, 150, 40, "Layout Demo",
                               on_click=lambda e: self.navigate_to_page("layout_demo"))
        settings_btn = Button(0, 0, 150, 40, "Settings",
                            on_click=lambda e: self.navigate_to_page("settings"))
        
        nav_layout.add_child(layout_demo_btn)
        nav_layout.add_child(settings_btn)
        
        main_layout.add_child(nav_layout, weight=0)
        
    def show_notification(self, message: str, type_str: str = "info"):
        """Show a notification (this would normally go through the UI manager)"""
        print(f"Notification ({type_str}): {message}")
        
    def navigate_to_page(self, page_id: str):
        """Navigate to another page"""
        print(f"Navigating to page: {page_id}")


class LayoutDemoPage(UIPage):
    """Page demonstrating different layout systems"""
    
    def __init__(self):
        super().__init__("layout_demo", 0, 0, 800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_container = LinearLayout(10, 10, 780, 580,
                                    direction=LayoutDirection.VERTICAL,
                                    spacing=10, padding=10,
                                    background_color=UIColors.BACKGROUND)
        self.add_child(main_container)
        
        # Title and back button
        header = LinearLayout(0, 0, 760, 40,
                            direction=LayoutDirection.HORIZONTAL,
                            spacing=10)
        
        back_btn = Button(0, 0, 80, 30, "Back")
        title = Button(0, 0, 200, 30, "Layout Demonstration",
                     background_color=UIColors.PRIMARY)
        
        header.add_child(back_btn)
        header.add_child(title)
        main_container.add_child(header, weight=0)
        
        # Demo layouts container
        demo_container = LinearLayout(0, 0, 760, 520,
                                    direction=LayoutDirection.HORIZONTAL,
                                    spacing=10)
        
        # Linear layout demo
        linear_demo = LinearLayout(0, 0, 240, 520,
                                 direction=LayoutDirection.VERTICAL,
                                 spacing=5, padding=5,
                                 background_color=UIColors.SURFACE,
                                 border_color=UIColors.BORDER)
        
        linear_title = Button(0, 0, 230, 25, "Linear Layout",
                            background_color=UIColors.SECONDARY)
        linear_demo.add_child(linear_title, weight=0)
        
        for i in range(4):
            btn = Button(0, 0, 230, 30, f"Item {i+1}",
                       background_color=UIColors.BUTTON_NORMAL)
            linear_demo.add_child(btn, weight=1 if i == 1 else 0)  # Make second item flexible
            
        demo_container.add_child(linear_demo)
        
        # Grid layout demo
        grid_demo = GridLayout(0, 0, 240, 520, rows=4, columns=2,
                             spacing=5, padding=5,
                             background_color=UIColors.SURFACE,
                             border_color=UIColors.BORDER)
        
        grid_title = Button(0, 0, 230, 25, "Grid Layout",
                          background_color=UIColors.SECONDARY)
        grid_demo.add_child_at(grid_title, 0, 0, 1, 2)  # Span 2 columns
        
        for row in range(1, 4):
            for col in range(2):
                btn = Button(0, 0, 100, 30, f"R{row}C{col}",
                           background_color=UIColors.BUTTON_NORMAL)
                grid_demo.add_child_at(btn, row, col)
                
        demo_container.add_child(grid_demo)
        
        # Flex layout demo
        flex_demo = FlexLayout(0, 0, 240, 520,
                             direction=LayoutDirection.VERTICAL,
                             justify_content=Alignment.START,
                             align_items=Alignment.STRETCH,
                             spacing=5, padding=5,
                             background_color=UIColors.SURFACE,
                             border_color=UIColors.BORDER)
        
        flex_title = Button(0, 0, 230, 25, "Flex Layout",
                          background_color=UIColors.SECONDARY)
        flex_demo.add_child(flex_title, flex_grow=0)
        
        # Add flexible items
        flex_demo.add_child(Button(0, 0, 230, 30, "Fixed", background_color=UIColors.BUTTON_NORMAL), flex_grow=0)
        flex_demo.add_child(Button(0, 0, 230, 30, "Grow 1", background_color=UIColors.PRIMARY), flex_grow=1)
        flex_demo.add_child(Button(0, 0, 230, 30, "Grow 2", background_color=UIColors.SUCCESS), flex_grow=2)
        flex_demo.add_child(Button(0, 0, 230, 30, "Fixed", background_color=UIColors.BUTTON_NORMAL), flex_grow=0)
        
        demo_container.add_child(flex_demo)
        
        main_container.add_child(demo_container, weight=1)


class SettingsPage(UIPage):
    """Settings page with various configuration options"""
    
    def __init__(self):
        super().__init__("settings", 0, 0, 800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        main_layout = LinearLayout(20, 20, 760, 560,
                                 direction=LayoutDirection.VERTICAL,
                                 spacing=15, padding=20,
                                 background_color=UIColors.BACKGROUND)
        self.add_child(main_layout)
        
        # Header
        header = LinearLayout(0, 0, 720, 40,
                            direction=LayoutDirection.HORIZONTAL,
                            spacing=10)
        
        back_btn = Button(0, 0, 80, 30, "Back")
        title = Button(0, 0, 150, 30, "Settings",
                     background_color=UIColors.PRIMARY)
        
        header.add_child(back_btn)
        header.add_child(title)
        main_layout.add_child(header, weight=0)
        
        # Settings sections
        
        # Audio settings
        audio_section = LinearLayout(0, 0, 720, 120,
                                   direction=LayoutDirection.VERTICAL,
                                   spacing=10, padding=10,
                                   background_color=UIColors.SURFACE,
                                   border_color=UIColors.BORDER)
        
        audio_title = Button(0, 0, 100, 25, "Audio",
                           background_color=UIColors.SECONDARY)
        audio_section.add_child(audio_title, weight=0)
        
        # Volume controls
        volume_row = LinearLayout(0, 0, 700, 30,
                                direction=LayoutDirection.HORIZONTAL,
                                spacing=10)
        
        master_vol = Slider(0, 0, 150, 20, min_value=0, max_value=100, value=75,
                          show_value=True, label_format="Master: {:.0f}%")
        music_vol = Slider(0, 0, 150, 20, min_value=0, max_value=100, value=60,
                         show_value=True, label_format="Music: {:.0f}%")
        sfx_vol = Slider(0, 0, 150, 20, min_value=0, max_value=100, value=80,
                       show_value=True, label_format="SFX: {:.0f}%")
        
        volume_row.add_child(master_vol)
        volume_row.add_child(music_vol)
        volume_row.add_child(sfx_vol)
        
        audio_section.add_child(volume_row, weight=0)
        
        # Audio toggles
        audio_toggles = LinearLayout(0, 0, 700, 30,
                                   direction=LayoutDirection.HORIZONTAL,
                                   spacing=20)
        
        mute_toggle = Toggle(0, 0, 80, 25, text="Mute")
        surround_toggle = Toggle(0, 0, 120, 25, text="Surround")
        
        audio_toggles.add_child(mute_toggle)
        audio_toggles.add_child(surround_toggle)
        
        audio_section.add_child(audio_toggles, weight=0)
        
        main_layout.add_child(audio_section, weight=0)
        
        # Graphics settings
        graphics_section = LinearLayout(0, 0, 720, 150,
                                      direction=LayoutDirection.VERTICAL,
                                      spacing=10, padding=10,
                                      background_color=UIColors.SURFACE,
                                      border_color=UIColors.BORDER)
        
        graphics_title = Button(0, 0, 100, 25, "Graphics",
                              background_color=UIColors.SECONDARY)
        graphics_section.add_child(graphics_title, weight=0)
        
        # Resolution dropdown
        res_row = LinearLayout(0, 0, 700, 30,
                             direction=LayoutDirection.HORIZONTAL,
                             spacing=10)
        
        res_options = [
            DropdownOption("800x600", "800 x 600"),
            DropdownOption("1024x768", "1024 x 768"),
            DropdownOption("1920x1080", "1920 x 1080"),
            DropdownOption("2560x1440", "2560 x 1440"),
        ]
        
        resolution_dropdown = Dropdown(0, 0, 150, 25, options=res_options, 
                                     selected_index=0, placeholder="Resolution")
        
        fullscreen_toggle = Toggle(0, 0, 100, 25, text="Fullscreen")
        vsync_toggle = Toggle(0, 0, 80, 25, text="V-Sync")
        
        res_row.add_child(resolution_dropdown)
        res_row.add_child(fullscreen_toggle)
        res_row.add_child(vsync_toggle)
        
        graphics_section.add_child(res_row, weight=0)
        
        # Quality settings
        quality_row = LinearLayout(0, 0, 700, 30,
                                 direction=LayoutDirection.HORIZONTAL,
                                 spacing=20)
        
        quality_options = [
            DropdownOption("low", "Low"),
            DropdownOption("medium", "Medium"),
            DropdownOption("high", "High"),
            DropdownOption("ultra", "Ultra"),
        ]
        
        quality_dropdown = Dropdown(0, 0, 120, 25, options=quality_options,
                                  selected_index=2, placeholder="Quality")
        
        # Radio buttons for renderer
        opengl_radio = RadioButton(0, 0, 80, 25, "renderer", "opengl", "OpenGL")
        vulkan_radio = RadioButton(0, 0, 80, 25, "renderer", "vulkan", "Vulkan")
        
        quality_row.add_child(quality_dropdown)
        quality_row.add_child(opengl_radio)
        quality_row.add_child(vulkan_radio)
        
        graphics_section.add_child(quality_row, weight=0)
        
        # Brightness slider
        brightness_row = LinearLayout(0, 0, 700, 30,
                                    direction=LayoutDirection.HORIZONTAL,
                                    spacing=10)
        
        brightness_slider = Slider(0, 0, 200, 20, min_value=0, max_value=100, value=50,
                                 show_value=True, label_format="Brightness: {:.0f}%")
        
        brightness_row.add_child(brightness_slider)
        graphics_section.add_child(brightness_row, weight=0)
        
        main_layout.add_child(graphics_section, weight=0)
        
        # Action buttons
        button_row = LinearLayout(0, 0, 720, 40,
                                direction=LayoutDirection.HORIZONTAL,
                                spacing=10)
        
        save_btn = Button(0, 0, 100, 35, "Save",
                        background_color=UIColors.SUCCESS)
        reset_btn = Button(0, 0, 100, 35, "Reset",
                         background_color=UIColors.WARNING)
        cancel_btn = Button(0, 0, 100, 35, "Cancel",
                          background_color=UIColors.DANGER)
        
        button_row.add_child(save_btn)
        button_row.add_child(reset_btn)
        button_row.add_child(cancel_btn)
        
        main_layout.add_child(button_row, weight=0)


def main():
    """Main function to run the UI demo"""
    
    # Initialize Pygame
    pygame.init()
    
    # Set up display
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dashr UI System Demo")
    
    # Load font
    try:
        font_dir = os.path.join("client", "assets", "fonts", "default")
        font = FontLoader.load_font_from_directory(font_dir)
    except Exception as e:
        print(f"Failed to load font: {e}")
        print("Make sure you're running from the project root directory")
        return
    
    # Create UI manager
    ui_manager = UIManager(WIDTH, HEIGHT)
    
    # Create and add pages
    main_menu = MainMenuPage()
    layout_demo = LayoutDemoPage()
    settings = SettingsPage()
    
    ui_manager.page_manager.add_page(main_menu)
    ui_manager.page_manager.add_page(layout_demo)
    ui_manager.page_manager.add_page(settings)
    
    # Set initial page
    ui_manager.page_manager.set_current_page("main_menu", immediate=True)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                # Let UI manager handle the event
                ui_manager.handle_event(event)
        
        # Update
        ui_manager.update(dt)
        
        # Render
        screen.fill(UIColors.BACKGROUND)
        ui_manager.render(screen, font)
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
