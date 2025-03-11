"""Input terminal class module."""

import random
from src.entities.entity import Entity


class InputTer(Entity):
    """
    InputTer class, defining the input terminals in the game. Inherits from Entity.
    Input terminals sit on the ground level and cannot be picked up.
    Input terminals serve as objectives in the game, requiring a blue robot to input the operation of two terminals.
    """

    def __init__(self, x, y, height, ter_one=None, ter_two=None):
        super().__init__(x, y, height, pickable=False)
        self.pickable = False  # Input terminals cannot be picked up
        self.input_ter_one = ter_one  # Color of thefirst terminal
        self.input_ter_two = ter_two  # Color of the second terminal
        self.operation = self.generate_operation()  # Random operation for the input terminal


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


    def generate_operation(self):
        """
        Generates a random operation for the input terminal to store and return inmediately.

        Returns:
            int: Random operation for the input terminal.
        """
        operation = random.choice(["+", "-", "*", "/"])
        self.operation = operation
        return operation