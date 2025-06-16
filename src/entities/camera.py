"""
Camera entity module.

This module defines the Camera class, which represents the camera or cursor in the game.
It inherits from the Entity class and serves as the player's way of moving around and selecting things.

Classes:
    Camera (Entity): Represents the camera in the game, allowing movement and selection.
"""

import threading
import logging
from src.entities.entity import Entity


class Camera(Entity):
    """
    Camera class, defining the camera / cursor in the game. Inherits from Entity.
    Cameras sit on the camera level and cannot be picked up.
    Cameras serve as the player's way of moving around and selecting things.

    Attributes:
        x (int): The x-coordinate of the camera.
        y (int): The y-coordinate of the camera.
        height (int): The height of the camera.
        direction (str): The initial direction of the camera, default is 'N'.
        pickable (bool): Indicates whether the camera can be picked up, default is False.

    Methods:
        __init__(x, y, height, direction='N'): Initializes a Camera with specified coordinates, height, and direction.
        __str__(): String representation of the camera.

    Example:
        camera = Camera(x=5, y=10, height=1, direction='N')
    """
    def __init__(self, x, y, height, direction='N'):
        """
        Initializes a Camera with specified coordinates, height, and direction.

        Args:
            x (int): The x-coordinate of the camera.
            y (int): The y-coordinate of the camera.
            height (int): The height of the camera.
            direction (str): The initial direction of the camera, default is 'N'.
        """
        super().__init__(x, y, height, direction=direction, pickable=False)
        self.direction = direction
        self.pickable = False

    def __str__(self):
        """
        String representation of the camera.

        Returns:
            str: String representation of the camera.
        """
        return "Camera"