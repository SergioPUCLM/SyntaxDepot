"""Charge pad class module."""

from src.entities.entity import Entity


class ChargePad(Entity):
    """
    ChargePad class, defining the charge pads in the game. Inherits from Entity.
    Chage pads sit on the tile level and cannot be picked up.
    Chage pads serve as objectives in the game, requiring a ground robot to be on top of them at the end of the script.
    """

    def __init__(self, x, y, height):
        super().__init__(x, y, height, pickable=False)
        self.pickable = False  # Charge pads cannot be picked up
        self.active = False  # Whether the charge pad has a robot on top of it or not


    def __str__(self):
        """
        String representation of the charge pad.

        Returns:
            str: String representation of the charge pad.
        """
        return "Charge Pad"