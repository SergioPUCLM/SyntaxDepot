"""
Blue robot class.
This module defines the Blue class, which represents a blue robot in the game.
It inherits from the Robot class and specifies properties unique to blue robots.
Blue robots cannot pick up crates, move at ground level, and can interact with terminals.

Class: 
    Blue (Robot): Represents a blue robot in the game.
"""

from src.entities.robot import Robot


class Blue(Robot):
    """
    Blue robot class, defining the structure of a blue robot in-game. This class inherits from the Robot class.
    Blue cannot pickup crates, and moves at ground level.
    Blue can interact with terminals

    Attributes:
        x (int): The x-coordinate of the blue robot.
        y (int): The y-coordinate of the blue robot.
        direction (str): The initial direction of the blue robot, default is 'N'.
        pickable (bool): Indicates whether the blue robot can pick up crates, always False.
        color (str): The color of the robot, set to 'Blue'.

    Methods:
        __init__(x, y, direction='N'): Initializes a Blue robot with specified coordinates and direction.
        __str__(): String representation of the blue robot.

    Example:
        blue_robot = Blue(5, 10, 'E')
    """
    def __init__(self, x, y, direction='N'):
        """
        Initializes a Blue robot with specified coordinates and direction.
        
        Args:
            x (int): The x-coordinate of the blue robot.
            y (int): The y-coordinate of the blue robot.
            direction (str): The initial direction of the blue robot, default is 'N'.
        """
        super().__init__(x, y, 0, direction)
        self.pickable = False
        self.color = 'Blue'


    def __str__(self):
        """
        String representation of the blue robot.

        Returns:
            str: String representation of the blue robot.
        """
        return f"Blue"

    