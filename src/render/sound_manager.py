"""Sound manager class"""

import pygame
import logging
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
        sounds (dict): Dictionary to store loaded sound effects.
        music (dict): Dictionary to store music file paths.
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
            self.sfx_channels = []
            self.muted = False
            self.sounds = {}  # For sound effects
            self.music = {}   # For music file paths
            self._initialized = True
            self.max_channels = 16  # Maximum number of sound channels


    def initialize(self):
        """Initialize the sound manager and set up channels."""
        if not pygame.mixer.get_init():
            raise RuntimeError("pygame.mixer not initialized")
        self.music_channel = pygame.mixer.Channel(0)
        self.sfx_channels = []  # Reset the list of sound effect channels
        for i in range(1, self.max_channels + 1):
            channel = pygame.mixer.Channel(i)
            self.sfx_channels.append(channel)


    def load_sound(self, name, path, is_music=False):
        """
        Load a sound file and store it in the sound manager.
        
        Args:
            name (str): The name to associate with the sound.
            path (str): The path to the sound file.
            is_music (bool): Whether the sound is music or not.
        """
        try:
            if is_music:
                # Store music path
                self.music[name] = path
            else:
                # Load sound effect immediately
                self.sounds[name] = pygame.mixer.Sound(path)
        except pygame.error as e:
            logging.error(f"Failed to load sound {name}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error loading sound {name}: {str(e)}")


    def play(self, name, loops=0, volume=1.0):  #FIXME: Sounds playing at the same time will interrupt each other
        """
        Play a sound by name.

        Args:
            name (str): The name of the sound to play.
            loops (int): The number of times to loop the sound.
            volume (float): The volume level (0.0 to 1.0).
        """
        if self.muted:
            return

        if name in self.music:  # It's music
            pygame.mixer.music.load(self.music[name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=loops)
        elif name in self.sounds:  # It's a sound effect
            # Find an available channel
            for channel in self.sfx_channels:
                if not channel.get_busy():
                    channel.set_volume(volume)
                    channel.play(self.sounds[name], loops=loops)
                    break
            else:
                logging.warning(f"No available channel to play sound: {name}")


    def stop_music(self):
        """Stop the music."""
        pygame.mixer.music.stop()


    def stop_all(self):
        """Stop all sounds."""
        pygame.mixer.music.stop()
        for channel in self.sfx_channels:
            channel.stop()


    def stop_sfx(self):
        """Stop all sound effects."""
        for channel in self.sfx_channels:
            channel.stop()


    def toggle_mute(self):
        """Toggle mute on or off."""
        self.muted = not self.muted
        pygame.mixer.music.set_volume(0 if self.muted else 1)
        for channel in self.sfx_channels:
            channel.set_volume(0 if self.muted else 1)


# Global instance
sound_manager = SoundManager()