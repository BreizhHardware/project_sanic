import pygame
from pygame.locals import *
import sys
import os
import time

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
pygame.display.set_caption("Project Sanic")

# Initialize font for FPS counter
try:
    font = pygame.font.SysFont("Arial", 24)
except:
    font = pygame.font.Font(None, 24)  # Default font if Arial is not available


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Animation variables
        self.animation_frames = []
        self.current_frame = 0
        self.animation_speed = 0.1
        self.last_update = time.time()
        self.static_image = None
        self.moving = False  # Track if player is moving

        # Load static image and animation frames
        self.load_images()

        # Set initial surface
        if self.static_image:
            self.surf = self.static_image
        elif self.animation_frames:
            self.surf = self.animation_frames[0]
        else:
            # Fallback to a colored rectangle
            self.surf = pygame.Surface((30, 30))
            self.surf.fill((128, 255, 40))

        self.rect = self.surf.get_rect()
        self.pos = vec((10, 385))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False

    def load_images(self):
        try:
            # Load static image
            if os.path.isfile("assets/player/Sanic Base.png"):
                self.static_image = pygame.image.load("assets/player/Sanic Base.png").convert_alpha()
                self.static_image = pygame.transform.scale(self.static_image, (160, 160))

            # Load animation sprite sheet
            if os.path.isfile("assets/player/Sanic Annimate.png"):
                sprite_sheet = pygame.image.load("assets/player/Sanic Annimate.png").convert_alpha()

                # Extract the 4 frames
                frame_width = sprite_sheet.get_height()

                for i in range(4):
                    # Cut out a region of the sprite sheet
                    frame = sprite_sheet.subsurface((i * 2207, 0, frame_width, frame_width))
                    # Resize the frame
                    frame = pygame.transform.scale(frame, (160, 160))
                    self.animation_frames.append(frame)

        except Exception as e:
            print(f"Error loading player images: {e}")

    def update_animation(self):
        if self.moving:
            # Only animate when moving
            if self.animation_frames and time.time() - self.last_update > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.surf = self.animation_frames[self.current_frame]
                self.last_update = time.time()
        else:
            # Use static image when not moving
            if self.static_image:
                self.surf = self.static_image

    def dash(self, acc):
        self.acc.x = 5 * acc

    def move(self):
        self.acc = vec(0, 1)  # Gravity

        # Reset moving flag
        self.moving = False

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_q]:
            self.acc.x = -ACC
            self.moving = True  # Set moving to True when moving left
            if pressed_keys[K_a]:
                self.dash(-ACC)
        if pressed_keys[K_d]:
            self.acc.x = ACC
            self.moving = True  # Set moving to True when moving right
            if pressed_keys[K_a]:
                self.dash(ACC)

        # Also consider the player moving if they have significant horizontal velocity
        if abs(self.vel.x) > 0.5:
            self.moving = True

        # Jumping logic
        if pressed_keys[K_SPACE] and not self.jumping:
            self.vel.y = -30
            self.jumping = True

        # Apply friction
        self.acc.y += self.vel.y * FRIC
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Prevent the player from moving off-screen horizontally
        if self.pos.x > WIDTH - self.rect.width / 2:
            self.pos.x = WIDTH - self.rect.width / 2
            self.vel.x = 0
        if self.pos.x < self.rect.width / 2:
            self.pos.x = self.rect.width / 2
            self.vel.x = 0

        self.rect.midbottom = self.pos

        # Update animation frame
        self.update_animation()

    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            if self.vel.y > 0:
                self.pos.y = hits[0].rect.top
                self.vel.y = 0
                self.jumping = False


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
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

    displaysurface.fill((0, 0, 0))

    P1.move()
    P1.update()
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    # Display FPS
    fps = int(FramePerSec.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    displaysurface.blit(fps_text, (10, 10))

    # Display player coordinates
    pos_text = font.render(f"X: {int(P1.pos.x)}, Y: {int(P1.pos.y)}", True, (255, 255, 255))
    displaysurface.blit(pos_text, (10, 40))

    pygame.display.update()
    FramePerSec.tick(FPS)