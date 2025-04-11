from src.Entity.Entity import Entity
from pygame import *
import pygame
import os
from PIL import Image, ImageSequence
from pygame.math import Vector2 as vec

from src.Entity.FloatingText import FloatingText
from src.Entity.Projectile import Projectile


class Player(Entity):
    def __init__(self, game_resources, width=100, height=100, x=10, y=385):
        super().__init__(pos=(x, y), size=(width, height), color=(128, 255, 40))

        # Game ressources
        self.game_resources = game_resources

        self.has_joystick = False
        self.joystick = None

        self.jump_button = 0
        self.dash_button = 1
        self.attack_button = 2
        self.menu_button = 3

        try:
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.has_joystick = True
        except pygame.error:
            self.has_joystick = False

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
        self.highest_position = self.pos.y

        # Dash mechanics
        self.last_dash_time = 0
        self.dash_start_time = 0
        self.dash_duration = 500  # 1/2 second activation time
        self.dash_cooldown = 3000  # 3 seconds cooldown
        self.speed_boost_active = False
        self.active_speed_boost = None

        # Jump mechanics
        self.jump_power = 30
        self.jump_boost_active = False
        self.active_jump_boost = None

        # Life system
        self.max_lives = 5
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.5
        self.life_icon = None

        self.rect = self.surf.get_rect()
        self.floating_texts = []

        # Load images
        self.load_images()

        # Coins amount
        self.coins = 0
        # Projectiles amount
        self.projectiles = 0

        # Override initial surface if images are loaded
        if self.static_image:
            self.surf = self.static_image
        elif self.animation_frames:
            self.surf = self.animation_frames[0]

        # Attacking
        self.last_attack_time = 0
        self.attack_start_time = 0
        self.attack_cooldown = 2000

        self.facing_right = True

        # Initilize mixer
        pygame.mixer.init()

    def load_images(self):
        """Load images for the player"""
        try:
            # Load the 7 frames of the GIF
            if os.path.isfile("assets/player/Sanic.gif"):
                self.load_gif_frames("assets/player/Sanic.gif")
                self.animation_speed = 0.05
            else:
                # Fallback to static image if GIF is not found
                self.load_static_and_sprite_sheets()

            # Load special animations (jump, dash, ...)
            self.load_special_animations()

        except Exception as e:
            print(f"Error loading player images: {e}")

    def load_gif_frames(self, gif_path):
        """Load frames from a GIF file"""
        try:
            gif = Image.open(gif_path)

            self.animation_frames = []

            for frame in ImageSequence.Iterator(gif):
                # Convert the frame to a format compatible with Pygame
                frame_rgb = frame.convert("RGBA")
                raw_str = frame_rgb.tobytes("raw", "RGBA")

                pygame_surface = pygame.image.fromstring(
                    raw_str, frame_rgb.size, "RGBA"
                )

                pygame_surface = pygame.transform.scale(pygame_surface, (125, 125))

                self.animation_frames.append(pygame_surface)

            # Use the first frame as the static image
            if self.animation_frames:
                self.static_image = self.animation_frames[0]

        except Exception as e:
            print(f"Error while loading the GIF: {e}")

    def load_static_and_sprite_sheets(self):
        """Previous method to load static image and sprite sheets"""
        # Load static image
        if os.path.isfile("assets/player/Sanic Base.png"):
            self.static_image = pygame.image.load(
                "assets/player/Sanic Base.png"
            ).convert_alpha()
            self.static_image = pygame.transform.scale(self.static_image, (100, 100))

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

    def load_special_animations(self):
        """Load special animations for jump and dash"""
        # Load jump animation sprite sheet
        if os.path.isfile("assets/player/Sanic Boule.png"):
            self.jump_frames.append(
                pygame.transform.scale(
                    pygame.image.load("assets/player/Sanic Boule.png").convert_alpha(),
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

    def update_animation(self):
        current_time = pygame.time.get_ticks()

        current_image = None

        # Priority: Dashing > Jumping > Moving > Static
        if self.dashing and self.dash_frames and len(self.dash_frames) > 0:
            if current_time - self.last_update > self.animation_speed * 1000:
                self.current_frame = (self.current_frame + 1) % len(self.dash_frames)
                self.last_update = current_time

            if 0 <= self.current_frame < len(self.dash_frames):
                current_image = self.dash_frames[self.current_frame]

        elif self.jumping and self.jump_frames and len(self.jump_frames) > 0:
            if 0 < len(self.jump_frames):
                current_image = self.jump_frames[0]

        elif self.moving and self.animation_frames and len(self.animation_frames) > 0:
            if current_time - self.last_update > self.animation_speed * 1000:
                self.current_frame = (self.current_frame + 1) % len(
                    self.animation_frames
                )
                self.last_update = current_time

            if 0 <= self.current_frame < len(self.animation_frames):
                current_image = self.animation_frames[self.current_frame]

        elif self.static_image:
            current_image = self.static_image

        # If no animation is found, use the static imagef available
        if not current_image:
            if self.static_image:
                current_image = self.static_image
            else:
                return

        # Appliquer le retournement selon la direction
        if not self.facing_right:
            self.surf = pygame.transform.flip(current_image, True, False)
        else:
            self.surf = current_image

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

        # Keyboard controls
        pressed_keys = pygame.key.get_pressed()
        move_left = pressed_keys[K_q]
        move_right = pressed_keys[K_d]
        jump = pressed_keys[K_SPACE]
        dash_key = pressed_keys[K_a]

        if self.has_joystick and self.joystick:
            try:
                # Left joystick for movement
                if self.joystick.get_numaxes() > 0:
                    joystick_x = self.joystick.get_axis(0)
                    if abs(joystick_x) > 0.2:
                        if joystick_x < 0:
                            move_left = True
                        elif joystick_x > 0:
                            move_right = True

                # Button for jumping and dashing
                if self.joystick.get_numbuttons() > self.jump_button:
                    if self.joystick.get_button(self.jump_button):
                        jump = True

                if self.joystick.get_numbuttons() > self.dash_button:
                    if self.joystick.get_button(self.dash_button):
                        dash_key = True
            except pygame.error:
                pass

        if move_left:
            # Check if X is > 0 to prevent player from going off screen
            if self.pos.x > 0:
                self.acc.x = -self.game_resources.ACC
                self.moving = True
                if dash_key:
                    self.dash(-self.game_resources.ACC)
        if move_right:
            self.acc.x = self.game_resources.ACC
            self.moving = True
            if dash_key:
                self.dash(self.game_resources.ACC)

        # Also consider the player moving if they have significant horizontal velocity
        if abs(self.vel.x) > 0.5:
            self.moving = True

        # Jumping logic
        if jump and not self.jumping:
            try:
                jump_sound = pygame.mixer.Sound("assets/sound/Jump.mp3")
                jump_sound.play()
            except Exception as e:
                print(f"Error playing jump sound: {e}")
            self.vel.y = -self.jump_power
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
        """Update the player position and check for collisions."""
        # Define the feet and side rectangles for collision detection
        feet_rect = pygame.Rect(0, 0, self.rect.width * 0.8, 10)
        feet_rect.midbottom = self.rect.midbottom

        left_side_rect = pygame.Rect(0, 0, 10, self.rect.height * 0.7)
        left_side_rect.midleft = self.rect.midleft

        right_side_rect = pygame.Rect(0, 0, 10, self.rect.height * 0.7)
        right_side_rect.midright = self.rect.midright

        hits = []
        # Check for collisions with the top of platforms
        for platform in self.game_resources.platforms:
            platform_top_rect = pygame.Rect(
                platform.rect.x, platform.rect.y, platform.rect.width, 5
            )
            if feet_rect.colliderect(platform_top_rect):
                hits.append(platform)

        if hits:
            if self.vel.y > 0:
                self.pos.y = hits[0].rect.top
                self.vel.y = 0
                self.jumping = False
                self.highest_position = self.pos.y

        side_hits = []
        for platform in self.game_resources.platforms:
            # Check for collisions with the left and right sides of the player
            platform_left_rect = pygame.Rect(
                platform.rect.x, platform.rect.y + 5, 5, platform.rect.height - 5
            )
            platform_right_rect = pygame.Rect(
                platform.rect.right - 5,
                platform.rect.y + 5,
                5,
                platform.rect.height - 5,
            )

            if right_side_rect.colliderect(platform_left_rect):
                side_hits.append(("right", platform))
            if left_side_rect.colliderect(platform_right_rect):
                side_hits.append(("left", platform))

        for side, platform in side_hits:
            if side == "right" and self.vel.x > 0:
                self.pos.x = platform.rect.left - self.rect.width / 2
                self.vel.x = 0
            elif side == "left" and self.vel.x < 0:
                self.pos.x = platform.rect.right + self.rect.width / 2
                self.vel.x = 0

        if self.invulnerable:
            self.invulnerable_timer += 1 / self.game_resources.FPS
            if self.invulnerable_timer >= self.invulnerable_duration:
                self.invulnerable = False
                self.invulnerable_timer = 0

        if self.vel.y <= 0:
            self.highest_position = self.pos.y

        if self.vel.y > 0:
            fall_distance = self.pos.y - self.highest_position
            if fall_distance > 500:
                self.death()

        if self.vel.x > 0:
            self.facing_right = True
        elif self.vel.x < 0:
            self.facing_right = False

        self.floating_texts = [text for text in self.floating_texts if text.update()]

    def take_damage(self, amount=1):
        """Reduce life number if not invulnerable"""
        if not self.invulnerable:
            self.lives -= amount

            if self.lives <= 0:
                self.death()
            else:
                # Temporarily make the player invulnerable
                self.invulnerable = True
                self.invulnerable_timer = 0

    def death(self):
        """Display menu to the player"""
        death_event = pygame.event.Event(pygame.USEREVENT, {"action": "player_death"})
        pygame.event.post(death_event)

    def draw_lives(self, surface):
        """Draws the player's remaining lives as icons in the top right corner."""
        spacing = 5
        start_x = surface.get_width() - (
            self.max_lives * (self.game_resources.life_icon_width + spacing)
        )
        start_y = 10

        for i in range(self.max_lives):
            if i < self.lives:
                # Active life: display the icon
                surface.blit(
                    self.life_icon,
                    (
                        start_x + i * (self.game_resources.life_icon_width + spacing),
                        start_y,
                    ),
                )
            else:
                # Life lost: display a grayscale version of the icon
                grayscale_icon = self.life_icon.copy()
                # Apply grayscale effect
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

    def draw_coins(self, surface):
        """Draws the coin counter with icon in the top left corner"""
        # Load coin texture (do this in __init__ for better performance)
        coin_texture = pygame.image.load(
            "assets/map/collectibles/Sanic_Coin.png"
        ).convert_alpha()
        coin_size = 30
        coin_texture = pygame.transform.scale(coin_texture, (coin_size, coin_size))

        # Position for coin display
        start_x = 200
        start_y = 10

        # Draw coin icon
        surface.blit(coin_texture, (start_x, start_y))

        # Use custom font
        try:
            font = pygame.font.Font("assets/fonts/sanicfont.ttf", 20)
        except:
            # Fallback to default font if custom font fails to load
            font = pygame.font.Font(None, 20)

        coin_text = font.render(f"x{self.coins}", True, (58, 83, 200))

        # Position text next to coin icon with small spacing
        text_x = start_x + coin_size + 5
        text_y = start_y + (coin_size - coin_text.get_height()) // 2

        surface.blit(coin_text, (text_x, text_y))

    def collect_coin(self, surface, speedrun_timer=None):
        """Increment coin counter when collecting a coin"""
        coin_sound = pygame.mixer.Sound("assets/sound/Coin.mp3")
        coin_sound.play()
        self.coins += 1
        if self.lives < self.max_lives:
            self.lives += 1
            self.draw_lives(surface)
        if speedrun_timer:
            speedrun_timer.collected_items += 1

    def attack(self):
        """Do an attack action on the player"""

        self.is_attacking = False
        current_time = pygame.time.get_ticks()
        pressed_keys = pygame.key.get_pressed()

        joystick_attack = False
        if self.has_joystick and self.joystick:
            try:
                if self.joystick.get_numbuttons() > self.attack_button:
                    joystick_attack = self.joystick.get_button(self.attack_button)
            except pygame.error:
                pass

        if (
            joystick_attack
            and current_time - self.last_attack_time >= self.attack_cooldown
            and self.projectiles > 0
        ):
            attack_sound = pygame.mixer.Sound("assets/sound/Boule de feu.mp3")
            attack_sound.set_volume(0.4)
            attack_sound.play()
            self.is_attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time

            # Direction en fonction de où le personnage est tourné
            if self.facing_right:
                direction = vec(self.pos.x, 0)
                position = vec(self.pos.x + 50, self.pos.y - 50)
            else:
                direction = vec(-self.pos.x, 0)
                position = vec(self.pos.x - 50, self.pos.y - 50)

            projectile = Projectile(
                pos=position,
                direction=direction,
                speed=2,
                damage=1,
                color=(165, 42, 42),
                enemy_proj=False,
                texturePath="assets/player/Boule de feu.png",
                size=(50, 50),
            )

            # Ajouter le projectile au groupe de sprites
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {"action": "create_projectile", "projectile": projectile},
                )
            )

            self.projectiles -= 1

        if (
            pressed_keys[K_q]
            and pressed_keys[K_c]
            and current_time - self.last_attack_time >= self.attack_cooldown
        ):
            self.is_attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time
            # Calculate direction to player
            direction = vec(self.pos.x, self.pos.y)
            projectile = Projectile(
                pos=vec(self.pos.x, self.pos.y),
                direction=direction,
                speed=2,
                damage=1,
                color=(165, 42, 42),
                enemy_proj=False,
                size=(50, 50),
            )
            # Add projectile to the sprite group (to be placed in main.py)
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {"action": "create_projectile", "projectile": projectile},
                )
            )

        if (
            pressed_keys[K_d]
            and pressed_keys[K_c]
            and current_time - self.last_attack_time >= self.attack_cooldown
        ):
            self.is_attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time
            # Calculate direction to player
            direction = vec(self.pos.x, self.pos.y)
            projectile = Projectile(
                pos=vec(self.pos.x, self.pos.y),
                direction=direction,
                speed=2,
                damage=1,
                color=(165, 42, 42),
                enemy_proj=False,
                size=(50, 50),
            )
            # Add projectile to the sprite group (to be placed in main.py)
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {"action": "create_projectile", "projectile": projectile},
                )
            )

        if (
            pressed_keys[K_q]
            and pressed_keys[K_v]
            and current_time - self.last_attack_time >= self.attack_cooldown
            and self.projectiles > 0
        ):
            attack_sound = pygame.mixer.Sound("assets/sound/Boule de feu.mp3")
            attack_sound.set_volume(0.4)
            attack_sound.play()
            self.is_attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time
            # Calculate direction to player
            direction = vec(-self.pos.x, 0)
            projectile = Projectile(
                pos=vec(self.pos.x - 50, self.pos.y - 50),
                direction=direction,
                speed=2,
                damage=1,
                color=(165, 42, 42),
                enemy_proj=False,
                texturePath="assets/player/Boule de feu.png",
                size=(50, 50),
            )
            # Add projectile to the sprite group (to be placed in main.py)
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {"action": "create_projectile", "projectile": projectile},
                )
            )
            self.projectiles -= 1

        if (
            pressed_keys[K_d]
            and pressed_keys[K_v]
            and current_time - self.last_attack_time >= self.attack_cooldown
            and self.projectiles > 0
        ):
            attack_sound = pygame.mixer.Sound("assets/sound/Boule de feu.mp3")
            attack_sound.set_volume(0.4)
            attack_sound.play()
            self.is_attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time
            # Calculate direction to player
            direction = vec(self.pos.x, 0)
            projectile = Projectile(
                pos=vec(self.pos.x + 50, self.pos.y - 50),
                direction=direction,
                speed=2,
                damage=1,
                color=(165, 42, 42),
                enemy_proj=False,
                texturePath="assets/player/Boule de feu.png",
                size=(50, 50),
            )
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {"action": "create_projectile", "projectile": projectile},
                )
            )
            self.projectiles -= 1

    def add_projectiles(self):
        """Set player projectiles to 3 and show floating text"""
        self.projectiles = 3
        self.floating_texts.append(
            FloatingText("+3 fireball", self, self.game_resources)
        )

    def draw_projectiles_amount(self, surface):
        """Draws the projectiles counter with icon in the top left corner"""
        # Load coin texture (do this in __init__ for better performance)
        projectiles_texture = pygame.image.load(
            "assets/player/Boule de feu.png"
        ).convert_alpha()
        projectile_size = 30
        projectiles_texture = pygame.transform.scale(
            projectiles_texture, (projectile_size, projectile_size)
        )

        # Position for coin display
        start_x = 300
        start_y = 10

        # Draw coin icon
        surface.blit(projectiles_texture, (start_x, start_y))

        # Use custom font
        try:
            font = pygame.font.Font("assets/fonts/sanicfont.ttf", 20)
        except:
            # Fallback to default font if custom font fails to load
            font = pygame.font.Font(None, 20)

        projectiles_text = font.render(f"x{self.projectiles}", True, (58, 83, 200))

        # Position text next to coin icon with small spacing
        text_x = start_x + projectile_size + 5
        text_y = start_y + (projectile_size - projectiles_text.get_height()) // 2

        surface.blit(projectiles_text, (text_x, text_y))
