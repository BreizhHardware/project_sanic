import pygame
from pygame.locals import *
import sys

pygame.init()

vec = pygame.math.Vector2
HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60
FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = displaysurface.get_size()
pygame.display.set_caption("Game")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 30))
        self.surf.fill((128, 255, 40))
        self.rect = self.surf.get_rect()

        self.pos = vec((10, 385))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False  # Track if the player is in the air

    def dash(self, acc):
        self.acc.x = 5*acc

    def move(self):
        self.acc = vec(0, 1)  # Gravity

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_q]:
            self.acc.x = -ACC
            if pressed_keys[K_a]:
                self.dash(-ACC)
        if pressed_keys[K_d]:
            self.acc.x = ACC
            if pressed_keys[K_a]:
                self.dash(ACC)

        # Jumping logic: only jump if not already in the air
        if pressed_keys[K_SPACE] and not self.jumping:
            self.vel.y = -30  # Jump force
            self.jumping = True  # Prevent mid-air jumping


            self.vel.x = -ACC
        # Apply friction
        self.acc.y += self.vel.y * FRIC
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Prevent the player from moving off-screen horizontally
        if self.pos.x > WIDTH - self.rect.width / 2:
            self.pos.x = WIDTH - self.rect.width / 2
            self.vel.x = 0  # Stop movement
        if self.pos.x < self.rect.width / 2:
            self.pos.x = self.rect.width / 2
            self.vel.x = 0  # Stop movement

        self.rect.midbottom = self.pos

    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            if self.vel.y > 0:  # Only reset jumping if falling onto a platform
                self.pos.y = hits[0].rect.top
                self.vel.y = 0
                self.jumping = False  # Reset jumping state



class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))


PT1 = platform()
P1 = Player()
platforms = pygame.sprite.Group()
platforms.add(PT1)
all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    displaysurface.fill((0, 0, 0))

    P1.move()
    P1.update()
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    pygame.display.update()
    FramePerSec.tick(FPS)