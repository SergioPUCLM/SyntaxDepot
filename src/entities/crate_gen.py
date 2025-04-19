"""Crate generator class module."""

from src.entities.entity import Entity


class CrateGen(Entity):
    """
    CrateGen class, defining the crate generators in the game. Inherits from Entity.
    Crate generators sit on the tile level and cannot be picked up.
    Crate generators serve as objectives in the game, spawning a defined number of crates on top of them at ground level.
    """

    def __init__(self, x, y, height, crate_count=0, crate_type="big"):
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