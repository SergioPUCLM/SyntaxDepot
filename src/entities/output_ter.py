"""
Output terminal class module.

This module defines the OutputTer class, which represents output terminals in the game.
It inherits from the Entity class and serves as an objective for blue robots to get a number from them.

Classes:
    OutputTer (Entity): Represents an output terminal in the game, which requires a blue robot to get a number from it.
"""

import random
from src.entities.entity import Entity


class OutputTer(Entity):
    """
    OutputTer class, defining the output terminals in the game. Inherits from Entity.
    Output terminals sit on the ground level and cannot be picked up.
    Output terminals serve as objectives in the game, requiring a blue robot to get a number from them.

    Attributes:
        color (str): Color of the output terminal, used as an ID for input terminals to request the number from here.
        number (int): Random number stored in the output terminal.

    Methods:
        __init__(x, y, color, height): Initializes an OutputTer at the specified coordinates, color, and height.
        __str__(): String representation of the output terminal.
        generate_number(): Generates a random number for the output terminal to store and return immediately.
        
    Example:
        output_terminal = OutputTer(x=5, y=10, color="red", height=0)
    """

    def __init__(self, x, y, color, height):
        """
        Initialize an OutputTer at the specified coordinates, color, and height.

        Args:
            x (int): The x-coordinate of the output terminal.
            y (int): The y-coordinate of the output terminal.
            color (str): Color of the output terminal, used as an ID for input terminals to request the number from here.
            height (int): The height of the output terminal.
        """
        super().__init__(x, y, height, pickable=False)
        self.pickable = False  # Output terminals cannot be picked up
        self.color = color  # Color of the terminal, will be used as ID for input terminals to request the number from here
        self.number = self.generate_number()  # Number stored in the output terminal


    def __str__(self):
        """
        String representation of the output terminal.

        Returns:
            str: String representation of the output terminal.
        """
        icon = "Output Terminal"
        if self.number:
            icon = "Output Terminal " + str(self.number)
        return icon


    def generate_number(self):
        """
        Generates a random number for the output terminal to store and return inmediately.

        Returns:
            int: Random number for the output terminal.
        """
        number = random.randint(0, 99)
        self.number = number
        return number