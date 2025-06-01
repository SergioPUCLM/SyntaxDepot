"""Output terminal class module."""

import random
from src.entities.entity import Entity


class OutputTer(Entity):
    """
    OutputTer class, defining the output terminals in the game. Inherits from Entity.
    Output terminals sit on the ground level and cannot be picked up.
    Output terminals serve as objectives in the game, requiring a blue robot to get a number from them.
    """

    def __init__(self, x, y, color, height):
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