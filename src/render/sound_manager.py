"""Sound manager class"""

import pygame
from typing import Dict


class SoundManager:
    """
    Singleton class to manage sound effects and music in the game.
    It uses pygame's mixer module to load, play, and stop sounds.
    It also provides functionality to mute and unmute sounds.
    It uses singleton to configure a global sound manager instance.

    Attributes:
        music_channel (pygame.mixer.Channel): The channel for playing music.
        sfx_channel (pygame.mixer.Channel): The channel for playing sound effects.
        muted (bool): Flag to indicate if sounds are muted.
        sounds (dict): Dictionary to store loaded sounds with their names as keys.

    Methods:
        load_sound(name, path, is_music=False): Load a sound file and store it in the sound manager.
        play(name, loops, volume=1.0): Play a sound by name.
        stop_music(): Stop the music channel.
        stop_all(): Stop all sounds.
        toggle_mute(): Toggle mute on or off.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance


    def __init__(self):
        if not self._initialized:
            self.music_channel = None
            self.sfx_channel = None
            self.muted = False
            self.sounds = {}
            self._initialized = True


    def initialize(self):
        """Initialize the sound manager and set up channels."""
        if not pygame.mixer.get_init():
            raise RuntimeError("pygame.mixer not initialized")
        self.music_channel = pygame.mixer.Channel(0)
        self.sfx_channel = pygame.mixer.Channel(1)


    def load_sound(self, name, path, is_music=False):
        """
        Load a sound file and store it in the sound manager.
        
        Args:
            name (str): The name to associate with the sound.
            path (str): The path to the sound file.
            is_music (bool): Whether the sound is music or not.
        """
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].is_music = is_music
        except pygame.error as e:
            error_handler.push_error(
                "Sound Error", 
                f"Failed to load sound {name}: {str(e)}",
                ErrorLevel.WARNING
            )


    def play(self, name, loops, volume=1.0):
        """
        Play a sound by name.

        Args:
            name (str): The name of the sound to play.
            loops (int): The number of times to loop the sound.
            volume (float): The volume level (0.0 to 1.0).
        """
        if self.muted or name not in self.sounds:
            return

        channel = self.music_channel if self.sounds[name].is_music else self.sfx_channel
        channel.set_volume(volume)
        channel.play(self.sounds[name], loops=loops)


    def stop_music(self):
        """Stop the music channel."""
        self.music_channel.stop()


    def stop_all(self):
        """Stop all sounds."""
        self.music_channel.stop()
        self.sfx_channel.stop()


    def toggle_mute(self):
        """Toggle mute on or off."""
        self.muted = not self.muted
        self.music_channel.set_volume(0 if self.muted else 1)
        self.sfx_channel.set_volume(0 if self.muted else 1)

# Global instance
sound_manager = SoundManager()