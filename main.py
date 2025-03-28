import pygame
import sys
from pygame.locals import *

from src.Entity.Enemy import Enemy
from src.game import initialize_game, reset_game, reset_game_with_checkpoint
from src.constant import (
    displaysurface,
    FramePerSec,
    font,
    FPS,
    WIDTH,
    HEIGHT,
    ORIGINAL_WIDTH,
    ORIGINAL_HEIGHT,
    fullscreen,
)
from src.Menu.Menu import Menu
from src.Menu.Leaderboard import Leaderboard
from src.Camera import Camera
from src.Database.CheckpointDB import CheckpointDB


def main():
    # Declare globals that we'll modify
    global displaysurface, fullscreen, ORIGINAL_WIDTH, ORIGINAL_HEIGHT

    # Add camera initialization
    camera = Camera(WIDTH, HEIGHT)

    # Game states
    MENU = 0
    PLAYING = 1
    INFINITE = 2
    LEADERBOARD = 3

    # Initialize game state and objects
    current_state = MENU
    menu = Menu()
    leaderboard = Leaderboard()

    # Initialize game components
    P1, PT1, platforms, all_sprites, background, checkpoints = initialize_game(
        "map_test.json"
    )
    projectiles = pygame.sprite.Group()

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if current_state in [PLAYING, INFINITE]:
                        current_state = MENU
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        # Store current window size before going fullscreen
                        ORIGINAL_WIDTH, ORIGINAL_HEIGHT = displaysurface.get_size()
                        displaysurface = pygame.display.set_mode(
                            (0, 0), pygame.FULLSCREEN
                        )
                    else:
                        # Return to windowed mode with previous size
                        displaysurface = pygame.display.set_mode(
                            (ORIGINAL_WIDTH, ORIGINAL_HEIGHT), pygame.RESIZABLE
                        )
            elif (
                event.type == VIDEORESIZE
            ):  # Fixed indentation - moved out of K_F11 condition
                if not fullscreen:
                    displaysurface = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )
                    # Update window dimensions
                    ORIGINAL_WIDTH, ORIGINAL_HEIGHT = event.w, event.h
            elif event.type == USEREVENT:
                if event.action == "player_death":
                    db = CheckpointDB()
                    checkpoint_pos = db.get_checkpoint("map_test.json")

                    if checkpoint_pos:
                        # Respawn player at checkpoint
                        P1, platforms, all_sprites, background, checkpoints = (
                            reset_game_with_checkpoint("map_test.json")
                        )
                        projectiles.empty()
                        print("Joueur réanimé au checkpoint")
                    else:
                        # No checkpoint found, return to menu
                        current_state = MENU
                        print("Game over - retour au menu")
                if event.dict.get("action") == "create_projectile":
                    projectile = event.dict.get("projectile")
                    projectiles.add(projectile)

            # Handle menu events
            if current_state == MENU:
                action = menu.handle_event(event)
                if action == "play":
                    P1, platforms, all_sprites, background, checkpoints = reset_game()
                    current_state = PLAYING
                elif action == "infinite":
                    current_state = INFINITE
                elif action == "leaderboard":
                    current_state = LEADERBOARD
                elif action == "quit":
                    pygame.quit()
                    sys.exit()

            # Handle leaderboard events
            elif current_state == LEADERBOARD:
                action = leaderboard.handle_event(event)
                if action == "menu":
                    current_state = MENU

        # Clear screen
        displaysurface.fill((0, 0, 0))

        # Draw appropriate screen based on state
        if current_state == MENU:
            menu.draw(displaysurface)

        elif current_state == PLAYING:
            # Regular game code
            P1.move()
            P1.update()

            # Update camera to follow player
            camera.update(P1)

            # Clear screen
            displaysurface.fill((0, 0, 0))

            for platform in platforms:
                if platform.is_moving and platform.movement_type == "linear":
                    if (
                        platform.movement_points[0]["x"]
                        - platform.movement_points[1]["x"]
                        == 0
                    ):
                        dir = 0
                    else:
                        dir = 1
                    platform.move_linear(
                        dir,
                        platform.movement_points,
                        platform.movement_speed,
                        platform.wait_time,
                        platform.coeff,
                    )

            if background:
                parallax_factor = 0.3
                bg_x = camera.camera.x * parallax_factor
                bg_y = camera.camera.y * parallax_factor
                displaysurface.blit(background, (bg_x, bg_y))

            # Draw all sprites with camera offset applied
            for entity in all_sprites:
                # Calculate position adjusted for camera
                camera_adjusted_rect = entity.rect.copy()
                camera_adjusted_rect.x += camera.camera.x
                camera_adjusted_rect.y += camera.camera.y
                displaysurface.blit(entity.surf, camera_adjusted_rect)

            for sprite in all_sprites:
                if isinstance(sprite, Enemy):
                    sprite.update(P1)
                else:
                    sprite.update()

            projectiles.update(WIDTH, HEIGHT, P1, camera)

            for projectile in projectiles:
                # Calculate position adjusted for camera (comme pour les autres sprites)
                camera_adjusted_rect = projectile.rect.copy()
                camera_adjusted_rect.x += camera.camera.x
                camera_adjusted_rect.y += camera.camera.y
                displaysurface.blit(projectile.surf, camera_adjusted_rect)

                print(
                    f"Projectile: pos={projectile.pos}, rect={projectile.rect}, camera={camera.camera}"
                )

            checkpoints_hit = pygame.sprite.spritecollide(P1, checkpoints, False)
            for checkpoint in checkpoints_hit:
                checkpoint.activate()

            # Display FPS and coordinates (fixed position UI elements)
            fps = int(FramePerSec.get_fps())
            fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
            displaysurface.blit(fps_text, (10, 10))

            P1.draw_dash_cooldown_bar(displaysurface)

            pos_text = font.render(
                f"X: {int(P1.pos.x)}, Y: {int(P1.pos.y)}", True, (255, 255, 255)
            )
            displaysurface.blit(pos_text, (10, 40))

            P1.draw_dash_cooldown_bar(displaysurface)
            P1.draw_lives(displaysurface)

        elif current_state == INFINITE:
            # Placeholder for infinite mode
            text = font.render("Mode Infini - À implémenter", True, (255, 255, 255))
            displaysurface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        elif current_state == LEADERBOARD:
            leaderboard.draw(displaysurface)

        pygame.display.update()
        FramePerSec.tick(FPS)


if __name__ == "__main__":
    main()
