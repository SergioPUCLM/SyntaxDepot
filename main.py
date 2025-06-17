"""
Main module.
Starts the game and handles the main loop.

This program was developed as part of the bachelor's dissertation in Computer Engineering at the University of Castille-La Mancha (UCLM), Spain.

Developed by: Sergio Pozuelo Martin-Consuegra
Supervised by: Jose Jesus Castro Sanchez

Thanks to:
- Jayvee Enaguas (Zeh Fernando): Pixel Operator font (https://www.dafont.com/pixel-operator.font)
- Alberto Barrais Bellerin: Testing and general feedback
- Manuel Cano Garcia: User interface feedback
- Alejandro Cañas Borreguero: General feedback
- Francisco Javier Luna: User interface feedback
- Luis Benito Lopez: General feedback
- Daniel Ayuso del Campo: General feedback
- Valeria Samani Padilla Cuba: Game art ideas

May this game provide as much enjoyment to you as it did to me while developing it.
"""

import sys
import os
import logging
import json
import pygame
import pygame_gui
from pygame_gui.core.text.text_box_layout_row import TextBoxLayoutRow

from src.setup import setup_paths
setup_paths()  # Set up the package paths for local imports

# Other imports
from src.render.menu import MainMenu
from src.render.level_select import LevelSelect
from src.render.game import GameScreen
from src.render.missing_image import missing_texture_pygame
from src.script.game_manager import GameManager
from src.render.error_handler import error_handler
from src.render.sound_manager import sound_manager

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
GAME_NAME = "Syntax Depot"
DATA_FILE = "data/options.json"
SPRITES_FOLDER = "res/sprites"
SFX_FOLDER = "res/sfx"

FONTS = ["res/fonts/PixelOperator8.ttf", "res/fonts/PixelOperatorMono8.ttf"]


def main():
    """
    Main function of the game.
    """
    # Monkey-patch pygame_gui to fix text box insert errors
    og_text_insert = TextBoxLayoutRow.insert_text
    def safe_insert_text(self, text, index_in_row, parser):
        """
        Attempt to insert text into the TextBoxLayoutRow by clamping the index.
        This is a workaround for a bug in pygame_gui that causes text insertion to fail.
        It will still fail to insert the text BUT it will not crash the game.
        Ideally, they should patch this on their end, but that could take a while.
        """
        index_in_row = min(index_in_row, self.letter_count)  # Clamp it to try and fix it
        try:
            return og_text_insert(self, text, index_in_row, parser)
        except RuntimeError as e:
            return False

    TextBoxLayoutRow.insert_text = safe_insert_text

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
    manager.get_theme().load_theme("./theme.json")  # Load the theme

    pygame.mixer.init(channels=17)  # Initialize the mixer with 17 channels
    pygame.mixer.set_num_channels(17)  # Channel 0 = music, 1 - 16 = SFX
    sound_manager.initialize()

    error_handler.set_ui_manager(manager)  # Set the UI manager for the error handler
    error_handler.load_icons()  # Load the icons for the error handler

    # Load sounds
    sound_manager.load_sound("click", os.path.join(SFX_FOLDER, "click.wav"), is_music=False)  # Button click sound
    sound_manager.load_sound("error", os.path.join(SFX_FOLDER, "error.wav"), is_music=False)  # Error sound
    sound_manager.load_sound("warning", os.path.join(SFX_FOLDER, "warning.wav"), is_music=False)  # Warning sound
    sound_manager.load_sound("info", os.path.join(SFX_FOLDER, "info.wav"), is_music=False)  # Info sound
    sound_manager.load_sound("finish_level", os.path.join(SFX_FOLDER, "finish_level.wav"), is_music=False)  # Finish level sound
    sound_manager.load_sound("reset_level", os.path.join(SFX_FOLDER, "reset_level.wav"), is_music=False)  # Reset level sound
    sound_manager.load_sound("help", os.path.join(SFX_FOLDER, "help.wav"), is_music=False)  # Help sound
    sound_manager.load_sound("camera", os.path.join(SFX_FOLDER, "camera.wav"), is_music=False)  # Help sound

    sound_manager.load_sound("red_move", os.path.join(SFX_FOLDER, "red_move.wav"), is_music=False)  # Red move sound
    sound_manager.load_sound("blue_move", os.path.join(SFX_FOLDER, "blue_move.wav"), is_music=False)  # Blue move sound
    sound_manager.load_sound("green_move", os.path.join(SFX_FOLDER, "green_move.wav"), is_music=False)  # Green move sound
    sound_manager.load_sound("pickup_big", os.path.join(SFX_FOLDER, "pickup_big.wav"), is_music=False)  # Big pickup sound
    sound_manager.load_sound("pickup_small", os.path.join(SFX_FOLDER, "pickup_small.wav"), is_music=False)  # Small pickup sound
    sound_manager.load_sound("drop_big", os.path.join(SFX_FOLDER, "drop_big.wav"), is_music=False)  # Big drop sound
    sound_manager.load_sound("drop_small", os.path.join(SFX_FOLDER, "drop_small.wav"), is_music=False)  # Small drop sound
    sound_manager.load_sound("correct", os.path.join(SFX_FOLDER, "correct.wav"), is_music=False)  # Correct sound
    sound_manager.load_sound("incorrect", os.path.join(SFX_FOLDER, "incorrect.wav"), is_music=False)  # Incorrect sound
    sound_manager.load_sound("crate_spawn", os.path.join(SFX_FOLDER, "crate_spawn.wav"), is_music=False)  # Crate spawn sound
    sound_manager.load_sound("crate_delete", os.path.join(SFX_FOLDER, "crate_delete.wav"), is_music=False)  # Crate delete sound
    sound_manager.load_sound("charge", os.path.join(SFX_FOLDER, "charge.wav"), is_music=False)  # Charge sound
    sound_manager.load_sound("collectable", os.path.join(SFX_FOLDER, "collectable.wav"), is_music=False)  # Collectable pickup sound
    sound_manager.load_sound("trap_activate", os.path.join(SFX_FOLDER, "trap_activate.wav"), is_music=False)  # Trap activate sound

    # Load music
    sound_manager.load_sound("menu", os.path.join(SFX_FOLDER, "menu.wav"), is_music=True)  # Menu music
    sound_manager.load_sound("think", os.path.join(SFX_FOLDER, "think.wav"), is_music=True)  # Thinking music
    sound_manager.load_sound("play", os.path.join(SFX_FOLDER, "play.wav"), is_music=True)  # Play music

    sound_manager.play("menu", fade_ms=1000)  # Play the menu music

    # Check if options.json exists and if it has the correct data:
    if not os.path.exists(DATA_FILE):
        logging.warning("Options file not found. Creating a new one.")
        with open(DATA_FILE, "w") as f:
            f.write('{"last_player": "Anonymous", "mute": 0}')
    else:
        with open(DATA_FILE, "r") as f:
            try:
                options = json.load(f)
                if not isinstance(options, dict):
                    # Recreate the file if it's not a dictionary
                    logging.warning("Options file is not a dictionary. Recreating the file.")
                    f.seek(0)
                    f.truncate()
                    f.write('{"last_player": "Anonymous", "mute": 0, "mute_music": 0}')
                if "last_player" not in options or "mute" not in options or "mute_music" not in options:
                    # Recreate the file with default values
                    logging.warning("Options file is missing keys. Recreating the file.")
                    f.seek(0)
                    f.truncate()
                    f.write('{"last_player": "Anonymous", "mute": 0, "mute_music": 0}')
            except (json.JSONDecodeError, ValueError) as e:
                # Recreate the file if there's a JSON error
                logging.warning(f"Options file is corrupted: {e}. Recreating the file.")
                with open(DATA_FILE, "w") as f:
                    f.write('{"last_player": "Anonymous", "mute": 0, "mute_music": 0}')
            except Exception as e:
                # Catch all other exceptions
                logging.error(f"Unexpected error while loading options: {e}. Recreating the file.")
                with open(DATA_FILE, "w") as f:
                    f.write('{"last_player": "Anonymous", "mute": 0, "mute_music": 0}')

    # Load the mute setting
    with open(DATA_FILE, "r") as f:
        options = json.load(f)
        if int(sound_manager.muted) != options["mute"]:
            sound_manager.toggle_mute()
        if int(sound_manager.music_muted) != options.get("mute_music", 0):
            sound_manager.toggle_music()

    try:
        icon = pygame.image.load(os.path.join(SPRITES_FOLDER, "icon.png"))  # Load the icon
    except FileNotFoundError:
        logging.error("Icon not found. Using fallback texture")
        icon = missing_texture_pygame(size_x=32, size_y=32)

    pygame.display.set_icon(icon)  # Set the icon

    # Scene management
    def change_scene(new_scene, level_name=None, level_folder=None):
        """
        Changes the current scene and resets UI elements.
        
        Args:
            new_scene (str): The name of the new scene to switch to.
            level_name (str, optional): The name of the level to load in the game scene.
            level_folder (str, optional): The folder containing the level data.
        """
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
                if sound_manager.current_music != "think":
                    sound_manager.play("think", fade_ms=500)
                raw_name = level_name.split("_", 1)[1]
                scenes[new_scene] = GameScreen(screen, manager, change_scene, game_manager, level_name, level_folder)
                pygame.display.set_caption(f"{GAME_NAME} - Playing level: {raw_name}")
            case "level_select":
                if sound_manager.current_music != "menu":
                    sound_manager.play("menu", fade_ms=500)
                scenes[new_scene] = LevelSelect(screen, manager, change_scene, game_manager)
                pygame.display.set_caption(f"{GAME_NAME} - Pick a level")
            case "menu":
                if sound_manager.current_music != "menu":
                    sound_manager.play("menu", fade_ms=500)
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

    while running:
        time_delta = clock.tick(FPS) / 1000.0  # Convert to seconds

        # Handle events
        events = pygame.event.get()  # Get all events
        for event in events:
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
        error_handler.update(time_delta, events) 

        screen.fill((0, 0, 0))  # Black background
        scenes[current_scene].render()
        scenes[current_scene].update(time_delta)
        if scenes["game"]:
            scenes["game"].game_manager.tick()  # Update the game state
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    """
    Entry point of the game.
    """
    main()
    