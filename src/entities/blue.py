"""Blue robot class"""

from src.entities.robot import Robot


class Blue(Robot):
    """
    Blue robot class, defining the structure of a blue robot in-game. This class inherits from the Robot class.
    Blue cannot pickup crates, and moves at ground level.
    Blue can interact with terminals
    """
    def __init__(self, x, y, direction='N'):
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

    