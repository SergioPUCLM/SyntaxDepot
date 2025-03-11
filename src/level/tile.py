"""Tile class module"""

import logging
import pygame
from src.render.missing_image import missing_texture_pygame


class Tile:
    """
    Tile class, representing a single tile in the level. It can contain up to 3 entities on different heights.
    Unless otherwise specified, all tiles are "walls" and have colision with anything (except the camera).
    However, the wall can also be classified as a "mid-height wall", which allows air entities to pass through it.
    """
    def __init__(self, x, y, image):
        self.entities = {
            'tile': None,  # Entity on the tile (Not the same as ground, this defines what the floor is made of)
            'ground': None,  # Entity on the ground
            'air': None,  # Entity in the air
            'camera': None  # Entity on the camera
        }

        self.x = x  # X Position of the tile in the level
        self.y = y  # Y Position of the tile in the level

        # Tiles start as walls by default
        self.is_path = False  # Whether this tile is a path or not
        self.is_mid_wall = False  # Whether this tile is a mid-height wall or not

        if isinstance(image, pygame.Surface):
            self.image = image
        else:
            try:
                self.image = pygame.image.load(image)
            except pygame.error as e:
                logging.error(f"Error loading tile image: {e}")
                self.image = missing_texture_pygame()  # Use missing texture


    
    def __str__(self):
        """
        String representation of the tile.

        Returns:
            str: String representation of the tile.
        """
        icon = "W"  # Wall icon
        if self.is_path:
            # Define the order of priority
            priority_keys = ['camera', 'air', 'ground', 'tile']
            
            # Get the first entity that is not None
            for key in priority_keys:
                if self.entities[key] is not None:
                    icon = str(self.entities[key])
                    break
            else:
                icon = '.'  # Empty tile
        elif self.is_mid_wall:
            icon = "w"
        return icon


    def set_path(self, force=False):
        """
        Marks this tile as a path, allowing entities to move through it.

        A tile set as a path loses its "wall" properties. This fails if the tile 
        is a mid-height wall unless overridden.

        Args:
            force (bool, optional): If True, overrides the mid-height wall and sets 
                the tile as a path. Default is False.

        Returns:
            bool: True if the tile was successfully set as a path, False otherwise.
        """

        success = False
        if not force and not self.is_mid_wall:
            self.is_path = True
            success = True
        elif force:  # If force is True, override the mid-height wall
            self.is_mid_wall = False
            self.is_path = True
            success = True
            logging.warning("Tile set as path, overriding mid-height wall")
        else:
            logging.warning("Cannot set a mid-height wall as a path. Use force=True to override")
        return success

    
    def set_mid_wall(self, force=False):
        """
        Marks this tile as a mid-height wall, allowing air entities to pass through it.

        A mid-height wall loses its "path" properties but keeps some wall properties. This fails if the tile is a path
        unless overridden.

        Args:
            force (bool, optional): If True, overrides the path and sets the tile as a mid-height wall. Default is False.

        Returns:
            bool: True if the tile was successfully set as a mid-height wall, False otherwise.
        """

        success = False
        if not force and not self.is_path:
            self.is_mid_wall = True
            success = True
        elif force:  # If force is True, override the path
            self.is_path = False
            self.is_mid_wall = True
            success = True
            logging.warning("Tile set as mid-height wall, overriding path")
        else:
            logging.warning("Cannot set a path as a mid-height wall")
        return success


    def set_wall(self):
        """
        Marks this tile as a wall, preventing entities from moving through it.

        A wall loses its "path" and "mid-height wall" properties.

        Returns:
            bool: True if the tile was successfully set as a wall, False otherwise.
        """
        self.is_path = False
        self.is_mid_wall = False
        return True

    
    def add_entity(self, entity, height, force=False):
       """
       Adds an entity to the tile at the specified height.

       Fails if an entity already exists at that height unless `force` is True.

       Args:
           entity (Entity): The entity to add to the tile.
           height (str): The height layer to place the entity in ('ground', 'air', 'camera').
           force (bool, optional): If True, replaces an existing entity at that height. Default is False.

       Returns:
           bool: True if the entity was successfully added, False otherwise.
       """

       success = False
       if self.entities[height] is None:
           self.entities[height] = entity
           success = True
       elif force:  # If force is True, override the entity
           self.entities[height] = entity
           success = True
           logging.warning("Entity added to tile, overriding existing entity")
       else:
           logging.warning("Cannot add entity to tile: Entity already exists at given height")
       return success


    def remove_entity(self, height):
        """
        Removes the entity from the tile at the specified height.

        Fails if no entity exists at that height.

        Args:
            height (str): The height layer to remove the entity from ('ground', 'air', 'camera').

        Returns:
            bool: True if the entity was successfully removed, False otherwise.
        """
        success = False
        if self.entities[height] is not None:
            self.entities[height] = None  # Height can be: 'ground', 'air', 'camera'
            success = True
        else:
            logging.warning("Cannot remove entity from tile: No entity at given height")
        return success