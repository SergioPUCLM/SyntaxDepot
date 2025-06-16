"""
Robot class.
This module defines the Robot class, which serves as a base class for different types of robots in the game.
It inherits from the Entity class and provides a structure for robots with unique properties and behaviors.

Classes:
    Robot (Entity): Represents a robot in the game, which can be of different colors and has specific properties.
"""

import logging
from src.entities.entity import Entity


class Robot(Entity):
    """
    Robot class, defining the structure of a robot in-game. This class inherits from the Entity class.
    Robots will be of 3 different types: Red, Green, and Blue, each with their own unique properties.

    Attributes:
        x (int): The x-coordinate of the robot.
        y (int): The y-coordinate of the robot.
        height (int): The height at which the robot operates (0 for ground level, 1 for air level).
        direction (str): The initial direction of the robot, default is 'N' (North).
        pickable (bool): Whether the robot can be picked up, default is False.
        script (str): Script to be executed by the robot.
        color (str): Color of the robot, can be 'Red', 'Green', or 'Blue'.

    Methods:
        __init__(x, y, height, direction='N', pickable=False): Initializes a Robot at the specified coordinates, height, and direction.
        __str__(): String representation of the robot.

    Example:
        robot = Robot(0, 0, 0, direction='N', pickable=False)

    Note: Do not instantiate this class directly. Instead, use the specific robot types like Red, Green, or Blue.
    """
    def __init__(self, x, y, height, direction='N', pickable=False):
        """
        Initialize a Robot at the specified coordinates, height, and direction.
        
        Args:
            x (int): The x-coordinate of the robot.
            y (int): The y-coordinate of the robot.
            height (int): The height at which the robot operates (0 for ground level, 1 for air level).
            direction (str): The initial direction of the robot, default is 'N' (North).
            pickable (bool): Whether the robot can be picked up, default is False.
        """
        super().__init__(x, y, height, direction, pickable)
        self.direction = direction  # Direction the robot is facing, can be 'N', 'S', 'E', 'W'
        self.pickable = False  # Robots cannot be picked up

        self.script = ""  # Script to be executed by the robot
        self.color = ""  # Color of the robot, can be 'Red', 'Green', 'Blue'


    def __str__(self):
        """
        String representation of the robot.

        Returns:
            str: String representation of the robot.
        """
        return f"R?"  # R? for Robot, Should not really appear as specific robot types are used instead