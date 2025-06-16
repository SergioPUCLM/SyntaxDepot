"""
Crate class module.

This module defines the Crate class, which represents pickable crates in the game.
It inherits from the Entity class and serves as objectives for robots to pick up.

Classes:
    Crate (Entity): Represents a pickable crate in the game, which can be picked up by robots and serves as an objective.
"""

from src.entities.entity import Entity

class Crate(Entity):
    """
    Crate class, defining the pickable crates in the game. Inherits from Entity. Existance of a crate defines an objective.
    Crates sit on the ground level and can be picked up by red and green robots, depending on their size.

    Attributes:
        small (bool): Whether the crate is small or not. Defaults to False (big crate).
        pickable (bool): Indicates whether the crate can be picked up. Always True for crates.
        
    Methods:
        __init__(x, y, height, small=False): Initializes a Crate with specified coordinates, height, and size.
        __str__(): String representation of the crate.

    Example:
        crate = Crate(10, 20, 5, small=True)
    """

    def __init__(self, x, y, height, small=False):
        """
        Initializes a Crate with specified coordinates, height, and size.
        
        Args:
            x (int): The x-coordinate of the crate.
            y (int): The y-coordinate of the crate.
            height (int): The height of the crate.
            small (bool, optional): Whether the crate is small or not. Defaults to False (big crate).
        """
        super().__init__(x, y, height, pickable=True)
        self.small = small # Whether the crate is small or not
        self.pickable = True  # Crates can be picked up


    def __str__(self):
        """
        String representation of the crate.

        Returns:
            str: String representation of the crate.
        """
        icon = "Big Crate"
        if self.small:
            icon = "Small Crate"
        return icon