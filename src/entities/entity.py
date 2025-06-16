"""
Entity class.

This module defines the Entity class, which serves as a base class for all entities in the game.
It provides the basic structure and properties that all entities will inherit from, such as position, height, direction, 
and if they can be picked up.

Classes:
    Entity (ABC): Base abstract class for all entities in the game, defining their basic properties and structure.
"""

import logging
from abc import ABC


class Entity(ABC):
    """
    Entity class, defining the basic structure of an entity in-game. This is a super class for all entities in the game.
    It includes properties such as position (x, y), height, direction, and pickability.

    Attributes:
        x (int): The x-coordinate of the entity.
        y (int): The y-coordinate of the entity.
        height (int): The height at which the entity will move (0 = tile, 1 = ground, 2 = air, 3 = camera).
        direction (str): The direction the entity is facing ('N', 'S', 'E', 'W').
        pickable (bool): Whether the entity can be picked up or not.

    Methods:
        __init__(x, y, height, direction='N', pickable=False): Initializes an Entity with specified coordinates, height, direction, and pickability.
        __str__(): String representation of the entity.

    Example:
        entity = Entity(10, 20, 1, direction='N', pickable=True)
    
    Note: Do not instantiate this class directly. Instead, create subclasses that implement specific entity behavior.
    """
    def __init__(self, x, y, height, direction='N', pickable=False):
        """
        Initializes an Entity with specified coordinates, height, direction, and pickability.
        Args:
            x (int): The x-coordinate of the entity.
            y (int): The y-coordinate of the entity.
            height (int): The height at which the entity will move (0 = tile, 1 = ground, 2 = air, 3 = camera).
            direction (str): The direction the entity is facing ('N', 'S', 'E', 'W').
            pickable (bool): Whether the entity can be picked up or not.
        """
        self.x = x  # X Position of the entity
        self.y = y  # Y Position of the entity
        self.height = height  # Height at which the entity will move, 0 = tile, 1 = ground, 2 = air, 3 = camera
        self.direction = direction  # Direction the entity is facing, can be 'N', 'S', 'E', 'W'
        self.pickable = False  # Whether the entity can be picked up or not

    
    def __str__(self):
        """
        String representation of the entity.

        Returns:
            str: String representation of the entity.
        """
        return f"?"  # ? Because there should not be standalone entities