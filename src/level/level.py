"""Level class"""

import os
import logging
import pygame
from src.level.tile import Tile
from src.render.missing_image import missing_texture_pygame
from src.render.error_handler import error_handler, ErrorLevel
from src.render.sound_manager import sound_manager


class Level:
    """
    Level class, defining the structure of a level in-game, including how the objectives and physical representation are handled.
    It contains a 2D array of tiles, each representing a cell in the level, a list of objectives, and the size of the level.

    Attributes:
        tile_size (int): Size of each tile in pixels.
        width (int): Width of the level in tiles.
        height (int): Height of the level in tiles.
        bg (pygame.Surface): Background image of the level.
        img_mtx (list): List of lists containing the image matrix.
        tiles (list): 2D array of Tile objects representing the level.
        objectives (dict): Dictionary containing the objectives of the level.

    Methods:
        __init__(self, width, height, background_image): Initializes the level with the given width, height, and background image.
        __str__(self): Returns a string representation of the level.
        split_image(self): Splits the background image into 64x64 sections.
        add_entity(self, entity): Adds an entity to the level.
        get_camera_position(self): Gets the position of the camera in the level.
        remove_entity(self, entity): Removes an entity from the level.
        teleport_entity(self, entity, x, y): Teleports an entity to a new position in the level.
        move_entity(self, entity, direction): Moves an entity in a direction.
        move(self, entity): Moves one entity on the direction it is facing currently.
        turn(self, entity, direction): Turns an entity in a direction.
        _get_target_coords(self, entity): Gets the target coordinates of an entity based on its direction.
        see(self, entity): Sees an entity in front of the current entity.
        pickup(self, entity): Picks up an entity that can be picked up.
        drop(self, entity): Drops an entity that can be dropped.
        read(self, entity): Reads an entity that can be read.
        write(self, entity, data): Writes data to an entity that can be written to.
        wait(self, entity): Waits for one turn.
    """
    def __init__(self, width, height, background_image, remove_callback=None):
        self.tile_size = 64
        self.width = width
        self.height = height
        self.remove_callback = remove_callback  # Callback function to remove entities from the level
        self.success = True  # Success flag for the level

        if os.path.exists(background_image):
            try:
                self.bg = pygame.image.load(background_image)
            except pygame.error as e:
                logging.error(f"Error loading background image: {e}")
                self.bg = missing_texture_pygame(width * self.tile_size, height * self.tile_size)
        else:
            logging.warning(f"Background image '{background_image}' not found. Using fallback texture.")
            self.bg = missing_texture_pygame(width * self.tile_size, height * self.tile_size)
            
        self.img_mtx = self.split_image()
        self.tiles = [[Tile(x, y, self.img_mtx[y][x]) for x in range(width)] for y in range(height)]  # 2D array of tiles

        self.objectives = {
            "charge_pads": 0,  # Number of charge pads in the level
            "crates_small": 0,  # Number of small crates in the level (include crate generators)
            "crates_large": 0,  # Number of large crates in the level (include crate generators)
            "terminals": 0,  # Number of terminals in the level
            "collectables": 0,  # Number of collectibles in the level
        }


    def __str__(self):
        """
        String representation of the level.

        Returns:
            str: String representation of the level.
        """
        level_str = ""
        for row in self.tiles:
            for tile in row:
                level_str += str(tile)
            level_str += "\n"
        return level_str


    def split_image(self):
        """
        Split an image into 64x64 sections. If the bg is not divisible by 64, it will be extended.

        Returns:
            list: List of lists containing the image matrix.
        """
        img = self.bg
        img_matrix = []

        img = pygame.transform.scale(img, (self.width * self.tile_size, self.height * self.tile_size))

        for y in range(0, self.height * self.tile_size, self.tile_size):  # Create subimages to assign to tiles
            img_matrix.append([])
            for x in range(0, self.width * self.tile_size, self.tile_size):
                img_matrix[y // self.tile_size].append(img.subsurface(x, y, self.tile_size, self.tile_size))
        return img_matrix


    def add_entity(self, entity):
        """
        Adds an entity to the level, placing it in the corresponding tile.

        Args:
            entity (Entity): Entity to be added to the level.

        Returns:
            bool: True if the entity was successfully added, False otherwise
        """
        success = True
        x = entity.x
        y = entity.y
        height = entity.height

        if x < 0 or x >= self.width or y < 0 or y >= self.height:  # Check if the entity is out of bounds
            logging.error(f"Entity {entity} is out of bounds.")
            success = False
        else:
            tile = self.tiles[y][x]
            match height:
                case 0:  # Tile entities
                    if tile.entities['tile'] is not None:  # Check if the tile is empty
                        logging.error(f"Tile {tile} is already occupied by {tile.entities['tile']}.")
                        success = False
                    elif tile.is_path:  # Tiles can only be placed on paths
                        tile.entities['tile'] = entity
                    else:
                        logging.error(f"Entity {entity} cannot be placed on a wall.")
                        success = False
                case 1:  # Ground entities
                    if tile.entities['ground'] is not None:
                        logging.error(f"Tile {tile} is already occupied by {tile.entities['ground']}.")
                        success = False
                    elif tile.is_path:  # Ground entities can only be placed on paths
                        tile.entities['ground'] = entity
                    else:
                        logging.error(f"Entity {entity} cannot be placed on a wall.")
                        success = False
                case 2:  # Air entities
                    if tile.entities['air'] is not None:
                        logging.error(f"Tile {tile} is already occupied by {tile.entities['air']}.")
                        success = False
                    elif tile.is_path or tile.is_mid_wall:  # Air entities can be placed on paths or mid-height walls
                        tile.entities['air'] = entity
                    else:
                        logging.error(f"Entity {entity} cannot be placed on a wall.")
                        success = False
                case 3:  # Camera entity
                    if tile.entities['camera'] is not None:
                        logging.error(f"Tile {tile} is already occupied by {tile.entities['camera']}.")
                        success = False
                    else:
                        tile.entities['camera'] = entity
                case _:
                    logging.error(f"Invalid entity height: {height}")
                    success = False
        return success


    def get_camera_position(self):
        """
        Get the position of the camera in the level.

        Returns:
            tuple: Position of the camera.
        """
        for row in self.tiles:
            for tile in row:
                if tile.entities['camera']:
                    return (tile.x, tile.y)


    def remove_entity(self, entity):
        """
        Removes an entity from the level.

        Args:
            entity (Entity): Entity to remove.
        
        Returns:
            bool: True if the entity was successfully removed, False otherwise.
        """
        success = True
        x = entity.x
        y = entity.y
        height = entity.height

        if x < 0 or x >= self.width or y < 0 or y >= self.height:  # Check if the entity is out of bounds
            logging.error(f"Entity {entity} is out of bounds.")
            success = False
        else:
            tile = self.tiles[y][x]
            match height:
                case 0:
                    tile.entities['tile'] = None
                case 1:
                    tile.entities['ground'] = None
                case 2:
                    tile.entities['air'] = None
                case 3:
                    tile.entities['camera'] = None
                case _:
                    logging.error(f"Invalid entity height: {height}")
                    success = False
            # If the entity is not a robot
            if entity.__class__.__name__.lower() not in ["red", "green", "blue"]:
                self.remove_callback(entity)  # Do not remove bots
        return success


    def teleport_entity(self, entity, x, y):
        """
        Teleport an entity to a new position in the level.

        Args:
            entity (Entity): Entity to teleport.
            x (int): New x position.
            y (int): New y position.

        Returns:
            bool: True if the entity was successfully teleported, False otherwise
        """
        success = True
        old_x = entity.x
        old_y = entity.y

        # Check if the entity or destination is out of bounds
        if (old_x < 0 or old_x >= self.width or old_y < 0 or old_y >= self.height) or (x < 0 or x >= self.width or y < 0 or y >= self.height):  
            logging.error(f"Entity {entity} is out of bounds.")
            return False

        target_tile = self.tiles[y][x]
        entity_height = entity.height  # Returns a number
        string_height = None
        match entity_height:
            case 0:
                string_height = 'tile'
            case 1:
                string_height = 'ground'
            case 2:
                string_height = 'air'
            case 3:
                string_height = 'camera'
            case _:
                logging.error(f"Invalid entity height: {entity_height}")
                return False

        # Check if the tile is occupied at this height level
        if target_tile.entities[string_height] is not None:
            logging.error(f"Cannot teleport entity {entity} to ({x}, {y}). Tile is already occupied.")
            return False

        if string_height == 'camera':
            # Camera can move anywhere as long as the spot isn't occupied by another camera
            pass
        elif string_height == 'air':
            # Air can move to paths or mid-walls, but not regular walls
            if not target_tile.is_path and not target_tile.is_mid_wall:
                logging.error(f"Cannot teleport air entity {entity} to ({x}, {y}). Tile is a solid wall.")
                return False
        else:
            # Must be on a path and not a mid-wall
            if not target_tile.is_path:
                logging.error(f"Cannot teleport entity {entity} to ({x}, {y}). Tile is a wall.")
                return False
            if target_tile.is_mid_wall:
                logging.error(f"Cannot teleport entity {entity} to ({x}, {y}). Tile is a mid-height wall.")
                return False

        self.remove_entity(entity)
        entity.x = x
        entity.y = y
        self.add_entity(entity)
        return True


    def move_entity(self, entity, direction):
        """
        Move an entity in a direction.

        Args:
            entity (Entity): Entity to move.
            direction (str): Direction to move in. (up, down, left, right)
        """
        success = True
        x = entity.x
        y = entity.y

        # Check if the entity is out of bounds
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            logging.error(f"Entity {entity} is out of bounds.")
            success = False
        else:
            match direction:
                case "up":
                    dx, dy = 0, -1
                case "down":
                    dx, dy = 0, 1
                case "left":
                    dx, dy = -1, 0
                case "right":
                    dx, dy = 1, 0
                case "N":  # Same as up
                    dx, dy = 0, -1
                case "S":  # Same as down
                    dx, dy = 0, 1
                case "E":  # Same as right
                    dx, dy = 1, 0
                case "W":  # Same as left
                    dx, dy = -1, 0
                case _:
                    logging.error(f"Invalid movement direction: {direction}")
                    success = False
            new_x = x + dx
            new_y = y + dy

            if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                success = False
            else:
                if not self.teleport_entity(entity, new_x, new_y):
                    string_height = None
                    match entity.height:
                        case 0:
                            string_height = 'tile'
                        case 1:
                            string_height = 'ground'
                        case 2:
                            string_height = 'air'
                        case 3:
                            string_height = 'camera'
                        case _:
                            logging.error(f"Invalid entity height: {entity.height}")
                            success = False
                    # If the fail reason is a collectable
                    if self.tiles[new_y][new_x].entities[string_height].__class__.__name__.lower() == "collectable":
                        # Remove the collectable from the tile and redo the teleport
                        collectable = self.tiles[new_y][new_x].entities[string_height]
                        self.remove_entity(collectable)
                        sound_manager.play("collectable")
                        self.teleport_entity(entity, new_x, new_y)
                    else:
                        logging.error(f"Entity {entity} cannot move to ({new_x}, {new_y}). Tile is already occupied.")
                        success = Falseç
            # After movement is confirmed successful
            if success and entity.__class__.__name__.lower() in ["red", "blue"]:
                # Check if target position has a chargepad
                target_tile = self.tiles[entity.y][entity.x]
                if (target_tile.entities['tile'] and 
                    target_tile.entities['tile'].__class__.__name__.lower() == "chargepad"):
                    sound_manager.play("charge")
        return success
    

    # ======== LANGUAGE ACTIONS ========

    def move(self, entity):  # move() in language (Wrapper function for move_entity())
        """
        Moves one entity on the direction it is facing currently 1 step

        Args:
            entity (Entity): Entity to move.

        Returns:
            bool: True if the entity was successfully moved, False otherwise
        """
        success = self.move_entity(entity, entity.direction)
        if not success:
            error_handler.push_error(
                "Execution Problem",
                f"Entity {entity} cannot advance.\nThe tile is occupied, out of bounds or it cannot cross it.",
                ErrorLevel.WARNING
            )
            self.success = False  # Mark level as failed
            logging.error(f"Entity {entity} cannot move.")
        else:
            match entity.__class__.__name__.lower():
                case "red":
                    sound_manager.play("red_move")
                case "green":
                    sound_manager.play("green_move")
                case "blue":
                    sound_manager.play("blue_move")
        return success

    
    def turn(self, entity, direction):  # turn_left() or turn_right() action in language
        """
        Turn an entity in a direction.

        Args:
            entity (Entity): Entity to turn.
            direction (str): Direction to turn in. (left, right)

        Returns:
            bool: True if the entity was successfully turned, False otherwise
        """
        success = True
        if direction == "left":
            match entity.direction:
                case "N":
                    entity.direction = "W"
                case "W":
                    entity.direction = "S"
                case "S":
                    entity.direction = "E"
                case "E":
                    entity.direction = "N"
        elif direction == "right":
            match entity.direction:
                case "N":
                    entity.direction = "E"
                case "E":
                    entity.direction = "S"
                case "S":
                    entity.direction = "W"
                case "W":
                    entity.direction = "N"
        else:
            logging.error(f"Invalid turn direction: {direction}")
            success = False
        if success:
            match entity.__class__.__name__.lower():
                case "red":
                    sound_manager.play("red_move")
                case "green":
                    sound_manager.play("green_move")
                case "blue":
                    sound_manager.play("blue_move")
        return success


    def _get_target_coords(self, entity):  # Helper function
        """
        Get the target coordinates of an entity based on its direction.

        Args:
            entity (Entity): Entity to get target coordinates for.

        Returns:
            tuple: Target coordinates (x, y).
        """
        x = entity.x
        y = entity.y

        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            logging.error(f"Entity {entity} is out of bounds.")
            new_x, new_y = None, None
        else:
            if entity.__class__.__name__.lower() == "red" or entity.__class__.__name__.lower() == "blue":  # Red and blue target up in front
                match entity.direction:
                    case "N":
                        new_x, new_y = x, y - 1
                    case "S":
                        new_x, new_y = x, y + 1
                    case "E":
                        new_x, new_y = x + 1, y
                    case "W":
                        new_x, new_y = x - 1, y
                    case _:
                        logging.error(f"Invalid direction: {entity.direction}")
                        new_x, new_y = None, None
            elif entity.__class__.__name__.lower() == "green":  # Green targets down below
                new_x, new_y = x, y
            else:
                logging.error(f"Entity {entity.__class__.__name__} cannot have a target")
                new_x, new_y = None, None

            if not new_x is None or not new_y is None:
                if (new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height):
                    logging.error(f"Target coordinates ({new_x}, {new_y}) are out of bounds.")
                    new_x, new_y = None, None
        return new_x, new_y


    def see(self, entity):  # see() in language
        """
        See an entity in front of the current entity.

        Args:
            entity (Entity): Entity to see.

        Returns:
            str: String representation of what is in front of the current entity.
        """
        vision = None
        new_x, new_y = self._get_target_coords(entity)
        if new_x is None or new_y is None:  # Check the target was set
            error_handler.push_error(
                "Execution Problem",
                f"Entity {entity} cannot see an invalid tile (out of bounds).",
                ErrorLevel.WARNING
            )
            self.success = False  # Mark level as failed
            logging.error(f"Entity {entity} cannot see.")
        else:
            target_tile = self.tiles[new_y][new_x]
            ground_entity = target_tile.entities.get('ground')
            skip_ground = False
            if ground_entity:
                match ground_entity.__class__.__name__.lower():
                    case "crate":
                        vision = "crate_small" if ground_entity.small else "crate"
                    case "crategen":
                        vision = "crategen_small" if ground_entity.type == "small" else "crategen"
                    case "collectable":
                        skip_ground = True  # Ignore collecables to make them invisible
                    case "trap":
                        # If active, return trap, if not return wall, empty or mid_height wall, depending on the tile
                        if ground_entity.active:
                            vision = "trap"
                        else:
                            if target_tile.is_mid_wall:
                                vision = "mid_wall"
                            elif not target_tile.is_path:
                                vision = "wall"
                    case _:
                        vision = ground_entity.__class__.__name__.lower()

            if (not ground_entity or skip_ground) and target_tile.entities.get('tile'):
                tile_entity = target_tile.entities['tile']
                vision = tile_entity.__class__.__name__.lower()

            if vision is None:
                if target_tile.is_mid_wall:
                    vision = "mid_wall"
                elif not target_tile.is_path:
                    vision = "wall"
                else:
                    vision = "empty"

        return vision


    def pickup(self, entity):  # pickup() in language
        """
        Pickup an entity that can be picked up

        Args:
            entity (Entity): Entity to pickup.

        Returns:
            bool: True if the entity was successfully picked up, False otherwise
        """
        success = True
        if entity.__class__.__name__.lower() in ["red", "green"]:  # Only red and green can pick up
            new_x, new_y = self._get_target_coords(entity)
            if new_x is None or new_y is None:  # Check the target was set
                logging.error(f"Entity {entity} cannot be picked up.")
                success = False
            else:
                target_entity = self.tiles[new_y][new_x].entities['ground']
                target_entity_class = target_entity.__class__.__name__.lower()
                if target_entity is not None and target_entity_class == "crate" and target_entity.pickable:  # Check if there is an entity to pick up there
                    # Make sure only green and red can pickup
                    match entity.__class__.__name__.lower():
                        case "red":  # Pick up any crate
                            entity.crate = target_entity
                            self.remove_entity(target_entity)  # Remove the reference to the crate from the tile
                            entity.crate.x = None  # Temporarelly disable it's coordinates
                            entity.crate.y = None
                            logging.info(f"Entity {entity} picked up crate {target_entity}.")
                            if target_entity.small:
                                sound_manager.play("pickup_small")
                            else:
                                sound_manager.play("pickup_big")
                        case "green":
                            if target_entity.small:
                                entity.crate = target_entity
                                self.remove_entity(target_entity)
                                entity.crate.x = None
                                entity.crate.y = None
                                logging.info(f"Entity {entity} picked up crate {target_entity}.")
                                sound_manager.play("pickup_small")
                            else:
                                error_handler.push_error(
                                    "Execution Problem",
                                    f"Entity {entity} can only carry small crates.\nBig crates must be carried by Red",
                                    ErrorLevel.WARNING
                                )
                                self.success = False  # Mark level as failed
                                logging.error(f"Entity {entity} cannot pick up crate {target_entity} (Too big).")
                                success = False
                else:
                    error_handler.push_error(
                        "Execution Problem",
                        f"Entity {entity} can only pick up crates.",
                        ErrorLevel.WARNING
                    )
                    self.success = False  # Mark level as failed
                    logging.error(f"No entity to pick up at ({new_x}, {new_y}).")
                    success = False
        else:
            logging.error(f"Entity {entity} cannot pick up.")
            error_handler.push_error(
                "Execution Problem",
                f"Robot {entity} cannot execute pickup() actions.\nOnly Red and Green can.",
                ErrorLevel.WARNING
            )
            self.success = False  # Mark level as failed
            success = False
        return success
                
                        
    def drop(self, entity):  # drop() in language
        """
        Drop an entity that can be dropped

        Args:
            entity (Entity): Entity that will drop.

        Returns:
            bool: True if the entity was successfully dropped, False otherwise
        """
        success = True
        if entity.__class__.__name__.lower() in ["red", "green"]:  # Only red and green can drop
            new_x, new_y = self._get_target_coords(entity)
            if new_x is None or new_y is None:
                error_handler.push_error(
                    "Execution Problem",
                    f"Entity {entity} cannot drop it's crate on an invalid tile (out of bounds).",
                    ErrorLevel.WARNING
                )
                self.success = False  # Mark level as failed
                logging.error(f"Entity {entity} cannot drop.")
                success = False
            else:
                target_entity = self.tiles[new_y][new_x].entities['ground']
                if target_entity is None and self.tiles[new_y][new_x].is_path:  # Check if the tile is empty and is not a wall
                    if entity.crate is not None:
                        entity.crate.x = new_x
                        entity.crate.y = new_y
                        self.add_entity(entity.crate)
                        if entity.crate.small:
                            sound_manager.play("drop_small")
                        else:
                            sound_manager.play("drop_big")
                        entity.crate = None
                        logging.info(f"Entity {entity} dropped crate at ({new_x}, {new_y}).")
                    else:
                        error_handler.push_error(
                            "Execution Problem",
                            f"Entity {entity} is not holding a crate.",
                            ErrorLevel.WARNING
                        )
                        self.success = False  # Mark level as failed
                        logging.error(f"Entity {entity} has nothing to drop.")
                        success = False
                else:
                    error_handler.push_error(
                        "Execution Problem",
                        f"Entity {entity} cannot drop it's crate on an occupied tile.",
                        ErrorLevel.WARNING
                    )
                    self.success = False  # Mark level as failed
                    logging.error(f"Cannot drop entity at ({new_x}, {new_y}). Tile is already occupied.")
                    success = False
        else:
            error_handler.push_error(
                "Execution Problem",
                f"Robot {entity} cannot hold crates.\nOnly Red and Green can.",
                ErrorLevel.WARNING
            )
            self.success = False  # Mark level as failed
            logging.error(f"Entity {entity} cannot drop.")
            success = False
        return success    


    def read(self, entity):  # read() in language
        """
        Read an entity that can be read

        Args:
            entity (Entity): Entity that will read.

        Returns:
            str: Data read from the entity (None if the read action could not be completed)
        """
        if entity.__class__.__name__.lower() == "blue":  # Only blue can read
            data = None
            new_x, new_y = self._get_target_coords(entity)
            if new_x is None or new_y is None:
                error_handler.push_error(
                    "Execution Problem",
                    f"Robot {entity} can only read from output terminals",
                    ErrorLevel.WARNING
                )
                self.success = False  # Mark level as failed
                logging.error(f"Entity {entity} cannot read.")
            else:
                target_entity = self.tiles[new_y][new_x].entities['ground']
                target_entity_class = target_entity.__class__.__name__.lower()
                if target_entity is not None and target_entity_class == "outputter":
                    data = target_entity.number
                else:
                    error_handler.push_error(
                        "Execution Problem",
                        f"There is nothing to read in front of {entity}.\nGot: {target_entity_class}\nExpected: outputter",
                        ErrorLevel.WARNING
                    )
                    self.success = False  # Mark level as failed
                    logging.error(f"No entity to read at ({new_x}, {new_y}).")
        else:
            error_handler.push_error(
                "Execution Problem",
                f"Robot {entity} cannot execute read() actions.",
                ErrorLevel.WARNING
            )
            self.success = False  # Mark level as failed
            logging.error(f"Entity {entity} cannot read.")
        return data


    def write(self, entity, data):  # write() in language
        """
        Write data to an entity that can be written to

        Args:
            entity (Entity): Entity that will write.
            data (str): Data to write.

        Returns:
            bool: True if the entity was successfully written to, False otherwise
        """
        success = True
        if entity.__class__.__name__.lower() == "blue":  # Only blue can write
            new_x, new_y = self._get_target_coords(entity)
            if new_x is None or new_y is None:
                error_handler.push_error(
                    "Execution Problem",
                    f"Robot {entity} can only write to input terminals",
                    ErrorLevel.WARNING
                )
                self.success = False  # Mark level as failed
                logging.error(f"No entity to write to at ({new_x}, {new_y}).")
                success = False
            else:
                target_entity = self.tiles[new_y][new_x].entities['ground']
                target_entity_class = target_entity.__class__.__name__.lower()
                if target_entity is not None and target_entity_class == "inputter":
                    if entity.__class__.__name__.lower() == "blue":
                        # Write (Check if the numbers required on the terminals num op num is the same as data)
                        # Locate the terminals in the level that have the colors
                        num_one = None
                        num_two = None
                        for tile in self.tiles:
                            for t in tile:
                                if t.entities['ground'] is not None and t.entities['ground'].__class__.__name__.lower() == "outputter":
                                    if target_entity.input_ter_one == t.entities['ground'].color:
                                        num_one = t.entities['ground'].number
                                    elif target_entity.input_ter_two == t.entities['ground'].color:
                                        num_two = t.entities['ground'].number
                        result = None
                        match target_entity.operation:
                            case "+":
                                result = num_one + num_two
                            case "-":
                                result = num_one - num_two
                            case "*":
                                result = num_one * num_two
                            case "/":
                                if num_two != 0:
                                    result = num_one / num_two
                                else:
                                    logging.error("Division by zero error.")
                                    success = False
                        if result == data:
                            target_entity.activated = True
                            logging.info(f"Entity {entity} wrote {data} to {target_entity}.")
                            sound_manager.play("correct")
                        else:
                            error_handler.push_error(
                                "Execution Problem",
                                f"Robot {entity} wrote the wrong data to a terminal.\nGot: {data}\nExpected: {result}",
                                ErrorLevel.WARNING
                            )
                            self.success = False  # Mark level as failed
                            logging.error(f"Entity {entity} failed to write {data} to {target_entity}.")
                            sound_manager.play("incorrect")
                            success = False
                else:
                    error_handler.push_error(
                        "Execution Problem",
                        f"Robot {entity} needs an Input terminal in front to write.",
                        ErrorLevel.WARNING
                    )
                    self.success = False  # Mark level as failed
                    logging.error(f"Entity {entity} cannot write to {target_entity}.")
                    success = False
        else:
            error_handler.push_error(
                "Execution Problem",
                f"Robot {entity} cannot execute write() actions.",
                ErrorLevel.WARNING
            )
            self.success = False  # Mark level as failed
            logging.error(f"Entity {entity} cannot write.")
            success = False
        return success
                
    
    def wait(self, entity):  # wait() in language
        """
        Wait for one turn.

        Args:
            entity (Entity): Entity to wait.

        Returns:
            bool: True if the entity successfully waited.
        """
        success = True
        if entity is not None and (entity.__class__.__name__.lower() == "green" or entity.__class__.__name__.lower() == "blue" or entity.__class__.__name__.lower() == "red"):
            logging.info(f"Entity {entity} is waiting.")
        else:
            logging.error(f"Entity {entity} cannot wait.")
            error_handler.push_error(
                "Execution Error",
                f"Robot {entity} cannot wait.",
                ErrorLevel.WARNING
            )
            self.success = False  # Mark level as failed
            success = False
        return success
