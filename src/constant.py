import pygame


class GameResources:
    def __init__(self):
        pygame.init()

        # Constantes
        self.FPS = 60
        self.ACC = 0.5
        self.FRIC = -0.12
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.ORIGINAL_WIDTH = self.WIDTH
        self.ORIGINAL_HEIGHT = self.HEIGHT
        self.life_icon_width = 50
        self.fullscreen = False

        try:
            icon = pygame.image.load("assets/player/Sanic Head.png")
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Error loading icons: {e}")

        # Ressources
        self.platforms = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.exits = pygame.sprite.Group()
        self.vec = pygame.math.Vector2
        self.displaysurface = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT), pygame.RESIZABLE, vsync=1
        )
        pygame.display.set_caption("Project Sanic")
        self.FramePerSec = pygame.time.Clock()

        self.infinite_manager = None
        self.infinite_mode = False

        # Font
        try:
            self.font = pygame.font.SysFont("Arial", 20)
        except:
            self.font = pygame.font.Font(None, 20)
