"""Red robot class"""

from src.entities.robot import Robot


class Red(Robot):
    """
    Red robot class, defining the structure of a red robot in-game. This class inherits from the Robot class.
    Red can pickup crates of both sizes, and moves at ground level.
    Red cannot interact with terminals.
    """

    def __init__(self, x, y, direction='N'):
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
