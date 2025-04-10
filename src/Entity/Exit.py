import pygame
import os
from src.Entity.Entity import Entity
from moviepy import VideoFileClip
import moviepy as mp


class Exit(Entity):
    """
    Class representing a level exit/goal point that triggers level completion when touched.
    Inherits from Entity base class.
    """

    def __init__(self, x, y, width, height, next_level, sprite_path=None):
        """
        Initialize the exit object.

        Args:
            x (int): X-coordinate position
            y (int): Y-coordinate position
            width (int): Width of the exit
            height (int): Height of the exit
            next_level (str): ID or name of the level to load when exiting
            sprite_path (str, optional): Path to the sprite image for the exit
        """
        super().__init__(pos=(x, y), size=(width, height), color=(0, 255, 0))
        self.next_level = next_level  # Store the next level to load
        self.active = True  # Flag to prevent multiple triggers
        self.player = None  # Will store the player reference

        # Load sprite if provided
        if sprite_path:
            try:
                self.image = pygame.image.load(sprite_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
                self.surf = self.image
            except Exception as e:
                print(f"Error loading exit sprite: {e}")

    def set_player(self, player):
        """
        Set the player reference for collision detection.

        Args:
            player: The player entity to check collision with
        """
        self.player = player

    def update(self):
        """
        Check for collision with the player and trigger level completion.
        """
        # Skip collision check if player reference is not set
        if not self.player or not self.active:
            return

        # Check if player is colliding with exit
        if self.rect.colliderect(self.player.rect):
            # Play the video and return to menu
            self.play_video_and_return_to_menu("assets/map/exit/Zeldo Motus.mp4")
            self.active = False  # Prevent multiple triggers

    def play_video_and_return_to_menu(self, video_path):
        """
        Play a video and then return to the menu.

        Args:
            video_path (str): Path to the video file
        """
        clip = VideoFileClip(video_path)
        screen = pygame.display.get_surface()
        screen_size = screen.get_size()
        clip = clip.resized(new_size=screen_size)
        clock = pygame.time.Clock()

        # Extract audio from the video
        audio = mp.AudioFileClip(video_path)
        audio.write_audiofile("temp_audio.mp3")

        # Pause the main music without stopping it
        main_music_pos = (
            pygame.mixer.music.get_pos() / 1000 if pygame.mixer.get_init() else 0
        )
        pygame.mixer.music.pause()

        # Load and play the audio on a separate channel
        temp_sound = pygame.mixer.Sound("temp_audio.mp3")
        sound_channel = temp_sound.play()

        for frame in clip.iter_frames(fps=24, dtype="uint8"):
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            screen.blit(frame_surface, (0, 0))
            pygame.display.flip()
            clock.tick(24)

            # Check if the sound channel is still playing
            if sound_channel and not sound_channel.get_busy():
                break

        clip.close()

        # Play the main music again from the last position
        pygame.mixer.music.unpause()

        # Remove the temporary audio file
        try:
            os.remove("temp_audio.mp3")
        except Exception as e:
            print(f"Error removing temporary audio file: {e}")

        # Return to the menu
        return_event = pygame.event.Event(
            pygame.USEREVENT, {"action": "return_to_menu"}
        )
        pygame.event.post(return_event)
