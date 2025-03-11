"""Trap class module."""

from src.entities.entity import Entity


class Trap(Entity):
    """
    Trap class, defining the traps in the game. Inherits from Entity.
    Traps sit on the tile level and cannot be picked up.
    Traps serve as obstacles in the game, killing any entity that steps on them when active.
    Traps should be activated on a timer.
    """

    def __init__(self, x, y, height):
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