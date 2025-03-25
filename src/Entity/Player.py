from src.Entity.Entity import Entity
from src.constant import WIDTH, vec, ACC, FRIC, platforms
from pygame import *
import pygame
import os
import time


class Player(Entity):
    def __init__(self, width=120, height=120, x=10, y=385):
        super().__init__(pos=(x, y), size=(width, height), color=(128, 255, 40))

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
        self.jumping = False

        # Load images
        self.load_images()

        # Override initial surface if images are loaded
        if self.static_image:
            self.surf = self.static_image
        elif self.animation_frames:
            self.surf = self.animation_frames[0]

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
