"""Main Menu Renderer"""

import pygame
import pygame_gui
import logging
from src.render.missing_image import missing_texture_pygame


class MainMenu:
    def __init__(self, screen, manager, change_scene):
        global BG_TILE
        self.screen = screen
        self.manager = manager
        self.change_scene = change_scene

        self.elements = {}  # Store UI elements for easy updates
        self.create_ui()


    def create_ui(self):
        """
        Creates and positions UI elements dynamically.
        Elements require to be defined as class attributes to be accessible in the event handler.
        """
        width, height = self.screen.get_size()

        # Title label
        self.elements["title"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((width * 0.25, height * 0.1), (width * 0.5, height * 0.1)),
            text="Syntax Depot",
            manager=self.manager,
            object_id="title",
            
        )

        # Play button
        self.elements["play_button"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width * 0.35, height * 0.4), (width * 0.3, height * 0.1)),
            text="Play",
            manager=self.manager,
            object_id="good_button"
        )

        # Exit button
        self.elements["exit_button"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width * 0.35, height * 0.6), (width * 0.3, height * 0.1)),
            text="Exit",
            manager=self.manager,
            object_id="bad_button"
        )


    def handle_events(self, event):
        """
        Handles the events in this scene.
        
        Args:
            event (pygame.event.Event): Event to handle.
        """
        match event.type:
            case pygame_gui.UI_BUTTON_PRESSED:
                match event.ui_element:
                    case element if element is self.elements["exit_button"]:
                        self.change_scene(None)
                    case element if element is self.elements["play_button"]:
                        self.change_scene("level_select")
            case pygame.QUIT:
                self.change_scene(None)
            case _:  # Ignore other events
                pass


    def update(self, time_delta):
        """
        Updates the UI manager, therefore refreshing the screen.
        """
        self.manager.update(time_delta)


    def render(self):
        """
        Renders the UI elements on the screen.
        """
        self.screen.fill((0, 0, 0))  # Black background
        self.manager.draw_ui(self.screen)


    def resize(self):
        """
        Recreates UI elements on window resize to achieve responsive design.
        """
        self.manager.clear_and_reset()  # Clear UI and recreate
        self.create_ui()


    def destroy(self):
        """
        Destroys the UI manager and its elements.
        """
        logging.debug("Destroying main menu scene")
        self.manager.clear_and_reset()