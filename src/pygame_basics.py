import pygame
import sys
from pygame.locals import *
import time
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
VEC = pygame.math.Vector2
ACC = 0.5
FRIC = -0.12
vec = pygame.math.Vector2

# Setup display
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
FramePerSec = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont("Arial", 20)

# Global variables for access in other modules
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Animation variables
        self.animation_frames = []
        self.jump_frames = []
        self.dash_frames = []
        self.current_frame = 0
        self.animation_speed = 0.1
        self.last_update = time.time()
        self.static_image = None
        self.moving = False
        self.dashing = False

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
                self.static_image = pygame.image.load(
                    "assets/player/Sanic Base.png"
                ).convert_alpha()
                self.static_image = pygame.transform.scale(
                    self.static_image, (120, 120)
                )

            # Load regular animation sprite sheet
            if os.path.isfile("assets/player/Sanic Annimate.png"):
                sprite_sheet = pygame.image.load(
                    "assets/player/Sanic Annimate.png"
                ).convert_alpha()

                # Extract the 4 frames
                frame_width = sprite_sheet.get_height()

                for i in range(4):
                    # Cut out a region of the sprite sheet
                    frame = sprite_sheet.subsurface(
                        (i * 2207, 0, frame_width, frame_width)
                    )
                    # Resize the frame
                    frame = pygame.transform.scale(frame, (120, 120))
                    self.animation_frames.append(frame)

            # Load jump animation sprite sheet
            if os.path.isfile("assets/player/Sanic Boule.png"):
                self.jump_frames.append(
                    pygame.transform.scale(
                        pygame.image.load(
                            "assets/player/Sanic Boule.png"
                        ).convert_alpha(),
                        (120, 120),
                    )
                )

            # Load dash animation sprite sheet
            if os.path.isfile("assets/player/Sanic Boule Annimate.png"):
                dash_sheet = pygame.image.load(
                    "assets/player/Sanic Boule Annimate.png"
                ).convert_alpha()

                # Extract the frames with 2000px gap
                dash_frame_height = dash_sheet.get_height()

                for i in range(4):  # Assuming 4 frames
                    frame = dash_sheet.subsurface(
                        (i * 2000, 0, dash_frame_height, dash_frame_height)
                    )
                    frame = pygame.transform.scale(frame, (120, 120))
                    self.dash_frames.append(frame)

        except Exception as e:
            print(f"Error loading player images: {e}")

    def update_animation(self):
        current_time = time.time()

        # Priority: Dashing > Jumping > Moving > Static
        if self.dashing and self.dash_frames:
            if current_time - self.last_update > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.dash_frames)
                self.surf = self.dash_frames[self.current_frame]
                self.last_update = current_time
        elif self.jumping and self.jump_frames:
            self.surf = self.jump_frames[0]  # Use jump frame
        elif self.moving and self.animation_frames:
            if current_time - self.last_update > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(
                    self.animation_frames
                )
                self.surf = self.animation_frames[self.current_frame]
                self.last_update = current_time
        elif self.static_image:
            self.surf = self.static_image

    def dash(self, acc):
        self.acc.x = 5 * acc
        self.dashing = True  # Set dashing flag

    def move(self):
        self.acc = vec(0, 1)  # Gravity

        # Reset flags
        self.moving = False
        self.dashing = False

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_q]:
            self.acc.x = -ACC
            self.moving = True
            if pressed_keys[K_a]:
                self.dash(-ACC)
        if pressed_keys[K_d]:
            self.acc.x = ACC
            self.moving = True
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


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))


def initialize_game():
    global platforms, all_sprites

    # Clear previous sprites if any
    platforms.empty()
    all_sprites.empty()

    # Create new game objects
    PT1 = Platform()
    P1 = Player()

    # Add them to the groups
    platforms.add(PT1)
    all_sprites.add(PT1)
    all_sprites.add(P1)

    return P1, PT1, platforms, all_sprites


def run_game(P1, all_sprites):
    """Run the main game loop without menu system"""
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
        pos_text = font.render(
            f"X: {int(P1.pos.x)}, Y: {int(P1.pos.y)}", True, (255, 255, 255)
        )
        displaysurface.blit(pos_text, (10, 40))

        pygame.display.update()
        FramePerSec.tick(FPS)


if __name__ == "__main__":
    P1, PT1, platforms, all_sprites = initialize_game()
    run_game(P1, all_sprites)
