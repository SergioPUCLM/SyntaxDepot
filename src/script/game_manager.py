"""Game manager class"""

import os
import pygame
import logging
from src.level.load_level import load_level

LEVEL_FOLDER = "data/level/"

class GameManager:
    def __init__(self):
        self.current_level = None
        self.level_folder = None
        self.is_running = False  # Whether the game is active (robots are moving)
        self.is_paused = False
        self.frame_count = 0
        self.camera_robot = None  # The robot that the camera is over

        self.entity_list = {  # Store entities for easy updates
            'tile': [],
            'ground': [],
            'air': [],
            'camera': []
        }

        self.completed_objectives = {  # Compare this dictionary with the current_level one
            "charge_pads": 0,
            "crates_small": 0,
            "crates_large": 0,
            "terminals": 0,
            "collectables": 0,
        }


    def update_entities(self):  # Scan the level for entities
        """
        Updates the entity list.
        WARNING: This method's overhead is massive. When making movements and changes, update the list instead of re-scanning.
        """
        if self.current_level:  # Reset the entity list
            self.entity_list = {
                'tile': [],
                'ground': [],
                'air': [],
                'camera': []
            }

            for x in range(self.current_level.width):
                for y in range(self.current_level.height):
                    tile = self.current_level.tiles[y][x]
                    for key, entity in tile.entities.items():
                        if entity:
                            self.entity_list[key].append(entity)

                            # Print the entity
                            logging.debug(f"Entity: {entity} at ({x}, {y}). Height {entity.height}")
        else:
            logging.error("Cannot update entities without a level loaded")


    def load_level(self, level_folder):
        """
        Loads a level from a folder.
        
        Args:
            level_folder (str): Folder name of the level.
        """
        logging.debug(f"Loading level: {level_folder}")
        self.current_level = load_level(level_folder)

        if self.current_level:
            logging.info(f"Level loaded")
            self.level_folder = level_folder
            self.camera_robot = None
            self.completed_objectives = {  # Reset the objectives
                "charge_pads": 0,
                "crates_small": 0,
                "crates_large": 0,
                "terminals": 0,
                "collectables": 0,
            }
            self.is_running = False
            self.is_paused = False
            self.frame_count = 0
            self.update_entities()
        else:
            logging.error(f"Failed to load level: {level_folder}")


    def start_game(self):
        """Starts the game, enabing robot movement."""
        logging.debug("Starting game")
        if self.current_level:
            self.is_running = True
            self.is_paused = False
            logging.info("Game started")
        else:
            logging.error("Cannot start game without a level loaded")


    def reset_level(self):
        """Resets the current level, resetting all entities to their original positions and pausing the game."""
        self.load_level(self.level_folder)
        self.is_running = False  # Stop the game
        logging.info("Level reset.")


    def pause_game(self):
        """Pauses or resumes the game."""
        if self.is_running:
            self.is_paused = not self.is_paused
            logging.info(f"Game {'paused' if self.is_paused else 'resumed'}.")


    def exit_to_menu(self):
        """Exits the game to the main menu."""
        logging.debug("Exiting to menu")
        self.is_running = False
        self.is_paused = False
        self.current_level = None
        logging.info("Exited to menu")


    def move_camera(self, direction):
        """
        Moves the camera in a direction.
        
        Args:
            direction (str): Direction to move in. (up, down, left, right)
        """
        if self.current_level:
            camera_x, camera_y = self.current_level.get_camera_position()
            camera_obj = self.current_level.tiles[camera_y][camera_x]
            self.current_level.move_entity(camera_obj.entities['camera'], direction)
            self.update_selected_robot()
        else:
            logging.error("Cannot move camera without a level loaded")


    def update_selected_robot(self):
        """Updates the selected robot."""
        camera_x, camera_y = self.current_level.get_camera_position()
        camera_obj = self.current_level.tiles[camera_y][camera_x]
        tile = self.current_level.tiles[camera_y][camera_x]
        if tile.entities['air']:
            logging.debug(f"Camera entity: {tile.entities['air']}")
            if tile.entities['air'].__class__.__name__.lower() == "green":
                self.camera_robot = "green"
            else:
                self.camera_robot = None
        elif tile.entities['ground']:
            logging.debug(f"Camera entity: {tile.entities['ground']}")
            if tile.entities['ground'].__class__.__name__.lower() == "red":
                self.camera_robot = "red"
            elif tile.entities['ground'].__class__.__name__.lower() == "blue":
                self.camera_robot = "blue"
            else:
                self.camera_robot = None
        else:
            logging.debug(f"Camera entity: None")
            self.camera_robot = None


    def save_script(self, script):
        """Save the current script to a file."""
        if self.camera_robot:
            file = os.path.join(LEVEL_FOLDER, self.level_folder, f"{self.camera_robot}.txt")
            logging.debug(f"Saving script to {file}")
            with open(file, "w") as f:
                f.write(script)
        else:
            logging.error("Cannot save script without a robot selected")

    
    def load_script(self):
        """Load a script from a file."""
        script = ""
        if self.camera_robot:
            file = os.path.join(LEVEL_FOLDER, self.level_folder, f"{self.camera_robot}.txt")
            if os.path.exists(file):
                with open(file, "r") as f:
                    script = f.read()
                script = script.strip()  # Remove leading and trailing whitespace
            return script
        else:
            logging.error("Cannot load script without a robot selected")
            return ""


    def tick(self):
        """Updates the game state."""
        if self.is_running and not self.is_paused:
            self.frame_count += 1
            if self.frame_count % 60 == 0:  # Every second
                logging.debug("PLACE HOLDER: Game tick")

        else:
            self.frame_count = 0