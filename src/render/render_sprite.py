import os
import pygame
import logging
from src.render.missing_image import missing_texture_pygame

SPRITES_FOLDER = "res/sprites/"  # Default sprite directory

def load_sprite(sprite_name, tile_size, color_on='#ff00dc', color_off='#010001'):
    """
    Loads a sprite from the given name. If the file is missing, uses a fallback texture.

    Args:
        sprite_name (str): Name of the sprite file (e.g., "player.png").
        size (tuple): Desired (width, height) for the sprite.

    Returns:
        pygame.Surface: The loaded sprite or a fallback texture.
    """
    size=(tile_size, tile_size)
    sprite_path = os.path.join(SPRITES_FOLDER, sprite_name)

    try:
        sprite = pygame.image.load(sprite_path)
        sprite = pygame.transform.scale(sprite, size)
        return sprite
    except Exception as e:
        return missing_texture_pygame(tile_size, tile_size, color_on, color_off)
