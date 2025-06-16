"""
Missing image renderer module.
Creates a replacement image for missing textures.

Methods:
    - missing_texture_pygame: Returns a pygame surface with the missing texture.
    - missing_texture_png: Returns a PNG image bytes with the missing texture.
    - render_missing_texture: Generates an image with a checkerboard pattern for missing textures.
    - hex_2_rgb: Converts a hex color value string to an RGB tuple.
"""

import logging
import pygame
import io
import numpy as np
from PIL import Image


def missing_texture_pygame(size_x=64, size_y=64, color_on='#ff00dc', color_off='#010001'):
    """
    Create a pygame surface missing texture image based on the colors and size provided.
    This function should be called as backup when a texture is missing.

    Args:
        size_x (int, optional): Width of the image. Default is 64.
        size_y (int, optional): Height of the image. Default is 64.
        color_on (str, optional): Color of the "on" blocks. Default is '#ff00dc'.
        color_off (str, optional): Color of the "off" blocks. Default is '#010001'.

    Returns:
        pygame.Surface: Surface object with the missing texture.
    """
    raw_img = render_missing_texture(size_x, size_y, color_on, color_off)
    return pygame.image.fromstring(raw_img.tobytes(), raw_img.size, "RGB")


def missing_texture_png(size_x=64, size_y=64, color_on='#ff00dc', color_off='#010001'):
    """
    Create a pygame surface missing texture image based on the colors and size provided.
    This function should be called as backup when a texture is missing.

    Args:
        size_x (int, optional): Width of the image. Default is 64.
        size_y (int, optional): Height of the image. Default is 64.
        color_on (str, optional): Color of the "on" blocks. Default is '#ff00dc'.
        color_off (str, optional): Color of the "off" blocks. Default is '#010001'.

    Returns:
        bytes: PNG image bytes with the missing texture
    """
    raw_img = render_missing_texture(size_x, size_y, color_on, color_off)
    img_bytes = io.BytesIO()
    raw_img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


def render_missing_texture(size_x=64, size_y=64, color_on='#ff00dc', color_off='#010001'):
    """
    Create a missing texture image based on the colors and size provided.
    This function should be called as backup when a texture is missing.
    Args:
        size_x (int, optional): Width of the image. Default is 64.
        size_y (int, optional): Height of the image. Default is 64.
        color_on (str, optional): Color of the "on" blocks. Default is '#ff00dc'.
        color_off (str, optional): Color of the "off" blocks. Default is '#010001'.
    Returns:
        Image: Image object with the missing texture.
    """
    block_size = 8
    color_on_rgb = np.array(hex_2_rgb(color_on, default=(255, 0, 220)), dtype=np.uint8)  # Magenta
    color_off_rgb = np.array(hex_2_rgb(color_off, default=(1, 0, 1)), dtype=np.uint8)  # Almost black

    # Find the larger valid dimension, ensuring it's a multiple of block_size
    larger_dim = max(size_x, size_y)
    if larger_dim % block_size != 0:
        larger_dim += block_size - (larger_dim % block_size)  # Round up

    # Create a coordinate grid
    x = np.arange(larger_dim)
    y = np.arange(larger_dim)
    x, y = np.meshgrid(x // block_size, y // block_size)  # Normalize to block index

    # Generate checkerboard pattern (boolean mask)
    pattern = (x + y) % 2 == 0

    # Create an RGB array and apply colors
    pixels = np.zeros((larger_dim, larger_dim, 3), dtype=np.uint8)
    pixels[pattern] = color_on_rgb
    pixels[~pattern] = color_off_rgb

    # Convert to PIL image
    img = Image.fromarray(pixels, 'RGB')

    # Crop to the exact size
    img = img.crop((0, 0, size_x, size_y))

    return img
    

def hex_2_rgb(hex_color, default=(0, 0, 0)):
    """
    Convert a hex color to an RGB tuple.
    The color needs to include the # symbol.

    Args:
        hex_color (str): Hex color to be converted.

    Returns:
        tuple: RGB tuple with the color values.
    """
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    except (ValueError, TypeError, IndexError):
        logging.error(f"Invalid hex color: {hex_color}, using default {default}")
        return default
