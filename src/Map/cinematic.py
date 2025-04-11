import pygame
from PIL import Image, ImageSequence


class Cinematic:
    """Class to handle cinematics in the game"""

    # Class variable to track if cinematics have been played (shared across all instances)
    played_cinematics = {"Level 1": False, "Level 2": False, "Level 3": False}

    def __init__(self):
        """Initialize cinematic resources"""
        # Load resources
        self.player_image = pygame.image.load(
            "assets/player/Sanic Base.png"
        ).convert_alpha()
        self.princess_image = pygame.image.load(
            "assets/map/exit/Zeldo.png"
        ).convert_alpha()

        # Prepare the boss GIF
        self.boss_gif = Image.open("assets/map/enemy/boss.gif")
        self.boss_frames = [
            frame.copy() for frame in ImageSequence.Iterator(self.boss_gif)
        ]
        self.boss_frame_index = 0

        self.player_image = pygame.transform.scale(self.player_image, (200, 200))
        self.princess_image = pygame.transform.scale(self.princess_image, (200, 200))

    def _create_gradient_background(
        self, screen, start_color=(0, 0, 128), end_color=(0, 0, 0)
    ):
        """Create a gradient background for the cinematic"""
        width, height = screen.get_size()
        background = pygame.Surface((width, height))

        for y in range(height):
            ratio = y / height

            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)

            pygame.draw.line(background, (r, g, b), (0, y), (width, y))

        return background

    def _display_cinematic_text(self, screen, lore_text, level_name):
        """Helper function to display cinematic text with animations"""
        font = pygame.font.Font(None, 36)
        pygame.mixer.init()
        cinematic_voice = pygame.mixer.Sound("assets/sound/cinematic_voice.mp3")

        gradient_bg = self._create_gradient_background(screen)
        screen.blit(gradient_bg, (0, 0))

        for i, line in enumerate(lore_text):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return False  # Skip the cinematic if any key is pressed

            # Play the voice audio
            cinematic_voice.play()

            # Display character images based on text content
            if "Sanic" in line:
                screen.blit(self.player_image, (100, 400))
            if "Zeldo" in line:
                screen.blit(self.princess_image, (700, 400))
            if "Wheatly" in line or "Wheatley" in line:
                for _ in range(46):
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            return False  # Skip the cinematic if any key is pressed

                    boss_frame = self.boss_frames[self.boss_frame_index]
                    boss_frame = boss_frame.convert("RGBA")
                    boss_frame = pygame.image.fromstring(
                        boss_frame.tobytes(), boss_frame.size, boss_frame.mode
                    )
                    boss_frame = pygame.transform.scale(boss_frame, (200, 200))
                    screen.blit(boss_frame, (400, 400))
                    pygame.display.flip()
                    pygame.time.wait(100)
                    self.boss_frame_index = (self.boss_frame_index + 1) % len(
                        self.boss_frames
                    )

            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (50, 50 + i * 40))
            pygame.display.flip()
            pygame.time.wait(2000)
            cinematic_voice.stop()

        # Mark this cinematic as played
        Cinematic.played_cinematics[level_name] = True
        return True

    def play_cinematic(self, game_resources, level_name):
        """Play the cinematic for levels"""
        # Check if this cinematic has already been played
        if Cinematic.played_cinematics.get(level_name, False):
            return

        screen = game_resources.displaysurface

        if level_name == "Level 1":
            lore_text = [
                "Once upon a time in a land far away...",
                "A brave hero named Sanic...",
                "And a beautiful princess named Zeldo...",
                "Has been captured by the evil boss...",
                "Wheatly !!!",
                "Sanic must rescue Zeldo...",
            ]
            self._display_cinematic_text(screen, lore_text, level_name)

        elif level_name == "Level 2":
            lore_text = [
                "When Sanic arrives at Zeldo's position...",
                "He realizes that it's a trap...",
                "Zeldo is actually a fake...",
                "And the real Zeldo is in another castle...",
            ]
            self._display_cinematic_text(screen, lore_text, level_name)

        elif level_name == "Level 3":
            lore_text = [
                "Sanic must face the evil boss Wheatley...",
                "To rescue the real princess Zeldo...",
                "Will Sanic succeed?",
            ]
            self._display_cinematic_text(screen, lore_text, level_name)
        else:
            pass
