"""Crate delivery class module."""

from src.entities.entity import Entity


class CrateDel(Entity):
    """
    CrateDel class, defining the crate delivery points in the game. Inherits from Entity.
    Crate delivery points sit on the tile level and cannot be picked up.
    Crate delivery points serve as objectives in the game, requiring a ground robot to be on top of them at the end of the script.
    """

    def __init__(self, x, y, height):
        super().__init__(x, y, height, pickable=False)
        self.pickable = False  # Crate delivery points cannot be picked up
        

    def __str__(self):
        """
        String representation of the crate delivery point.

        Returns:
            str: String representation of the crate delivery point.
        """
        return "Crate delivery"