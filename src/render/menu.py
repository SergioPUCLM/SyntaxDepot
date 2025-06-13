"""Main Menu Renderer"""

import pygame
import pygame_gui
import logging
import json
import os
import time
from string import ascii_letters, digits
from pathlib import Path
from src.render.missing_image import missing_texture_pygame
from src.render.sound_manager import sound_manager

SPRITE_FOLDER = "res/sprites/"
PLAYER_FOLDER = "data/player/"
DATA_FILE = "data/options.json"


class MainMenu:
    def __init__(self, screen, manager, change_scene):
        self.screen = screen
        self.manager = manager
        self.change_scene = change_scene
        self.name_changing = False
        self.player_name = self.load_player_name()

        # Load icons
        self.mute_icon_surface = None
        self.unmute_icon_surface = None
        try:
            self.mute_icon_surface = pygame.image.load(os.path.join(SPRITE_FOLDER, "mute.png")).convert_alpha()
            self.unmute_icon_surface = pygame.image.load(os.path.join(SPRITE_FOLDER, "unmute.png")).convert_alpha()
        except FileNotFoundError:
            logging.error("Mute icon not found. Using fallback texture")
            self.mute_icon_surface = missing_texture_pygame(size_x=16, size_y=16, color_on="#fc0303")
            self.unmute_icon_surface = missing_texture_pygame(size_x=16, size_y=16, color_on="#15FF00FF")

        self.mute_music_icon_surface = None
        self.unmute_music_icon_surface = None
        try:
            self.mute_music_icon_surface = pygame.image.load(os.path.join(SPRITE_FOLDER, "mute_music.png")).convert_alpha()
            self.unmute_music_icon_surface = pygame.image.load(os.path.join(SPRITE_FOLDER, "unmute_music.png")).convert_alpha()
        except FileNotFoundError:
            logging.error("Mute music icon not found. Using fallback texture")
            self.mute_music_icon_surface = missing_texture_pygame(size_x=16, size_y=16, color_on="#fc0303")
            self.unmute_music_icon_surface = missing_texture_pygame(size_x=16, size_y=16, color_on="#15FF00FF")

        self.create_ui()


    def create_ui(self):
        """Creates and positions UI elements dynamically."""
        width, height = self.screen.get_size()

        # Title label
        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((width * 0.25, height * 0.1), (width * 0.5, height * 0.1)),
            text="Syntax Depot",
            manager=self.manager,
            object_id="title",  
        )

        # Welcome label with red player name
        self.welcome_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((width * 0.25, height * 0.3), (width * 0.5, height * 0.1)),
            text=f"Welcome back, {self.player_name}!",
            manager=self.manager,
            object_id="subtitle"
        )

        # Name input (hidden by default)
        self.name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((width * 0.35, height * 0.3), (width * 0.3, height * 0.07)),
            manager=self.manager,
            object_id="name_input",
        )
        self.name_input.hide()
        self.name_input.set_allowed_characters(list(ascii_letters + digits) + ["_"])  # Only allow alphanumeric characters and underscores

        # Name change button
        self.name_change_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width * 0.32, height * 0.4), (width * 0.36, height * 0.07)),
            text="This isn't you? Click here",
            manager=self.manager,
            object_id="good_button"
        )

        # Play button
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width * 0.35, height * 0.65), (width * 0.3, height * 0.1)),
            text="Play",
            manager=self.manager,
            object_id="good_button"
        )

        # Exit button
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width * 0.35, height * 0.8), (width * 0.3, height * 0.1)),
            text="Exit",
            manager=self.manager,
            object_id="bad_button"
        )

        # Mute button
        self.mute_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 50, height - 50), (40, 40)),
            text="",
            manager=self.manager,
            object_id="neutral_button"
        )
        
        # Set initial icon
        self.update_mute_button_image()


        # Mute music button
        self.mute_music_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 100, height - 50), (40, 40)),
            text="",
            manager=self.manager,
            object_id="neutral_button"
        )

        # Set initial icon for mute music button
        self.update_mute_music_button_image()

        # Reset player data button
        self.reset_player_data_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, height - 50), (width * 0.25, 40)),
            text="Reset Player Data",
            manager=self.manager,
            object_id="bad_button"
        )

    def update_mute_button_image(self):
        # Scale the icon to fit the button
        icon_size = (int(self.mute_button.rect.width * 0.8), int(self.mute_button.rect.height * 0.8))
        current_icon = self.unmute_icon_surface if int(sound_manager.muted) == 0 else self.mute_icon_surface
        scaled_icon = pygame.transform.scale(current_icon, icon_size)
        
        # Set the button's normal and hover images
        self.mute_button.normal_image = scaled_icon
        self.mute_button.hovered_image = scaled_icon
        self.mute_button.selected_image = scaled_icon
        self.mute_button.rebuild()

        try:
            options_path = Path(DATA_FILE)
            data = {}
            if options_path.exists():
                with open(options_path, 'r') as f:
                    data = json.load(f)
            
            data["mute"] = int(sound_manager.muted)
            options_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(options_path, 'w') as f:
                json.dump(data, f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error saving options: {e}")


    def update_mute_music_button_image(self):
        # Scale the icon to fit the button
        icon_size = (int(self.mute_music_button.rect.width * 0.8), int(self.mute_music_button.rect.height * 0.8))
        current_icon = self.mute_music_icon_surface if int(sound_manager.music_muted) == 0 else self.unmute_music_icon_surface
        scaled_icon = pygame.transform.scale(current_icon, icon_size)
        
        
        # Set the button's normal and hover images
        self.mute_music_button.normal_image = scaled_icon
        self.mute_music_button.hovered_image = scaled_icon
        self.mute_music_button.selected_image = scaled_icon
        self.mute_music_button.rebuild()

        try:
            options_path = Path(DATA_FILE)
            data = {}
            if options_path.exists():
                with open(options_path, 'r') as f:
                    data = json.load(f)
            
            data["mute_music"] = int(sound_manager.music_muted)
            options_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(options_path, 'w') as f:
                json.dump(data, f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error saving options: {e}")


    def handle_events(self, event):
        """Handles the events in this scene."""
        match event.type:
            case pygame_gui.UI_BUTTON_PRESSED:
                sound_manager.play("click")
                match event.ui_element:
                    case element if element is self.exit_button:  # Exit the game
                        time.sleep(0.2)
                        self.change_scene(None)
                    case element if element is self.play_button:  # Move to level select and create player data if it doesn't exist
                        player_data_path = os.path.join(PLAYER_FOLDER, f"{self.player_name}.json")
                        if not os.path.exists(player_data_path):
                            with open(player_data_path, 'w') as f:
                                json.dump({"highest_level": 0}, f)
                        self.change_scene("level_select")
                    case element if element is self.name_change_button:  # Toggle name change mode
                        self.toggle_name_change()
                    case element if element is self.mute_button:  # Toggle mute
                        sound_manager.toggle_mute()
                        self.update_mute_button_image()
                    case element if element is self.mute_music_button:  # Toggle music mute
                        sound_manager.toggle_music()
                        self.update_mute_music_button_image()
                    case element if element is self.reset_player_data_button:  # Reset player data
                        self.reset_player_data()
            case pygame.QUIT:
                self.change_scene(None)
            case _:
                pass
    

    def load_player_name(self):
        """Load the last player name from options file"""
        try:
            options_path = Path(DATA_FILE)
            if options_path.exists():
                with open(options_path, 'r') as f:
                    data = json.load(f)
                    return data.get("last_player", "Player")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading options: {e}")
        return "Player"


    def toggle_name_change(self):
        """Toggle between name display and name change mode"""
        self.name_changing = not self.name_changing
        
        if self.name_changing:
            # Entering name change mode
            self.welcome_label.hide()
            self.name_input.show()
            self.name_input.set_text(self.player_name)
            self.name_input.focus()
            self.name_change_button.set_text("Confirm Name")
            self.play_button.disable()
            self.exit_button.disable()
            self.reset_player_data_button.disable()
        else:
            # Exiting name change mode
            new_name = self.name_input.get_text()
            if new_name and new_name != self.player_name:
                # Only update if name changed and not empty
                self.player_name = new_name
                self.save_player_name(self.player_name)
                self.welcome_label.set_text(f"Welcome back, {self.player_name}!")
            
            self.welcome_label.show()
            self.name_input.hide()
            self.name_input.set_text("")  # Clear input field
            self.name_change_button.set_text("This isn't you? Click here")
            self.play_button.enable()
            self.exit_button.enable()
            self.reset_player_data_button.enable()


    def save_player_name(self, name):
        """Save the player name to options file"""
        try:
            options_path = Path(DATA_FILE)
            data = {}
            if options_path.exists():
                with open(options_path, 'r') as f:
                    data = json.load(f)
            
            data["last_player"] = name
            options_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(options_path, 'w') as f:
                json.dump(data, f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error saving options: {e}")


    def reset_player_data(self):
        """Resets player data to default values"""
        try:
            # Look in the player folder for any files named "player_name.json"
            file = f"{self.player_name}.json"
            if os.path.exists(os.path.join(PLAYER_FOLDER, file)):  # Check if the file exists
                os.remove(os.path.join(PLAYER_FOLDER, file))
            # Recreate the default player file. highest_level = 1
            with open(os.path.join(PLAYER_FOLDER, f"{self.player_name}.json"), 'w') as f:
                json.dump({"highest_level": 0}, f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error resetting player data: {e}")


    def update(self, time_delta):
        """
        Updates the UI manager, therefore refreshing the screen.
        """
        self.manager.update(time_delta)


    def render(self):
        """
        Renders the UI elements on the screen.
        """
        self.screen.fill((0, 0, 0))  # Black background
        self.manager.draw_ui(self.screen)


    def resize(self):
        """
        Recreates UI elements on window resize to achieve responsive design.
        """
        self.manager.clear_and_reset()  # Clear UI and recreate
        self.create_ui()


    def destroy(self):
        """
        Destroys the UI manager and its elements.
        """
        logging.debug("Destroying main menu scene")
        self.manager.clear_and_reset()