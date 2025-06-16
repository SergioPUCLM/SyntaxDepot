"""
Crate generator class module.

This module defines the CrateGen class, which represents crate generators in the game.
It inherits from the Entity class and serves as objectives for spawning crates.

Classes:
    CrateGen (Entity): Represents a crate generator in the game, which cannot be picked up and serves as an objective for spawning crates.
"""

from src.entities.entity import Entity


class CrateGen(Entity):
    """
    CrateGen class, defining the crate generators in the game. Inherits from Entity.
    Crate generators sit on the tile level and cannot be picked up.
    Crate generators serve as objectives in the game, spawning a defined number of crates on top of them at ground level.

    Attributes:
        x (int): The x-coordinate of the crate generator.
        y (int): The y-coordinate of the crate generator.
        height (int): The height of the crate generator.
        crate_count (int): Number of crates to spawn on top of the crate generator. Defaults to 0.
        crate_type (str): Type of crate generated ("big" or "small"). Defaults to "big".
        active (bool): Whether the crate generator has a crate on top of it or not. Defaults to False.

    Methods:
        __init__(x, y, height, crate_count=0, crate_type="big"): Initializes a CrateGen with specified coordinates, height, crate count, and crate type.
        __str__(): String representation of the crate generator.

    Example:
        crate_gen = CrateGen(x=10, y=20, height=5, crate_count=3, crate_type="big")
    """

    def __init__(self, x, y, height, crate_count=0, crate_type="big"):
        """
        Initializes a CrateGen with specified coordinates, height, crate count, and crate type.
        
        Args:
            x (int): The x-coordinate of the crate generator.
            y (int): The y-coordinate of the crate generator.
            height (int): The height of the crate generator.
            crate_count (int, optional): Number of crates to spawn on top of the crate generator. Defaults to 0.
            crate_type (str, optional): Type of crate generated ("big" or "small"). Defaults to "big".
        """
        super().__init__(x, y, height, pickable=False)
        self.pickable = False  # Crate generators cannot be picked up
        self.active = False  # Whether the crate generator has a crate on top of it or not
        self.crate_count = crate_count  # Number of crates to spawn on top of the crate generator
        self.crate_type = crate_type  # Type of crate generated (big or small)
        self.active = False  # Whether in the next tick it will spawn a crate or not


    def __str__(self):
        """
        String representation of the crate generator.

        Returns:
            str: String representation of the crate generator.
        """
        return "Crate generator"