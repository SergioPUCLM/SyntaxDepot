"""Entity class"""

import logging
from abc import ABC


class Entity(ABC):
    """
    Entity class, defining the basic structure of an entity in-game. This is a super class for all entities in the game.
    """
    def __init__(self, x, y, height, direction='N', pickable=False):
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