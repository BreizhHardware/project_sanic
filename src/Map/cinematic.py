import pygame
from PIL import Image, ImageSequence


class Cinematic:
    """Class to handle cinematics in the game"""

    # Class variable to track if level 1 cinematic has been played (shared across all instances)
    has_played_level1 = False

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

    def play_cinematic(self, game_resources):
        """Play the cinematic for level 1"""
        if Cinematic.has_played_level1:
            return

        screen = game_resources.displaysurface
        font = pygame.font.Font(None, 36)
        lore_text = [
            "Once upon a time in a land far away...",
            "A brave hero named Sanic...",
            "And a beautiful princess named Zeldo...",
            "Has been captured by the evil boss...",
            "Wheatly !!!",
            "Sanic must rescue Zeldo...",
        ]

        # Initialize the mixer
        pygame.mixer.init()
        cinematic_voice = pygame.mixer.Sound("assets/sound/cinematic_voice.mp3")

        screen.fill((0, 0, 0))
        for i, line in enumerate(lore_text):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return  # Skip the cinematic if any key is pressed

            # Play the voice audio
            cinematic_voice.play()

            if "Sanic" in line:
                screen.blit(self.player_image, (100, 400))
            if "Zeldo" in line:
                screen.blit(self.princess_image, (700, 400))
            if "Wheatly" in line:
                for _ in range(46):
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            return  # Skip the cinematic if any key is pressed

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
            Cinematic.has_played_level1 = True
