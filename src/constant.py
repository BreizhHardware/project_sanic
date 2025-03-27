import pygame

pygame.init()

FPS = 60
ACC = 0.5
FRIC = -0.12
WIDTH = 1200
HEIGHT = 800
platforms = pygame.sprite.Group()
vec = pygame.math.Vector2
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Project Sanic")
FramePerSec = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
fullscreen = False
ORIGINAL_WIDTH = WIDTH
ORIGINAL_HEIGHT = HEIGHT

try:
    font = pygame.font.SysFont("Arial", 20)
except:
    font = pygame.font.Font(None, 20)
