"""Level select renderer"""

import pygame
import pygame_gui
import logging
import os
import json
from src.render.sound_manager import sound_manager

LEVEL_FOLDER = "data/level/"
PLAYER_FOLDER = "data/player/"
OPTIONS_FILE = "data/options.json"
PADDING = 20  # Space between buttons
COLUMNS = 10  # Number of columns in the grid


class LevelSelect:
    def __init__(self, screen, manager, change_scene, game_manager):
        self.screen = screen
        self.manager = manager
        self.change_scene = change_scene
        self.game_manager = game_manager
        self.buttons = []
        self.selected_level = None
        self.level_data = {}  # Stores level name & leaderboard info
        self.player_level = self.load_player_level()  # Load player level from JSON (Last level played)
        
        self.create_ui()


    def create_ui(self):
        """Scans levels and positions buttons in a scrollable grid layout that adapts to screen size."""
        self.manager.clear_and_reset()
        self.buttons.clear()

        # Screen and layout sizing
        width, height = self.screen.get_size()
        sidebar_width = int(width * 0.25)
        grid_width = width - sidebar_width - PADDING
        panel_height = height - 100

        # Determine optimal button size and column count dynamically
        min_button_size = 80
        max_button_size = 150
        for columns in range(20, 0, -1):
            btn_candidate = (grid_width - (columns + 1) * PADDING) // columns
            if min_button_size <= btn_candidate <= max_button_size:
                COLUMNS = columns
                button_size = btn_candidate
                break
        else:
            COLUMNS = 1
            button_size = min_button_size

        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((sidebar_width, 20), (grid_width, 40)),
            text="Select a Level",
            manager=self.manager,
            object_id="title"
        )

        # Scrollable grid panel
        self.level_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((sidebar_width + 15, 70), (grid_width, panel_height)),
            starting_height=1,
            manager=self.manager,
            object_id="level_panel",
        )
        container = self.level_panel.get_container()

        # Grid layout logic
        x_start, y_start = PADDING, PADDING
        x, y = x_start, y_start
        col_count = 0

        for folder in sorted(os.listdir(LEVEL_FOLDER)):
            # Skip non-directory items
            if not os.path.isdir(os.path.join(LEVEL_FOLDER, folder)):
                continue

            if not self.is_valid_level(folder):
                continue

            level_number, level_name = folder.split("_", 1)
            leaderboard_path = os.path.join(LEVEL_FOLDER, folder, "leaderboard.json")
            leaderboard = self.load_leaderboard(leaderboard_path)
            self.level_data[folder] = {"name": level_name, "leaderboard": leaderboard}

            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x, y), (button_size, button_size)),
                text=f"{level_number}",
                manager=self.manager,
                container=container,
                object_id="level_button"
            )

            if self.player_level + 1 < int(level_number):
                button.disable()
            else:
                button.enable()

            self.buttons.append((button, folder))

            col_count += 1
            x += button_size + PADDING
            if col_count >= COLUMNS:
                col_count = 0
                x = x_start
                y += button_size + PADDING

        # Sidebar
        self.sidebar_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 40), (sidebar_width, height - 50)),
            starting_height=1.0,
            manager=self.manager,
            object_id="sidebar_panel"
        )

        self.leaderboard_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((15, 25), (sidebar_width - 40, 20)),
            text="Leaderboard",
            manager=self.manager,
            object_id="subtitle",
            container=self.sidebar_panel
        )

        self.leaderboard_textbox = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((15, 50), (sidebar_width - 40, height - 310)),
            html_text="No leaderboard loaded.\n\nClick a level to view its scores.",
            manager=self.manager,
            object_id="leaderboard",
            container=self.sidebar_panel
        )

        self.level_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, self.leaderboard_textbox.get_relative_rect().height + 40), (sidebar_width - 40, 80)),
            text="",
            manager=self.manager,
            object_id="label",
            container=self.sidebar_panel
        )

        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((15, self.leaderboard_textbox.get_relative_rect().height + 100), (sidebar_width - 40, 50)),
            text="Play",
            manager=self.manager,
            object_id="good_button",
            container=self.sidebar_panel
        )
        self.play_button.disable()

        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((15, self.leaderboard_textbox.get_relative_rect().height + 160), (sidebar_width - 40, 50)),
            text="Back",
            manager=self.manager,
            object_id="bad_button",
            container=self.sidebar_panel
        )

    
    def load_player_level(self):
        """Loads player highest level from JSON. Creates file if missing."""
        player_name = "Anonymous"  # Default player name
        player_level = 1  # Default level

        # Load last player name from options file
        if os.path.exists(OPTIONS_FILE):
            try:
                with open(OPTIONS_FILE, "r") as file:
                    options = json.load(file)
                    player_name = options.get("last_player", "Anonymous")
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON in {OPTIONS_FILE}")

        # Ensure player folder exists
        os.makedirs(PLAYER_FOLDER, exist_ok=True)

        player_file = os.path.join(PLAYER_FOLDER, f"{player_name}.json")

        # Load or create player file
        if os.path.exists(player_file):
            try:
                with open(player_file, "r") as file:
                    player_data = json.load(file)
                    player_level = player_data.get("highest_level", 1)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON in {player_file}")
        else:
            # Create the file with default level
            with open(player_file, "w") as file:
                json.dump({"highest_level": 0}, file)

        return player_level


    def handle_events(self, event):
        """Handles UI interactions."""
        match event.type:
            case pygame_gui.UI_BUTTON_PRESSED:
                sound_manager.play("click")
                for button, folder in self.buttons:
                    if event.ui_element == button:
                        self.select_level(folder)
                match event.ui_element:
                    case self.play_button if self.selected_level:
                        self.game_manager.load_level(self.selected_level)  # Preload level
                        if self.game_manager.current_level:
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
                leaderboard_html += f"{i}.{entry['name']}<br>{entry['steps_taken']} Steps<br>{entry['collectables']}% Drives<br>Score: {entry['score']}<br><br>"
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
        success = True
        if not folder_name.count("_") == 1 and folder_name.split("_")[0].isdigit():
            success = False
        
        # Check if a structure.json file is present in the folder
        structure_path = os.path.join(LEVEL_FOLDER, folder_name, "structure.json")
        if not os.path.exists(structure_path):
            logging.debug(f"Missing structure.json in {folder_name}")
            success = False
        return success


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


