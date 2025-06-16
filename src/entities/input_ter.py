"""
Input terminal class module.

This module defines the InputTer class, which represents input terminals in the game.
It inherits from the Entity class and serves as an objective for blue robots to input operations.

Classes:
    InputTer (Entity): Represents an input terminal in the game, which requires a blue robot to input the operation of two terminals.
"""

import random
from src.entities.entity import Entity


class InputTer(Entity):
    """
    InputTer class, defining the input terminals in the game. Inherits from Entity.
    Input terminals sit on the ground level and cannot be picked up.
    Input terminals serve as objectives in the game, requiring a blue robot to input the operation of two terminals.

    Attributes:
        input_ter_one (str): Color of the first terminal.
        input_ter_two (str): Color of the second terminal.
        activated (bool): Whether the input terminal has been activated.
        operation (str): Operation to be performed ["+", "-", "*", "/"].

    Methods:
        __init__(x, y, height, ter_one=None, ter_two=None, operation=None): Initializes an InputTer at the specified coordinates and height.
        __str__(): String representation of the input terminal.

    Example:
        input_terminal = InputTer(x=5, y=10, height=0, ter_one="red", ter_two="blue", operation="+")
    """

    def __init__(self, x, y, height, ter_one=None, ter_two=None, operation=None):
        """
        Initialize an InputTer at the specified coordinates and height.

        Args:
            x (int): The x-coordinate of the input terminal.
            y (int): The y-coordinate of the input terminal.
            height (int): The height of the input terminal.
            ter_one (str, optional): Color of the first terminal. Defaults to None.
            ter_two (str, optional): Color of the second terminal. Defaults to None.
            operation (str, optional): Operation to be performed ["+", "-", "*", "/"]. Defaults to None.
        """
        super().__init__(x, y, height, pickable=False)
        self.pickable = False  # Input terminals cannot be picked up
        self.input_ter_one = ter_one  # Color of thefirst terminal
        self.input_ter_two = ter_two  # Color of the second terminal
        self.activated = False  # Whether the input terminal has been activated
        self.operation = operation  # Operation to be performed ["+", "-", "*", "/"]


    def __str__(self):
        """
        String representation of the input terminal.

        Returns:
            str: String representation of the input terminal.
        """
        icon = "Input Terminal"
        if self.operation:
            icon = "Input Terminal " + self.operation
        return icon