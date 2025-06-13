"""Game manager class"""

import os
import pygame
import logging
from src.level.load_level import load_level
from src.script.parser import parse_code
from src.script.ast_nodes import *
from src.script.interpreter import CoroutineInterpreter
from src.entities.crate import Crate
from src.render.error_handler import error_handler, ErrorLevel
from src.render.sound_manager import sound_manager

LEVEL_FOLDER = "data/level/"  # Folder where the levels are stored
PLAYER_SCRIPTS = "script/"
TRAP_DELAY_DEFAULT = 1  # Default delay for traps (in ticks)


class GameManager:
    def __init__(self):
        self.current_level = None
        self.level_folder = None
        self.is_running = False  # Whether the game is active (robots are moving)
        self.frame_count = 0
        self.camera_robot = None  # The robot that the camera is over
        self.trap_delay = TRAP_DELAY_DEFAULT  # Delay for traps
        self.coroutines = {}
        self.finished_robots = []  # List of finished robots
        self.success = True  # Whether the level was completed successfully (No errors or warnings happened)
        self.steps_taken = 0  # Number of steps taken in the level (for leaderboard purposes)
        self.completed = False  # Whether the level was completed
        self.needs_ui_update = False  # Flag to indicate if the code ui needs to be updated

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


    def remove_from_list(self, entity):  # Remove an entity from the list
        """
        Removes an entity from the list.

        Args:
            entity (Entity): Entity to remove.
        """
        string_height = None
        match entity.height:
            case 0:
                string_height = "tile"
            case 1:
                string_height = "ground"
            case 2:
                string_height = "air"
            case 3:
                string_height = "camera"
            case _:
                logging.error(f"Invalid height for entity: {entity.height}")
                return
        if string_height in self.entity_list:
            if entity in self.entity_list[string_height]:
                self.entity_list[string_height].remove(entity)


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
            self.frame_count = 0
            self.update_entities()
            self.current_level.remove_callback = self.remove_from_list  # Set the callback to remove entities from the list
            self.trap_delay = TRAP_DELAY_DEFAULT  # Reset the trap delay
            self.finished_robots = []  # Reset the finished robots list
            self.coroutines = {}  # Reset the coroutines
            self.success = True  # Reset the success flag
            self.steps_taken = 0  # Reset the steps taken
            self.completed = False  # Reset the completed flag
        else:
            logging.error(f"Failed to load level: {level_folder}")


    def start_game(self, player_name):
        """Starts the game, enabing robot movement."""
        if self.current_level and self.is_running == False:  # Check if a level is loaded and the game is not already running
            self.is_running = True
            self.frame_count = 0
            self.compile_scripts(player_name)
            sound_manager.play("play", fade_ms=500)
        else:
            logging.error("Cannot start game without a level loaded")


    def reset_level(self):
        """Resets the current level, resetting all entities to their original positions and pausing the game."""
        self.needs_ui_update = True
        self.load_level(self.level_folder)
        self.is_running = False  # Stop the game
        sound_manager.play("reset_level")  # Play reset sound
        sound_manager.play("think", fade_ms=500)


    def exit_to_menu(self):
        """Exits the game to the main menu."""
        logging.debug("Exiting to menu")
        self.is_running = False
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
            if tile.entities['air'].__class__.__name__.lower() == "green":
                self.camera_robot = "green"
            else:
                self.camera_robot = None
        elif tile.entities['ground']:
            if tile.entities['ground'].__class__.__name__.lower() == "red":
                self.camera_robot = "red"
            elif tile.entities['ground'].__class__.__name__.lower() == "blue":
                self.camera_robot = "blue"
            else:
                self.camera_robot = None
        else:
            self.camera_robot = None


    def save_script(self, script, player_name):
        """Save the current script to a file."""
        message = "Simulation running...\n\nScript editing is disabled."
        if self.camera_robot and self.is_running == False and script != message:  # Save only if the game is not running
            # Create scripts folder if it doesn't exist
            if not os.path.exists(os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS)):
                os.makedirs(os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS))
            file = os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS, f"{self.camera_robot}_{player_name}.sds")
            with open(file, "w") as f:
                f.write(script)

    
    def load_script(self, player_name):
        """Load a script from a file."""
        script = ""
        if self.camera_robot:
            if not os.path.exists(os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS)):
                os.makedirs(os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS))
            file = os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS, f"{self.camera_robot}_{player_name}.sds")
            if os.path.exists(file):
                with open(file, "r") as f:
                    script = f.read()
                script = script.strip()  # Remove leading and trailing whitespace
            return script
        else:
            logging.error("Cannot load script without a robot selected")
            return ""


    def compile_scripts(self, player_name):
        present_robots = []
        for robot in self.entity_list['air']:
            if robot.__class__.__name__.lower() == "green":
                present_robots.append(robot)
        for robot in self.entity_list['ground']:
            if robot.__class__.__name__.lower() == "red" or robot.__class__.__name__.lower() == "blue":
                present_robots.append(robot)
        
        for robot in present_robots:
            if not os.path.exists(os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS)):
                os.makedirs(os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS))
            file = os.path.join(LEVEL_FOLDER, self.level_folder, PLAYER_SCRIPTS, f"{robot.__class__.__name__.lower()}_{player_name}.sds")
            if os.path.exists(file):
                with open(file, "r") as f:
                    script = f.read()
                script = script.strip()
                robot.script = script

                try:
                    tree = parse_code(robot.script)
                    interpteter = CoroutineInterpreter(self.current_level, robot)
                    coroutine = interpteter.run(tree)
                    next(coroutine)
                    self.coroutines[robot] = coroutine
                    logging.debug(f"Coroutine for {robot.__class__.__name__} created")
                except SyntaxError as e:
                    error_handler.push_error(
                        "Script Syntax Error",
                        f"Error in {robot.__class__.__name__}'s script:\n{e}",
                        ErrorLevel.ERROR
                    )
                    logging.error(f"Syntax error in {robot.__class__.__name__}'s script: {e}")
                    self.reset_level()
                except StopIteration as e:
                    error_handler.push_error(
                        "Script Error",
                        f"{robot.__class__.__name__}'s script has finished. No actions were detected.",
                        ErrorLevel.ERROR
                    )
                    logging.error(f"Script for {robot.__class__.__name__} has no movement commands")
                    self.success = False
                    self.finished_robots.append(robot)
                    continue
                except Exception as e:
                    if robot.script != "":  # Only trigger if the script is not empty
                        error_handler.push_error(
                            "Script Error",
                            f"Could not load the script for: {robot.__class__.__name__}\nError: {str(e)}",
                            ErrorLevel.ERROR
                        )
                        logging.error(f"Failure to initialize script for {robot.__class__.__name__}: {e}")
                    self.finished_robots.append(robot)  # If the script is empty, mark the robot as finished too
            else:
                error_handler.push_error(
                    "Script Problem",
                    f"{robot.__class__.__name__.lower()} does not have a script set\nMake sure you made a script and it saved.",
                    ErrorLevel.WARNING
                )
                logging.error(f"Script file for {robot.__class__.__name__.lower()}_{player_name}.sds not found. Make sure you made a script for it and it saved.")
                self.success = False
                self.finished_robots.append(robot)

    
    def check_completion(self):
        """Checks if the level is completed."""
        if not self.current_level:
            return False  # If the level is not loaded

        objectives_met = True
        for objective, target in self.current_level.objectives.items():
            if objective != "collectables":
                if self.completed_objectives[objective] < target:
                    objectives_met = False
                    break
        
        present_robots = []
        for robot in self.entity_list['air']:
            if robot.__class__.__name__.lower() == "green":
                present_robots.append(robot)
        for robot in self.entity_list['ground']: 
            if robot.__class__.__name__.lower() == "red" or robot.__class__.__name__.lower() == "blue":
                present_robots.append(robot)

        all_robots_finished = True
        for robot in present_robots:
            if robot not in self.finished_robots:
                all_robots_finished = False
                break

        # If all the robots are finished BUT the level is not completed, reset the level
        if all_robots_finished and not objectives_met:
            logging.error("All robots finished, but objectives were not completed. The level was restarted.")
            error_handler.push_error(
                "Execution Error",
                f"All robots finished, but objectives not met. Resetting level.",
                ErrorLevel.ERROR
            )
            self.reset_level()

        return objectives_met and all_robots_finished and self.current_level.success and self.success

    
    def calculate_score(self):
        """Calculates the score based on the completed objectives."""
        if not self.success or not self.current_level:
            return 0

        base_percentage = 0.5  # Base percentage for score calculation
        picked_collectables = self.completed_objectives["collectables"]
        total_collectables = self.current_level.objectives["collectables"]
        if total_collectables > 0:
            collectable_percentage = 1 + (picked_collectables / total_collectables) * base_percentage
        else:
            collectable_percentage = 1
        return int(self.steps_taken / collectable_percentage)


    def tick(self):
        """Updates the game state."""
        if self.is_running:
            self.frame_count += 1
            if self.frame_count % 30 == 0:  # 60 for Every second, 30 is normal
                occupied_chargepads = 0
                active_terminals = 0
                present_collectables = 0


                # Step 0: Update trap delay (if larger than 0, decrease it, if 0 or under, reset it) and toggle traps
                if self.trap_delay > 0:
                    self.trap_delay -= 1
                elif self.trap_delay <= 0:
                    self.trap_delay = TRAP_DELAY_DEFAULT
                else:
                    logging.error("Trap delay is negative. Resetting to default.")
                    self.trap_delay = TRAP_DELAY_DEFAULT

                for tile_entity in self.entity_list['tile']:
                    # Step 0.1: Toggle traps
                    if tile_entity.__class__.__name__.lower() == "trap":
                        if self.trap_delay <= 0:  # If the trap delay is 0, toggle the trap
                            tile_entity.active = not tile_entity.active
                            if tile_entity.active:
                                sound_manager.play("trap_activate")
                        # Check if a robot is above the trap, if trap is active, fail the level and reset
                        if tile_entity.active and self.current_level.tiles[tile_entity.y][tile_entity.x].entities['ground'] is not None:
                            if self.current_level.tiles[tile_entity.y][tile_entity.x].entities['ground'].__class__.__name__.lower() in ["red", "blue"]:
                                logging.error("Robot stepped on a trap. Level failed.")
                                error_handler.push_error(
                                    "Execution Error",
                                    f"Robot stepped on an active trap. Level failed.",
                                    ErrorLevel.ERROR
                                )
                                self.reset_level()
                                break
                
                # Step 1: Advance robot scripts (green > blue > red)
                for robot, coroutine in self.coroutines.items():
                    try:
                        next(coroutine)  # Advance coroutine
                    except StopIteration:
                        if robot not in self.finished_robots:
                            self.finished_robots.append(robot)
                            logging.info(f"{robot.__class__.__name__} has finished its script.")
                            error_handler.push_error(
                                "Script Finished",
                                f"{robot.__class__.__name__} has finished its script.",
                                ErrorLevel.INFO
                            )
                    except Exception as e:
                        error_handler.push_error(
                            f"Script Error: {robot.__class__.__name__}",
                            f"{e}",
                            ErrorLevel.ERROR
                        )
                        logging.error(f"Error while executing robot script for {robot}: {e}")
                        self.success = False

                # Step 2: Update tile entities
                    # Step 2.1: Check chargepads
                    if tile_entity.__class__.__name__.lower() == "chargepad":
                        # If a robot is above them
                        entity_above = self.current_level.tiles[tile_entity.y][tile_entity.x].entities['ground']
                        if entity_above:
                            if entity_above.__class__.__name__.lower() in ["red", "blue"]:
                                occupied_chargepads += 1

                    # Step 2.2: Check crate generators
                    if tile_entity.__class__.__name__.lower() == "crategen":
                        # If nothing is above them
                        if self.current_level.tiles[tile_entity.y][tile_entity.x].entities['ground'] is None:
                            new_crate = None
                            if tile_entity.active:  # If the crate generator is active
                                match tile_entity.crate_type:
                                    case "small":
                                        new_crate = Crate(tile_entity.x, tile_entity.y, 1, True)
                                    case "big":
                                        new_crate = Crate(tile_entity.x, tile_entity.y, 1, False)
                                    case _:
                                        new_crate = None
                                tile_entity.active = False  # Deactivate the crate generator
                            else:
                                tile_entity.active = True  # Activate the crate generator
                            if new_crate and tile_entity.crate_count > 0:
                                self.current_level.tiles[tile_entity.y][tile_entity.x].entities['ground'] = new_crate
                                self.entity_list['ground'].append(new_crate)  # Add the crate to the entity list
                                tile_entity.crate_count -= 1
                                sound_manager.play("crate_spawn")  # Play crate spawn sound
                    
                    # Step 2.3: Check crate deletors
                    if tile_entity.__class__.__name__.lower() == "cratedel":
                        # If a crate is above them
                        entity_above = self.current_level.tiles[tile_entity.y][tile_entity.x].entities['ground']
                        if entity_above:
                            if entity_above.__class__.__name__.lower() == "crate":
                                if tile_entity.active:  # If the crate deletor is active
                                    # Delete the crate
                                    self.current_level.remove_entity(entity_above)
                                    sound_manager.play("crate_delete")  # Play crate delete sound

                                    # Update the completed objectives
                                    if entity_above.small:
                                        self.completed_objectives["crates_small"] += 1
                                    else:
                                        self.completed_objectives["crates_large"] += 1
                                    tile_entity.active = False  # Deactivate the crate deletor
                                else:
                                    tile_entity.active = True  # Activate the crate deletor

                # Step 3: Update ground entities
                for ground_entity in self.entity_list['ground']:
                    # Step 3.1: Check terminals
                    if ground_entity.__class__.__name__.lower() == "inputter" and ground_entity.activated:
                        active_terminals += 1

                    # Step 3.2: Check collectables
                    if ground_entity.__class__.__name__.lower() == "collectable":
                        present_collectables += 1

                # Step 4: Update air entities
                for air_entity in self.entity_list['air']:
                    # Step 4.1: Check collectables
                    if air_entity.__class__.__name__.lower() == "collectable":
                        present_collectables += 1

                # Step 5: Update objectives
                self.completed_objectives["charge_pads"] = occupied_chargepads
                self.completed_objectives["terminals"] = active_terminals
                collectables_picked = self.current_level.objectives["collectables"] - present_collectables
                self.completed_objectives["collectables"] = collectables_picked

                # Step 6: Increase steps taken
                self.steps_taken += 1

                # Step 7: Check if all robots finished execution and completion
                self.completed = self.check_completion()

        else:
            self.frame_count = 0
