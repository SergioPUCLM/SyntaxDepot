"""Main File"""

import sys
import os
import logging
import pygame
import pygame_gui

from src.setup import setup_paths
setup_paths()  # Set up the package paths for local imports

# Other imports
from src.render.menu import MainMenu
from src.render.level_select import LevelSelect
from src.render.game import GameScreen
from src.render.missing_image import missing_texture_pygame
from src.script.game_manager import GameManager

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
GAME_NAME = "Syntax Depot"

FONTS = ["res/fonts/PixelOperator8.ttf", "res/fonts/PixelOperatorMono8.ttf"]


def main():
    """
    Main function of the game.
    """

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting the game")

    # Check Python version is compatible with match-case
    python_version = sys.version_info
    logging.debug(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        logging.error("Python 3.10 or newer is required.")
        sys.exit(1)

    # Initial setup
    pygame.init()  # Initialize pygame	
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)  # Create the screen
    pygame.display.set_caption(f"{GAME_NAME} - Main menu")  # Set the window title
    game_manager = GameManager()  # Create the game manager
    manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))  # Create the UI manager
    manager.get_theme().get_font_dictionary().add_font_path("PixelOperator8", FONTS[0])  # Add the custom font 1
    manager.get_theme().get_font_dictionary().add_font_path("PixelOperatorMono8", FONTS[1])  # Add the custom font 2
    manager.get_theme().load_theme("./res/theme.json")  # Load the theme

    try:
        icon = pygame.image.load(os.path.join("assets", "icon.png"))  # Load the icon
    except FileNotFoundError:
        logging.error("Icon not found. Using fallback texture")
        icon = missing_texture_pygame(size_x=16, size_y=16)

    pygame.display.set_icon(icon)  # Set the icon


    # Scene management
    def change_scene(new_scene, level_name=None):
        """Changes the current scene and resets UI elements."""
        nonlocal current_scene, manager, running

        logging.debug(f"Switching to scene: {new_scene}")

        # Quit the game when selecting None as the new scene
        if new_scene is None:
            running = False
            return

        # Destroy the current scene before switching
        if scenes[current_scene]:
            scenes[current_scene].destroy()

        # Create the new scene
        match new_scene:
            case "game":
                raw_name = level_name.split("_", 1)[1]
                scenes[new_scene] = GameScreen(screen, manager, change_scene, game_manager, level_name)
                pygame.display.set_caption(f"{GAME_NAME} - Playing level: {raw_name}")
            case "level_select":
                scenes[new_scene] = LevelSelect(screen, manager, change_scene, game_manager)
                pygame.display.set_caption(f"{GAME_NAME} - Pick a level")
            case "menu":
                scenes[new_scene] = MainMenu(screen, manager, change_scene)
                pygame.display.set_caption(f"{GAME_NAME} - Main menu")

        current_scene = new_scene


    scenes = {
        # We use deferred initialization to avoid having render issues
        "menu": None,
        "level_select": None,  
        "game": None,
    }

    # Initial scene
    current_scene = "menu"
    scenes[current_scene] = MainMenu(screen, manager, change_scene)

    # Game loop
    clock = pygame.time.Clock()
    FPS = 60
    running = True

    logging.debug(f"Entering game loop with scene: {current_scene}")

    while running:
        time_delta = clock.tick(FPS) / 1000.0  # Convert to seconds

        # Handle events
        for event in pygame.event.get():
            manager.process_events(event)
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    manager.set_window_resolution((event.w, event.h))
                    scenes[current_scene].resize()
                case _:
                    scenes[current_scene].handle_events(event)

        # Update and render
        manager.update(time_delta)
        screen.fill((0, 0, 0))  # Black background
        scenes[current_scene].render()
        if scenes["game"]:
            scenes["game"].game_manager.tick()  # Update the game state
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()