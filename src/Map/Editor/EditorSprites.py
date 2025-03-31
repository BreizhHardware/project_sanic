import pygame


class EditorPlatform(pygame.sprite.Sprite):
    """Platform object for the level editor"""

    def __init__(self, width, height, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        # Create surface for drawing
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 200, 100))  # Green color for platforms

        # Store original dimensions
        self.width = width
        self.height = height

        # Attributes for moving platforms
        self.moving = False
        self.direction = "horizontal"
        self.speed = 2
        self.distance = 100


class EditorCheckpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 30, 30)
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 255, 0))  # Yellow


class EditorEnemy(pygame.sprite.Sprite):
    def __init__(self, game_resources, x, y, enemy_type="walker"):
        super().__init__()
        self.rect = pygame.Rect(x, y, 30, 30)
        self.image = pygame.Surface((30, 30))
        self.enemy_type = enemy_type
        self.update_appearance()

    def update_appearance(self):
        if self.enemy_type == "walker":
            self.image.fill((255, 0, 0))  # Rouge
        elif self.enemy_type == "flyer":
            self.image.fill((255, 165, 0))  # Orange
        elif self.enemy_type == "turret":
            self.image.fill((128, 0, 128))  # Violet


class EditorExit(pygame.sprite.Sprite):
    def __init__(self, x, y, width=50, height=50, next_level="map/levels/1.json"):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 255))  # Cyan
        self.next_level = next_level
        self.sprite = "assets/map/exit/door.png"


class EditorCollectible(pygame.sprite.Sprite):
    def __init__(self, x, y, collectible_type="coin"):
        super().__init__()
        self.rect = pygame.Rect(x, y, 20, 20)
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 215, 0))  # Gold color for coins
        self.collectible_type = collectible_type
        self.value = 10 if collectible_type == "coin" else 0
        self.duration = 5.0 if collectible_type == "power_up" else 0
