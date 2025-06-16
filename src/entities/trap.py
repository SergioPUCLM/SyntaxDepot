"""
Trap class module.
This module defines the Trap class, which represents a dangeorus trap in the game.
It inherits from the Entity class and serves as an obstacle that can kill robots when activated, causing a level reset.

Classes:
    Trap (Entity): Represents a trap in the game, which can be activated to kill robots that step on it.
"""

from src.entities.entity import Entity


class Trap(Entity):
    """
    Trap class, defining the traps in the game. Inherits from Entity.
    Traps sit on the tile level and cannot be picked up.
    Traps serve as obstacles in the game, killing any entity that steps on them when active.
    Traps are activated on a tick timer.

    Attributes:
        x (int): The x-coordinate of the trap.
        y (int): The y-coordinate of the trap.
        height (int): The height at which the trap operates (0 for ground level).
        pickable (bool): Whether the trap can be picked up, default is False.
        active (bool): Whether the trap is currently active or not.

    Methods:
        __init__(x, y, height): Initializes a Trap at the specified coordinates and height.
        __str__(): String representation of the trap.
        switch_mode(): Switches the trap mode between active and inactive.

    Example:
        trap = Trap(5, 10, 0)
    """

    def __init__(self, x, y, height):
        """
        Initialize a Trap at the specified coordinates and height.

        Args:
            x (int): The x-coordinate of the trap.
            y (int): The y-coordinate of the trap.
            height (int): The height at which the trap operates (0 for ground level).
        """
        super().__init__(x, y, height, pickable=False)
        self.pickable = False  # Traps cannot be picked up
        self.active = False  # Whether the trap is deployed


    def __str__(self):
        """
        String representation of the trap.

        Returns:
            str: String representation of the trap.
        """
        if self.active:
            icon = "Active trap"
        else:
            icon = "Inactive trap"
        return icon


    def switch_mode():
        """
        Switches the trap mode between active and inactive.

        Returns:
            bool: The new mode of the trap.
        """
        self.active = not self.active
        return self.active