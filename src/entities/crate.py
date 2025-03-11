"""Crate class module"""

from src.entities.entity import Entity

class Crate(Entity):
    """
    Crate class, defining the pickable crates in the game. Inherits from Entity. Existance of a crate defines an objective.
    Crates sit on the ground level and can be picked up by red and green robots, depending on their size.
    """

    def __init__(self, x, y, height, small=False):
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