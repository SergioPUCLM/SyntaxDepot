"""Level class"""

import os
import logging
import pygame
from src.level.tile import Tile
from src.render.missing_image import missing_texture_pygame

class Level:
    """
    Level class, defining the structure of a level in-game, including how the objectives and physical representation are handled.
    It contains a 2D array of tiles, each representing a cell in the level, a list of objectives, and the size of the level.
    """
    def __init__(self, width, height, background_image):
        self.tile_size = 32
        self.width = width
        self.height = height

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
                #img_matrix[y // 64].append(img.subsurface(x, y, tile_size, tile_size))
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
            match height:  # Replace entity if it already exists
                case 0:  # Tile entities
                    if tile.is_path:  # Tiles can only be placed on paths
                        tile.entities['tile'] = entity
                    else:
                        logging.error(f"Entity {entity} cannot be placed on a wall.")
                        success = False
                case 1:  # Ground entities
                    if tile.is_path:  # Ground entities can only be placed on paths
                        tile.entities['ground'] = entity
                    else:
                        logging.error(f"Entity {entity} cannot be placed on a wall.")
                        success = False
                case 2:  # Air entities
                    if tile.is_path or tile.is_mid_wall:  # Air entities can be placed on paths or mid-height walls
                        tile.entities['air'] = entity
                    else:
                        logging.error(f"Entity {entity} cannot be placed on a wall.")
                        success = False
                case 3:  # Camera entity
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
            entity (Entity): Entity to remove.ç
        
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
            success = False
        else:
            self.remove_entity(entity)
            entity.x = x
            entity.y = y
            self.add_entity(entity)
        return success


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
                case _:
                    logging.error(f"Invalid movement direction: {direction}")
                    success = False
            new_x = x + dx
            new_y = y + dy

            if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                logging.error(f"Entity {entity} cannot move {direction}. Out of bounds.")
                success = False
            else:
                self.teleport_entity(entity, new_x, new_y)
                logging.info(f"Entity {entity} moved {direction} from ({x}, {y}) to ({new_x}, {new_y}).")
        return success

        