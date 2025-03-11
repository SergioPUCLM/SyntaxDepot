"""Robot class"""

import logging
from src.entities.entity import Entity


class Robot(Entity):
    """
    Robot class, defining the structure of a robot in-game. This class inherits from the Entity class.
    Robots will be of 3 different types: Red, Green, and Blue, each with their own unique properties.
    """
    def __init__(self, x, y, height, direction='N', pickable=False):
        super().__init__(x, y, height, direction, pickable)
        self.direction = direction  # Direction the robot is facing, can be 'N', 'S', 'E', 'W'
        self.pickable = False  # Robots cannot be picked up

        self.script = ""  # Script to be executed by the robot TODO: Define how scripts are handled
        self.color = ""  # Color of the robot, can be 'Red', 'Green', 'Blue'


    def __str__(self):
        """
        String representation of the robot.

        Returns:
            str: String representation of the robot.
        """
        return f"R?"  # R? for Robot, Should not really appear as specific robot types are used instead