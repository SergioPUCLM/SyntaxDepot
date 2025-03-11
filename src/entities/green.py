"""Green robot class"""

from src.entities.robot import Robot


class Green(Robot):
    """
    Green robot class, defining the structure of a green robot in-game. This class inherits from the Robot class.
    Green can pickup small crates, and moves at air level.
    Green can interact with terminals.
    """

    def __init__(self, x, y, direction='N'):
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