"""Error handler class"""

import pygame
import pygame_gui
import logging
from enum import Enum, auto
from typing import Optional, Tuple
from src.render.missing_image import missing_texture_pygame

ICON_FOLDER = "res/sprites/"

class ErrorLevel(Enum):
    """
    Enum to represent the severity level of an error.
    """
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

class ErrorHandler:
    """
    Singleton class to handle error messages and display them using pygame_gui.
    It manages a queue of error messages and displays them in a panel with an icon, title, and message.
    It uses singleton to configure a global error handler instance.

    Attributes:
        ui_manager (pygame_gui.UIManager): The UI manager instance for rendering the error panel.
        current_panel (Optional[pygame_gui.elements.UIPanel]): The currently active error panel.
        error_queue (list): A queue to store error messages to be displayed.
        icons (dict): A dictionary mapping error levels to their respective icons.

    Methods:
        set_ui_manager(manager: pygame_gui.UIManager): Set the UI manager for rendering.
        push_error(title: str, message: str, level=ErrorLevel.ERROR): Queue an error with title, message, and severity level.
        _process_queue(): Process the error queue and display the next error if no current panel is active.
        _show_error(title: str, message: str, level: ErrorLevel): Create the error panel with icon, title, and message.
        dismiss_current(): Manually dismiss the current error.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.ui_manager = None
            cls._instance.current_panel = None
            cls._instance.error_queue = []

            cls._instance.icons = {
                ErrorLevel.INFO: None,
                ErrorLevel.WARNING: None,
                ErrorLevel.ERROR: None
            }
        return cls._instance


    def load_icons(self):
        """Load icons for different error levels"""
        try:
            self.icons[ErrorLevel.INFO] = pygame.image.load(ICON_FOLDER + "info.png").convert_alpha()
        except FileNotFoundError:
            self.icons[ErrorLevel.INFO] = missing_texture_pygame(size_x=32, size_y=32)
            logging.error("Info icon not found. Using fallback texture")

        try:
            self.icons[ErrorLevel.WARNING] = pygame.image.load(ICON_FOLDER + "warning.png").convert_alpha()
        except FileNotFoundError:
            self.icons[ErrorLevel.WARNING] = missing_texture_pygame(size_x=32, size_y=32)
            logging.error("Warning icon not found. Using fallback texture")

        try:
            self.icons[ErrorLevel.ERROR] = pygame.image.load(ICON_FOLDER + "error.png").convert_alpha()
        except FileNotFoundError:
            self.icons[ErrorLevel.ERROR] = missing_texture_pygame(size_x=32, size_y=32)
            logging.error("Error icon not found. Using fallback texture")


    def set_ui_manager(self, manager: pygame_gui.UIManager):
        self.ui_manager = manager


    def push_error(self, title, message, level=ErrorLevel.ERROR):
        """Queue an error with title, message, and severity level"""
        self.error_queue.append((title, message, level))
        self._process_queue()

    def _process_queue(self):
        """Process the error queue and display the next error if no current panel is active"""
        if not self.current_panel and self.error_queue and self.ui_manager:
            title, message, level = self.error_queue.pop(0)
            self._show_error(title, message, level)

    def _show_error(self, title, message, level):
        """
        Create the error panel with icon, title, and message

        Args:
            title (str): Title of the error message
            message (str): Message content
            level (ErrorLevel): Severity level of the error
        """
        padding = 10
        icon_height = 32
        title_height = 32
        button_height = 30
        spacing = 3 * padding
        
        # Calculate required dimensions
        font = self.ui_manager.get_theme().get_font(["error_message_textbox"])
        text_width = 400 - 2 * padding
        
        # Estimate text height
        text_lines = message.split('\n')
        line_height = font.get_point_size()
        estimated_text_height = max(100, len(text_lines) * line_height + 20)  # Minimum 100px
        
        # Calculate panel height based on content
        panel_height = (4 * padding + title_height + 
                        estimated_text_height +
                        button_height)
        
        # Set panel width (could also make this dynamic if needed)
        panel_width = 400
        
        # Position panel in top-left corner
        panel_rect = pygame.Rect(
            padding,  # x position (from left)
            padding,  # y position (from top)
            panel_width,
            panel_height
        )

        self.current_panel = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            starting_height=1000,
            object_id=f"error_panel_{level.name.lower()}"
        )

        # Add icon
        icon_rect = pygame.Rect(padding, padding, icon_height, icon_height)
        pygame_gui.elements.UIImage(
            relative_rect=icon_rect,
            image_surface=self.icons[level],
            manager=self.ui_manager,
            container=self.current_panel
        )

        # Add title
        title_rect = pygame.Rect(
            padding + icon_height + padding, 
            padding, 
            panel_width - (icon_height + 3 * padding), 
            title_height
        )
        pygame_gui.elements.UILabel(
            relative_rect=title_rect,
            text=title,
            manager=self.ui_manager,
            container=self.current_panel,
            object_id="error_title"
        )

        # Add message box (centered below)
        message_rect = pygame.Rect(
            padding,
            padding + title_height + padding,
            panel_width - 3 * padding,
            estimated_text_height
        )
        pygame_gui.elements.UITextBox(
            relative_rect=message_rect,
            html_text=message,
            manager=self.ui_manager,
            container=self.current_panel,
            object_id="error_message_textbox"
        )

        # Add OK button
        button_rect = pygame.Rect(
            panel_width - 80 - padding,
            panel_height - button_height - 1.5 * padding,
            80,
            button_height
        )
        self._ok_button = pygame_gui.elements.UIButton(
            relative_rect=button_rect,
            text="OK",
            manager=self.ui_manager,
            container=self.current_panel,
            #object_id="error_ok_button"
            object_id="good_button"
        )

        self._last_show_time = pygame.time.get_ticks()


    def dismiss_current(self):
        """Manually dismiss the current error"""
        if self.current_panel:
            self.current_panel.kill()
            self.current_panel = None
        self._process_queue()


    def dismiss_all(self):
        """Manually dismiss all errors"""
        while self.current_panel:
            self.dismiss_current()
        self.error_queue.clear()

    
    def update(self, time_delta):
        """Call this every frame to handle auto-dismiss timing and button events."""
        if self.current_panel:
            # Handle auto-dismiss for INFO and WARNING
            if any(id.endswith("_info") or id.endswith("_warning") for id in self.current_panel.object_ids):
                if pygame.time.get_ticks() - self._last_show_time > 5000:
                    self.dismiss_current()

            # Check if OK button was pressed
            for event in pygame.event.get():
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self._ok_button:
                        self.dismiss_current()


# Global instance
error_handler = ErrorHandler()