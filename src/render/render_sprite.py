import os
import pygame
import logging
from src.render.missing_image import missing_texture_pygame

SPRITES_FOLDER = "res/sprites/"  # Default sprite directory

def load_sprite(sprite_name, tile_size, color_on='#ff00dc', color_off='#010001', entity=None):
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
        if "inputter" in sprite_name:
            sprite = pygame.image.load(sprite_path).convert_alpha()

            new_color_1 = pygame.Color(entity.input_ter_one)
            new_color_2 = pygame.Color(entity.input_ter_two)

            replace_color_1 = (255, 216, 0)  # Yellow
            replace_color_2 = (0, 38, 255)  # Blue

            sprite = sprite.convert_alpha()
            pixels = pygame.PixelArray(sprite)

            # Replace colors
            for x in range(sprite.get_width()):
                for y in range(sprite.get_height()):
                    current_color = sprite.unmap_rgb(pixels[x, y])[:3]
                    if current_color == replace_color_1:
                        pixels[x, y] = new_color_1
                    elif current_color == replace_color_2:
                        pixels[x, y] = new_color_2

            del pixels

        elif "outputter" in sprite_name:
            sprite = pygame.image.load(sprite_path).convert_alpha()
            new_color = pygame.Color(entity.color)
            replace_color = (255, 216, 0)
            
            sprite = sprite.convert_alpha()
            pixels = pygame.PixelArray(sprite)

            for x in range(sprite.get_width()):
                for y in range(sprite.get_height()):
                    current_color = sprite.unmap_rgb(pixels[x, y])[:3]
                    if current_color == replace_color:
                        pixels[x, y] = new_color

        else :
            sprite = pygame.image.load(sprite_path)
        
        sprite = pygame.transform.scale(sprite, size)
        return sprite
    except Exception as e:
        print(f"Error loading sprite: {e}")
        return missing_texture_pygame(tile_size, tile_size, color_on, color_off)

