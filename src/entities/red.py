"""
Red robot class.

This module defines the Red class, which represents a red robot in the game.
It inherits from the Robot class and serves as a specific type of robot with unique properties and behaviors.
Red robots move at ground level, can pick up crates of both sizes, but cannot interact with terminals.

Classes:
    Red (Robot): Represents a red robot in the game, which can pick up crates of both sizes and cannot interact with terminals.
"""

from src.entities.robot import Robot


class Red(Robot):
    """
    Red robot class, defining the structure of a red robot in-game. This class inherits from the Robot class.
    Red can pickup crates of both sizes, and moves at ground level.
    Red cannot interact with terminals.

    Attributes:
        pickable (bool): Whether the robot can be picked up, always False for Red robots.
        color (str): Color of the robot, always 'Red'.
        crate (Crate or None): The crate the robot is currently holding (big or small), initially None.

    Methods:
        __init__(x, y, direction='N'): Initializes a Red robot at the specified coordinates and direction.
        __str__(): String representation of the red robot.

    Example:
        red_robot = Red(x=5, y=10, direction='N')
    """

    def __init__(self, x, y, direction='N'):
        """
        Initialize a Red robot at the specified coordinates and direction.

        Args:
            x (int): The x-coordinate of the robot.
            y (int): The y-coordinate of the robot.
            direction (str): The initial direction of the robot, default is 'N' (North).
        """
        super().__init__(x, y, 0, direction)
        self.pickable = False  # Red robots cannot be picked up
        self.color = 'Red'  # Color of the robot is Red

        self.crate = None  # Crate the robot is currently holding (big or small)


    def __str__(self):
        """
        String representation of the red robot.

        Returns:
            str: String representation of the red robot.
        """
        return f"Red"  # R for Red robot
