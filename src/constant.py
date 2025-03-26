import pygame

pygame.init()

FPS = 60
ACC = 0.5
FRIC = -0.12
WIDTH = 800
HEIGHT = 600
platforms = pygame.sprite.Group()
vec = pygame.math.Vector2
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
FramePerSec = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

try:
    font = pygame.font.SysFont("Arial", 20)
except:
    font = pygame.font.Font(None, 20)
