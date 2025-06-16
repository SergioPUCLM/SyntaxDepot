"""
Collectable class module.

This module defines the Collectable class, which represents collectable items in the game.
It inherits from the Entity class and serves as a side objective for players to collect.

Classes: 
    Collectable (Entity): Represents a collectable item in the game, which can be picked up by the robot.
"""

from src.entities.entity import Entity


class Collectable(Entity):
    """
    Collectable class, defining the collectables in the game. Inherits from Entity.
    Collectables sit on the tile or air level and will be automatically picked up by the robot when it moves over them.
    Collectables serve as a side objective in the game, and are not required to complete the level.

    Attributes:
        x (int): The x-coordinate of the collectable.
        y (int): The y-coordinate of the collectable.
        height (int): The height of the collectable.
        pickable (bool): Indicates whether the collectable can be picked up. Defaults to False since they are automatically collected.

    Methods:
        __init__(x, y, height): Initializes a Collectable with specified coordinates and height.
        __str__(): String representation of the collectable.

    Example:
        collectable = Collectable(5, 10, 0)
    """

    def __init__(self, x, y, height):
        """
        Initializes a Collectable with specified coordinates and height.

        Args:
            x (int): The x-coordinate of the collectable.
            y (int): The y-coordinate of the collectable.
            height (int): The height of the collectable.
        """
        super().__init__(x, y, height)
        self.pickable = False  # Collectables can be picked up but not in the traditional sense

    def __str__(self):
        """
        String representation of the collectable.

        Returns:
            str: String representation of the collectable.
        """
        return "Collectable"