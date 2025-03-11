"""Collectable class module."""

from src.entities.entity import Entity


class Collectable(Entity):
    """
    Collectable class, defining the collectables in the game. Inherits from Entity.
    Collectables sit on the tile or air level and will be automatically picked up by the robot when it moves over them.
    Collectables serve as a side objective in the game, and are not required to complete the level.
    """

    def __init__(self, x, y, height):
        super().__init__(x, y, height)
        self.pickable = False  # Collectables can be picked up but not in the traditional sense


    def __str__(self):
        """
        String representation of the collectable.

        Returns:
            str: String representation of the collectable.
        """
        return "Collectable"