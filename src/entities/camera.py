"""Camera entity module."""

import threading
import logging
from src.entities.entity import Entity


class Camera(Entity):
    """
    Camera class, defining the camera / cursor in the game. Inherits from Entity.
    Cameras sit on the camera level and cannot be picked up.
    Cameras serve as the player's way of moving around and selecting things.
    """
    def __init__(self, x, y, height, direction='N'):
        super().__init__(x, y, height, direction=direction, pickable=False)
        self.direction = direction
        self.pickable = False

    def __str__(self):
        """
        String representation of the camera.
        """
        return "Camera"