"""
Level loadermodule.

This module is responsible for loading a level from a specified folder.
It reads the level structure from a JSON file and background map, validates the entities, and creates a Level object.
It also performs various checks to ensure the level is valid, such as checking for required robots, charge pads, and terminals.

Methods:
    load_level(folder): Loads a level from the specified folder and returns a Level object or None if an error occurs.
"""

import os
import logging
import json
from src.level.level import Level
from src.level.tile import Tile
from src.entities.blue import Blue
from src.entities.camera import Camera
from src.entities.charge_pad import ChargePad
from src.entities.collectable import Collectable
from src.entities.crate_del import CrateDel
from src.entities.crate_gen import CrateGen
from src.entities.crate import Crate
from src.entities.green import Green
from src.entities.input_ter import InputTer
from src.entities.output_ter import OutputTer
from src.entities.red import Red
from src.entities.trap import Trap
from src.render.error_handler import error_handler, ErrorLevel

DEFAULT_LEVEL_PATH = "./data/level/"


def load_level(folder):
    """
    Load a level from a folder containing the level structure and background map.
    
    Args:
        folder (str): Folder name containing the level files.

    Returns:
        Level: The loaded level, or None if an error occurred
    """
    structure = DEFAULT_LEVEL_PATH + folder + "/structure.json"  # Level structure file
    background_image = DEFAULT_LEVEL_PATH + folder + "/bg.png"  # Level background image file
    has_red = False  # If we added a red robot
    has_blue = False  # If we added a blue robot
    has_green = False  # If we added a green robot
    has_crates = False  # If we added crates
    has_big_crate = False  # If we added a big crate
    has_crate_del = False  # If we added a crate deletor
    chargepads = 0  # Number of charge pads
    ground_bots = 0  # Number of ground robots
    required_terminals = []
    existing_terminals = []  
    expected_heights = {  # Allowed heights for each entity type
        "tile": [ChargePad, Trap, CrateDel, CrateGen],
        "ground": [Blue, Red, Collectable, Crate, InputTer, OutputTer],
        "air": [Green, Collectable],
        "camera": [Camera],
    }

    if not os.path.exists(structure):  # Fail if the structure file is missing
        logging.error(f"Level structure file not found: {structure}")
        error_handler.push_error(
            "Loading Error",
            f"Level structure file not found: {structure}",
            ErrorLevel.ERROR
        )
        return None

    try:
        with open(structure, "r") as f:
            data = json.load(f)

            if not data:  # Fail if the structure file is empty
                logging.error("Level structure file is empty.")
                error_handler.push_error(
                    "Loading Error",
                    "Level structure file is empty.",
                    ErrorLevel.ERROR
                )
                return None

            # Fail if the values expected are not present
            if "size" not in data or "matrix" not in data or "entities" not in data:
                logging.error("Level structure file is missing required keys.")
                error_handler.push_error(
                    "Loading Error",
                    "Level structure file is missing required keys.\nCheck level creation manual.",
                    ErrorLevel.ERROR
                )
                return None
            size = data["size"]  # Dimensions of the level
            matrix = data["matrix"]  # Matrix of the level
            entities = data["entities"]  # Entities in the level

            # Step 1: Create the level
            level = Level(size[0], size[1], background_image)

            # Step 2: Load map data
            for y in range(size[1]):
                for x in range(size[0]):
                    if matrix[y][x] == 0:  # Path
                        level.tiles[y][x].set_path()
                    elif matrix[y][x] == 1:  # Mid-height wall
                        level.tiles[y][x].set_mid_wall()

            # Step 3: Define entity creation mapping
            entity_classes = {
                "Blue": lambda e: Blue(e["x"], e["y"], e.get("direction", "N")),
                "Red": lambda e: Red(e["x"], e["y"], e.get("direction", "N")),
                "Green": lambda e: Green(e["x"], e["y"], e.get("direction", "N")),
                "ChargePad": lambda e: ChargePad(e["x"], e["y"], 0),
                "Collectable": lambda e: Collectable(e["x"], e["y"], e.get("height", 0)),
                "Trap": lambda e: Trap(e["x"], e["y"], 0),
                "CrateDel": lambda e: CrateDel(e["x"], e["y"], 0),
                "CrateGen": lambda e: CrateGen(e["x"], e["y"], 0, e.get("crate_count", 0), e.get("crate_type", "big")),
                "Crate": lambda e: Crate(e["x"], e["y"], 0, small=e.get("small", False)),
                "InputTer": lambda e: InputTer(e["x"], e["y"], 0, e.get("ter_one"), e.get("ter_two"), e.get("operation")),
                "OutputTer": lambda e: OutputTer(e["x"], e["y"], e["color"], 0),
            }

            # Step 4: Load entities
            for height, entity_list in entities.items():
                for entity in entity_list:
                    entity_type = entity["type"]

                    # Determine the numerical height first
                    match height:
                        case "tile":
                            numerical_height = 0
                        case "ground":
                            numerical_height = 1
                        case "air":
                            numerical_height = 2
                        case _:
                            logging.error(f"Unknown entity height: {height}")
                            numerical_height = 0  # Default to 0 to prevent crashes

                    # Create the entity if the type is valid
                    valid_operations = ["+", "-", "*", "/"]
                    if entity_type in entity_classes:
                        # Don't create an input terminal if the operation is not valid
                        if entity_type == "InputTer" and entity.get("operation") not in valid_operations:
                            logging.error(f"Invalid operation for InputTer: {entity.get('operation')}")
                            error_handler.push_error(
                                "Loading Error",
                                f"Invalid operation for InputTer: {entity.get('operation')}\nThe only valid operations are: {valid_operations}",
                                ErrorLevel.ERROR
                            )
                            return None

                        obj = entity_classes[entity_type](entity)  # Create the entity using the mapping
                        obj.height = numerical_height  # Change the height to the numerical value

                        match entity_type:
                            case "Red":
                                if has_red:
                                    logging.error("Only one red robot is allowed in the level.")
                                    error_handler.push_error(
                                        "Loading Error",
                                        "Only one red robot is allowed in the level.",
                                        ErrorLevel.ERROR
                                    )
                                    return None
                                has_red = True
                                ground_bots += 1
                            case "Blue":
                                if has_blue:
                                    logging.error("Only one blue robot is allowed in the level.")
                                    error_handler.push_error(
                                        "Loading Error",
                                        "Only one blue robot is allowed in the level.",
                                        ErrorLevel.ERROR
                                    )
                                    return None
                                has_blue = True
                                ground_bots += 1
                            case "Green":
                                if has_green:
                                    logging.error("Only one green robot is allowed in the level.")
                                    error_handler.push_error(
                                        "Loading Error",
                                        "Only one green robot is allowed in the level.",
                                        ErrorLevel.ERROR
                                    )
                                    return None
                                has_green = True
                            case "ChargePad":
                                chargepads += 1
                                level.objectives["charge_pads"] += 1  # Modify objectives dictionary
                            case "Collectable":
                                level.objectives["collectables"] += 1
                            case "Crate":
                                if obj.small:
                                    level.objectives["crates_small"] += 1
                                else:
                                    level.objectives["crates_large"] += 1
                                    has_big_crate = True
                                has_crates = True
                            case "CrateGen":
                                if obj.crate_type == "small":
                                    level.objectives["crates_small"] += obj.crate_count
                                else:
                                    level.objectives["crates_large"] += obj.crate_count
                                    has_big_crate = True
                                has_crates = True
                            case "CrateDel":
                                has_crate_del = True
                            case "OutputTer":
                                if obj.color in required_terminals:
                                    logging.error(f"Duplicate output terminal color: {obj.color}")
                                    error_handler.push_error(
                                        "Loading Error",
                                        f"Duplicate output terminal color: {obj.color}",
                                        ErrorLevel.ERROR
                                    )
                                    return None
                                required_terminals.append(obj.color)
                            case "InputTer":
                                existing_terminals.append(obj.input_ter_one)
                                existing_terminals.append(obj.input_ter_two)
                                level.objectives["terminals"] += 1
                        
                        if not level.add_entity(obj):
                            logging.error(f"Failed to add entity {entity} to level.")
                            error_handler.push_error(
                                "Loading Error",
                                f"Failed to add entity {entity} to level.\nCheck the coordinates aren't already occupied.",
                                ErrorLevel.ERROR
                            )
                            return None
                    else:
                        logging.error(f"Unknown entity type: {entity_type}")


            # Step 5: Add the camera at the center of the level
            cam_x = size[0] // 2
            cam_y = size[1] // 2
            level.tiles[cam_y][cam_x].entities["camera"] = Camera(cam_x, cam_y, 3)

            # Step 6: Additional checks
            if not has_blue and not has_green and not has_red:  # Ensure at least one robot is present
                logging.error("No robots were added to the level.")
                error_handler.push_error(
                    "Loading Error",
                    "No robots were added to the level.\nAt least one robot is required.",
                    ErrorLevel.ERROR
                )
                return None

            if chargepads > ground_bots:  # Ensure less or equal charge pads than ground robots
                logging.error("Too many charge pads in the level.")
                error_handler.push_error(
                    "Loading Error",
                    "Level has more charge pads than ground robots.\nThis is not allowed.",
                    ErrorLevel.ERROR
                )
                return None

            for color in required_terminals:  # Ensure all required terminals are present
                if color not in existing_terminals:
                    logging.error(f"Missing output terminal for color: {color}")
                    error_handler.push_error(
                        "Loading Error",
                        f"A defined input terminal requires an output terminal of color {color}.\nThis terminal is missing.",
                        ErrorLevel.ERROR
                    )
                    return None

            if has_big_crate and not has_red:  # Ensure red robot is present if big crate is in the level
                logging.error("Big crate requires a red robot to be moved.")
                error_handler.push_error(
                    "Loading Error",
                    "Level has a big crate but no Red robot is present.\nRed is required to move big crates.",
                    ErrorLevel.ERROR
                )
                return None

            if not has_blue and required_terminals:  # Ensure blue robot is present if terminals are required
                logging.error("Blue robot is required to use terminals.")
                error_handler.push_error(
                    "Loading Error",
                    "Level has terminals but no Blue robot is present.\nBlue is required to operate terminals.",
                    ErrorLevel.ERROR
                )
                return None

            if not (has_green or has_red) and has_crates:  # Ensure green or red robot is present if crates are in the level
                logging.error("Crates require a green or red robot to be moved.")
                error_handler.push_error(
                    "Loading Error",
                    "Level has crates but no crate mover is present.\nCrate movers: Green, Red.",
                    ErrorLevel.ERROR
                )
                return None

            # Ensure a crate deletor exists if there are crates in the level
            if has_crates and not has_crate_del:
                logging.error("Crate deletor is required to remove crates.")
                error_handler.push_error(
                    "Loading Error",
                    "Level has crates but no CrateDel is present.\nCrateDel is required to remove crates.",
                    ErrorLevel.ERROR
                )
                return None

            for y in range(size[1]):  # Check all entities are on expected heights
                for x in range(size[0]):
                    tile = level.tiles[y][x]
                    for height, entity in tile.entities.items():
                        if entity is not None:
                            if type(entity) not in expected_heights[height]:
                                logging.error(f"Entity {entity} is on the wrong height.")
                                error_handler.push_error(
                                    "Loading Error",
                                    f"Entity {entity} is on the wrong height: {height}.",
                                    ErrorLevel.ERROR
                                )
                                return None
            return level

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        error_handler.push_error(
            "Loading Error",
            f"Error decoding level structure JSON: {e}\nAre you sure the structure is valid?",
            ErrorLevel.ERROR
        )
    except KeyError as e:
        logging.error(f"Missing key in level JSON: {e}")
        error_handler.push_error(
            "Loading Error",
            f"Missing key in level structure JSON: {e}\nAre you sure the structure has all required fields?",
            ErrorLevel.ERROR
        )
    '''
    except Exception as e:
        logging.error(f"Unknown error loading level: {e}")
        error_handler.push_error(
            "Loading Error",
            f"Unknown error loading level: {e}\nPerhaps you forgot one of the entity keys? (tile, ground, air)\nAll must be present, even if empty.",
            ErrorLevel.ERROR
        )
    '''

    return None
