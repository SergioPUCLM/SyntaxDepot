"""
Charge pad class module.

This module defines the ChargePad class, which represents charge pads in the game.
It inherits from the Entity class and serves as objectives that require a ground robot to be on top of them at the end of the script.

Classes:
    ChargePad (Entity): Represents a charge pad in the game, serving as an objective for ground robots.
"""

from src.entities.entity import Entity


class ChargePad(Entity):
    """
    ChargePad class, defining the charge pads in the game. Inherits from Entity.
    Chage pads sit on the tile level and cannot be picked up.
    Chage pads serve as objectives in the game, requiring a ground robot to be on top of them at the end of the script.

    Attributes:
        x (int): The x-coordinate of the charge pad.
        y (int): The y-coordinate of the charge pad.
        height (int): The height of the charge pad.
        pickable (bool): Whether the charge pad can be picked up. Always False for ChargePad.
        active (bool): Whether the charge pad has a robot on top of it or not.

    Methods:
        __init__(x, y, height): Initializes a ChargePad with specified coordinates and height.
        __str__(): String representation of the charge pad.

    Example:
        charge_pad = ChargePad(5, 10, 0)
    """

    def __init__(self, x, y, height):
        """
        Initializes a ChargePad with specified coordinates and height.

        Args:
            x (int): The x-coordinate of the charge pad.
            y (int): The y-coordinate of the charge pad.
            height (int): The height of the charge pad.
        """
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