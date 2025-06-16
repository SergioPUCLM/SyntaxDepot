"""
Crate delivery class module.

This module defines the CrateDel class, which represents crate delivery points in the game.
It inherits from the Entity class and serves as objectives for ground robots to reach.

Classes:
    CrateDel (Entity): Represents a crate delivery point in the game, which cannot be picked up and serves as an objective.
"""

from src.entities.entity import Entity


class CrateDel(Entity):
    """
    CrateDel class, defining the crate delivery points in the game. Inherits from Entity.
    Crate delivery points sit on the tile level and cannot be picked up.
    Crate delivery points serve as objectives in the game, requiring a ground robot to be on top of them at the end of the script.

    Attributes:
        x (int): The x-coordinate of the crate delivery point.
        y (int): The y-coordinate of the crate delivery point.
        height (int): The height of the crate delivery point.
        pickable (bool): Whether the crate delivery point can be picked up (always False).
        active (bool): Whether it will delete a crate or not in the next tick.

    Methods:
        __init__(x, y, height): Initializes a CrateDel instance with specified coordinates and height.
        __str__(): String representation of the crate delivery point.

    Example:
        crate_delivery = CrateDel(5, 10, 1)
    """

    def __init__(self, x, y, height):
        """
        Initializes a CrateDel with specified coordinates and height.
        
        Args:
            x (int): The x-coordinate of the crate delivery point.
            y (int): The y-coordinate of the crate delivery point.
            height (int): The height of the crate delivery point.
        """
        super().__init__(x, y, height, pickable=False)
        self.pickable = False  # Crate delivery points cannot be picked up
        self.active = False  # Whether it will delete a crate or not in the next tick
        

    def __str__(self):
        """
        String representation of the crate delivery point.

        Returns:
            str: String representation of the crate delivery point.
        """
        return "Crate delivery"