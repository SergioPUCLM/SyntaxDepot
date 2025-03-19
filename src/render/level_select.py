"""Level select renderer"""

import pygame
import pygame_gui
import logging
import os
import json

LEVEL_FOLDER = "data/level/"
PADDING = 20  # Space between buttons
COLUMNS = 10  # Number of columns in the grid


class LevelSelect:
    def __init__(self, screen, manager, change_scene, game_manager):
        self.screen = screen
        self.manager = manager
        self.change_scene = change_scene
        self.buttons = []
        self.selected_level = None
        self.level_data = {}  # Stores level name & leaderboard info
        
        self.create_ui()


    def create_ui(self):
        """Scans levels and positions buttons in a grid layout."""
        self.manager.clear_and_reset()
        self.buttons.clear()  # Prevents duplication on resize (I hate pygame_gui)

        width, height = self.screen.get_size()
        sidebar_width = int(width * 0.2)  # Sidebar for leaderboard & play button
        grid_width = width - sidebar_width - PADDING

        # Dynamically adjust button size based on screen width
        button_size = max(80, min(150, grid_width // COLUMNS - PADDING))  

        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((sidebar_width, 20), (grid_width, 40)),
            text="Select a Level",
            manager=self.manager,
            object_id="title"
        )

        # Positioning logic for grid
        x_start = sidebar_width + PADDING
        y_start = 80
        x, y = x_start, y_start
        col_count = 0

        for folder in sorted(os.listdir(LEVEL_FOLDER)):  # Locate all level folders
            if not self.is_valid_level(folder):
                continue

            level_number, level_name = folder.split("_", 1)
            leaderboard_path = os.path.join(LEVEL_FOLDER, folder, "leaderboard.json")
                        
            # Load leaderboard if it exists
            leaderboard = self.load_leaderboard(leaderboard_path)
            self.level_data[folder] = {"name": level_name, "leaderboard": leaderboard}

            # Create level button with both number and name
            button_text = f"{level_number}"  # Show the number
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x, y), (button_size, button_size)),
                text=button_text,
                manager=self.manager,
                object_id="level_button"
            )

            self.buttons.append((button, folder))
            
            col_count += 1
            x += button_size + PADDING
            if col_count >= COLUMNS:
                col_count = 0
                x = x_start
                y += button_size + PADDING

        # Sidebar panel to group elements
        self.sidebar_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 40), (sidebar_width, height - 50)),
            starting_height=1.0,
            manager=self.manager,
            object_id="sidebar_panel"
        )

        # Leaderboard texbox (dynamically sized)
        self.leaderboard_textbox = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((15, 50), (sidebar_width - 40, height - 310)),
            html_text="No leaderboard loaded.\n\nClick a level to view it's scores.",
            manager=self.manager,
            object_id="leaderboard",
            container=self.sidebar_panel
        )

        # Leaderboard label (dynamically sized)
        self.leaderboard_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((15, 25), (sidebar_width - 40, 20)),
            text="Leaderboard",
            manager=self.manager,
            object_id="subtitle",
            container=self.sidebar_panel
        )

        # Selected level info
        self.level_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, self.leaderboard_textbox.get_relative_rect().height + 40), (sidebar_width - 40, 80)),
            text="",
            manager=self.manager,
            object_id="label",
            container=self.sidebar_panel
        )
        
        # Play button (dynamically sized)
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((15, self.leaderboard_textbox.get_relative_rect().height + 100), (sidebar_width - 40, 50)),
            text="Play",
            manager=self.manager,
            object_id="good_button",
            container=self.sidebar_panel
        )
        self.play_button.disable()

        # Back button (dynamically sized)
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((15, self.leaderboard_textbox.get_relative_rect().height + 160), (sidebar_width - 40, 50)),
            text="Back",
            manager=self.manager,
            object_id="bad_button",
            container=self.sidebar_panel
        )


    def handle_events(self, event):
        """Handles UI interactions."""
        match event.type:
            case pygame_gui.UI_BUTTON_PRESSED:
                for button, folder in self.buttons:
                    if event.ui_element == button:
                        self.select_level(folder)
                match event.ui_element:
                    case self.play_button if self.selected_level:
                        self.change_scene("game", self.selected_level, os.path.join(LEVEL_FOLDER, self.selected_level))
                    case self.back_button:
                        self.change_scene("menu")
            case pygame.QUIT:
                self.change_scene(None)
            case _:
                pass


    def select_level(self, folder):
        """
        Highlights selected level and updates UI.

        Args:
            folder (str): Folder name of the selected level.
        """
        self.selected_level = folder
        level_info = self.level_data[folder]
        self.level_label.set_text(f"Level: {level_info['name']}")
        self.level_label.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
        self.play_button.enable()
        
        # Load the leaderboard data from level_data
        leaderboard = level_info["leaderboard"]

        
        if leaderboard:  # If there's data
            leaderboard_html = ""
            i = 0
            for entry in leaderboard:
                i += 1
                leaderboard_html += f"{i}. {entry['steps']} Steps<br>"
        else:
            leaderboard_html = "No leaderboard data available."

        self.leaderboard_textbox.set_text(leaderboard_html)


    def load_leaderboard(self, filepath):
        """
        Loads leaderboard data from JSON.
        
        Args:
            filepath (str): Path to the leaderboard file.
        
        Returns:
            list: A list of dictionaries with leaderboard data. (Empty if file not found or invalid)
        """
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                try:
                    return json.load(file)  # Load entire JSON file as a list
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON in {filepath}")
                    return []  # Return empty list if there's a parsing error
        else:
            logging.debug(f"Leaderboard not found: {filepath}")
            return []  # Return empty list instead of a string

            return output
    

    def is_valid_level(self, folder_name):
        """Checks if the folder name follows the correct format (X_Name)."""
        return folder_name.count("_") == 1 and folder_name.split("_")[0].isdigit()


    def update(self, time_delta):
        """Updates the UI manager."""
        self.manager.update(time_delta)


    def render(self):
        """Draws the UI elements."""
        self.screen.fill((0, 0, 0))
        self.manager.draw_ui(self.screen)


    def resize(self):
        """Recreates UI elements on window resize."""
        self.manager.clear_and_reset()
        self.create_ui()
    

    def destroy(self):
        """Clears UI elements."""
        logging.debug("Destroying level select scene")
        self.manager.clear_and_reset()


