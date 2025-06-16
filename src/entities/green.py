"""
Green robot class.

This module defines the Green class, which represents a green robot in the game.
It inherits from the Robot class and serves as a specific type of robot with unique properties and behaviors.
Green robots fly at air level, can pick up small crates, but cannot pick up big crates or interact with terminals.

Classes:
    Green (Robot): Represents a green robot in the game, which can pick up small crates and interact with terminals.
"""

from src.entities.robot import Robot


class Green(Robot):
    """
    Green robot class, defining the structure of a green robot in-game. This class inherits from the Robot class.
    Green can pickup small crates, and moves at air level.
    Green can interact with terminals.

    Attributes:
        x (int): The x-coordinate of the robot.
        y (int): The y-coordinate of the robot.
        direction (str): The initial direction of the robot, default is 'N' (North).
        pickable (bool): Indicates whether the robot can be picked up, default is False.
        color (str): The color of the robot, set to 'Green'.
        crate (Crate or None): The crate the robot is currently holding, initially None.

    Methods:
        __init__(x, y, direction='N'): Initializes a Green robot at the specified coordinates and direction.
        __str__(): Returns a string representation of the green robot.

    Example:
        green_robot = Green(5, 10, 'N')
    """

    def __init__(self, x, y, direction='N'):
        """
        Initialize a Green robot at the specified coordinates and direction.
        
        Args:
            x (int): The x-coordinate of the robot.
            y (int): The y-coordinate of the robot.
            direction (str): The initial direction of the robot, default is 'N' (North).
        """
        super().__init__(x, y, 0, direction)
        self.pickable = False  # Green robots cannot be picked up
        self.color = 'Green'  # Color of the robot is Green

        self.crate = None  # Crate the robot is currently holding


    def __str__(self):
        """
        String representation of the green robot.

        Returns:
            str: String representation of the green robot.
        """
        return f"Green"