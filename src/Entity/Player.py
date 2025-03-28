from src.Entity.Entity import Entity
from pygame import *
import pygame
import os


class Player(Entity):
    def __init__(self, game_resources, width=100, height=100, x=10, y=385):
        super().__init__(pos=(x, y), size=(width, height), color=(128, 255, 40))

        # Game ressources
        self.game_resources = game_resources

        # Animation variables
        self.animation_frames = []
        self.jump_frames = []
        self.dash_frames = []
        self.current_frame = 0
        self.animation_speed = 0.1
        self.last_update = pygame.time.get_ticks()
        self.static_image = None
        self.moving = False
        self.dashing = False
        self.jumping = False

        # Dash mechanics
        self.last_dash_time = 0
        self.dash_start_time = 0
        self.dash_duration = 500  # 1/2 second activation time
        self.dash_cooldown = 3000  # 3 seconds cooldown

        # Life system
        self.max_lives = 2
        self.lives = 2
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.5
        self.life_icon = None

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
                    self.static_image, (100, 100)
                )

            # Load regular animation sprite sheet
            if os.path.isfile("assets/player/Sanic Annimate.png"):
                sprite_sheet = pygame.image.load(
                    "assets/player/Sanic Annimate.png"
                ).convert_alpha()

                # Extract the 4 frames
                frame_height = sprite_sheet.get_height()
                frame_width = sprite_sheet.get_width() // 4

                for i in range(4):
                    # Cut out a region of the sprite sheet
                    frame = sprite_sheet.subsurface(
                        (i * 2290, 0, frame_width, frame_height)
                    )
                    # Resize the frame
                    frame = pygame.transform.scale(frame, (100, 100))
                    self.animation_frames.append(frame)

            # Load jump animation sprite sheet
            if os.path.isfile("assets/player/Sanic Boule.png"):
                self.jump_frames.append(
                    pygame.transform.scale(
                        pygame.image.load(
                            "assets/player/Sanic Boule.png"
                        ).convert_alpha(),
                        (80, 80),
                    )
                )

            # Load dash animation sprite sheet
            if os.path.isfile("assets/player/Sanic Boule Annimate.png"):
                dash_sheet = pygame.image.load(
                    "assets/player/Sanic Boule Annimate.png"
                ).convert_alpha()

                dash_frame_height = dash_sheet.get_height()

                for i in range(4):
                    frame = dash_sheet.subsurface(
                        (i * 2000, 0, dash_frame_height, dash_frame_height)
                    )
                    frame = pygame.transform.scale(frame, (80, 80))
                    self.dash_frames.append(frame)

            # Load life icon
            if os.path.isfile("assets/player/Sanic Head.png"):
                self.life_icon = pygame.image.load(
                    "assets/player/Sanic Head.png"
                ).convert_alpha()
                self.life_icon = pygame.transform.scale(
                    self.life_icon,
                    (
                        self.game_resources.life_icon_width,
                        self.game_resources.life_icon_width,
                    ),
                )
            else:
                # Backup: use a red square
                self.life_icon = pygame.Surface(
                    (
                        self.game_resources.life_icon_width,
                        self.game_resources.life_icon_width,
                    )
                )
                self.life_icon.fill((255, 0, 0))

        except Exception as e:
            print(f"Error loading player images: {e}")

    def update_animation(self):
        current_time = pygame.time.get_ticks()

        # Priority: Dashing > Jumping > Moving > Static
        if self.dashing and self.dash_frames:
            if current_time - self.last_update > self.animation_speed * 1000:
                self.current_frame = (self.current_frame + 1) % len(self.dash_frames)
                self.surf = self.dash_frames[self.current_frame]
                self.last_update = current_time
        elif self.jumping and self.jump_frames:
            self.surf = self.jump_frames[0]  # Use jump frame
        elif self.moving and self.animation_frames:
            if current_time - self.last_update > self.animation_speed * 1000:
                self.current_frame = (self.current_frame + 1) % len(
                    self.animation_frames
                )
                self.surf = self.animation_frames[self.current_frame]
                self.last_update = current_time
        elif self.static_image:
            self.surf = self.static_image

    def dash(self, acc):
        current_time = pygame.time.get_ticks()

        # Check if dash is available (3 seconds since last dash)
        if current_time - self.last_dash_time >= self.dash_cooldown:
            # Start the dash
            self.vel.x = 75 * acc  # Apply velocity instead of acceleration
            self.dashing = True  # Set dashing flag
            self.dash_start_time = current_time
            self.last_dash_time = current_time

    def move(self):
        current_time = pygame.time.get_ticks()

        # End dash after 0.5 seconds
        if self.dashing and current_time - self.dash_start_time >= self.dash_duration:
            self.dashing = False

        self.acc = self.game_resources.vec(0, 1)

        # Reset flags
        self.moving = False

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_q]:
            # Check if X is > 0 to prevent player from going off screen
            if self.pos.x > 0:
                self.acc.x = -self.game_resources.ACC
                self.moving = True
                if pressed_keys[K_a]:
                    self.dash(-self.game_resources.ACC)
        if pressed_keys[K_d]:
            self.acc.x = self.game_resources.ACC
            self.moving = True
            if pressed_keys[K_a]:
                self.dash(self.game_resources.ACC)

        # Also consider the player moving if they have significant horizontal velocity
        if abs(self.vel.x) > 0.5:
            self.moving = True

        # Jumping logic
        if pressed_keys[K_SPACE] and not self.jumping:
            self.vel.y = -30
            self.jumping = True

        # Apply friction
        self.acc.y += self.vel.y * self.game_resources.FRIC
        self.acc.x += self.vel.x * self.game_resources.FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        self.rect.midbottom = self.pos

        # Update animation frame
        self.update_animation()

    def draw_dash_cooldown_bar(self, surface):
        """Draws a cooldown bar next to the FPS display."""
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_dash_time

        # Calculate progress (0 to 1)
        cooldown_progress = min(elapsed_time / self.dash_cooldown, 1)

        # Bar settings
        bar_width, bar_height = 75, 8
        x, y = 560, 330

        # Background (empty bar)
        pygame.draw.rect(surface, (100, 100, 100), (x, y, bar_width, bar_height))

        # Filled portion (based on cooldown progress)
        pygame.draw.rect(
            surface, (58, 83, 200), (x, y, bar_width * cooldown_progress, bar_height)
        )

    def update(self):
        hits = pygame.sprite.spritecollide(self, self.game_resources.platforms, False)
        if hits:
            if self.vel.y > 0:
                self.pos.y = hits[0].rect.top
                self.vel.y = 0
                self.jumping = False

        if self.invulnerable:
            self.invulnerable_timer += 1 / self.game_resources.FPS
            if self.invulnerable_timer >= self.invulnerable_duration:
                self.invulnerable = False
                self.invulnerable_timer = 0

    def take_damage(self, amount=1):
        """Reduce life number if not invulnerable"""
        if not self.invulnerable:
            self.lives -= amount

            if self.lives <= 0:
                self.death()
            else:
                # Période d'invulnérabilité temporaire
                self.invulnerable = True
                self.invulnerable_timer = 0

    def death(self):
        """Display menu to the player"""
        death_event = pygame.event.Event(pygame.USEREVENT, {"action": "player_death"})
        pygame.event.post(death_event)
        print("Player died! Returning to menu...")

    def draw_lives(self, surface):
        """Draws the player's remaining lives as icons in the top right corner."""
        spacing = 5
        start_x = surface.get_width() - (
            self.max_lives * (self.game_resources.life_icon_width + spacing)
        )
        start_y = 10

        for i in range(self.max_lives):
            if i < self.lives:
                # Vie active: afficher l'icône normale
                surface.blit(
                    self.life_icon,
                    (
                        start_x + i * (self.game_resources.life_icon_width + spacing),
                        start_y,
                    ),
                )
            else:
                # Vie perdue: afficher l'icône grisée
                grayscale_icon = self.life_icon.copy()
                # Appliquer un filtre gris
                for x in range(grayscale_icon.get_width()):
                    for y in range(grayscale_icon.get_height()):
                        color = grayscale_icon.get_at((x, y))
                        gray = (color[0] + color[1] + color[2]) // 3
                        grayscale_icon.set_at((x, y), (gray, gray, gray, color[3]))
                surface.blit(
                    grayscale_icon,
                    (
                        start_x + i * (self.game_resources.life_icon_width + spacing),
                        start_y,
                    ),
                )
