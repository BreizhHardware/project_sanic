import re

import pygame
import sys
from pygame.locals import *

from src.Database.LevelDB import LevelDB
from src.Entity.Enemy import Enemy
from src.Menu.LevelSelectMenu import LevelSelectMenu
from src.game import (
    initialize_game,
    reset_game_with_checkpoint,
    clear_checkpoint_database,
)
from src.constant import GameResources
from src.Menu.Menu import Menu
from src.Menu.Leaderboard import Leaderboard
from src.Camera import Camera
from src.Database.CheckpointDB import CheckpointDB
from src.Map.Editor.LevelEditor import LevelEditor
from src.Menu.LevelEditorSelectionMenu import LevelEditorSelectionMenu


def main():
    # Initialize Pygame and game resources
    game_resources = GameResources()
    displaysurface = game_resources.displaysurface
    FramePerSec = game_resources.FramePerSec
    font = game_resources.font
    FPS = game_resources.FPS
    WIDTH = game_resources.WIDTH
    HEIGHT = game_resources.HEIGHT
    ORIGINAL_WIDTH = game_resources.ORIGINAL_WIDTH
    ORIGINAL_HEIGHT = game_resources.ORIGINAL_HEIGHT
    fullscreen = game_resources.fullscreen

    # Add camera initialization
    camera = Camera(WIDTH, HEIGHT, game_resources)

    # Game states
    MENU = 0
    PLAYING = 1
    INFINITE = 2
    LEADERBOARD = 3

    # Initialize game state and objects
    current_state = MENU
    main_menu = Menu(game_resources)
    level_select_menu = None
    level_file = "map/levels/1.json"
    current_menu = "main"
    leaderboard = Leaderboard(WIDTH, HEIGHT, font)

    clear_checkpoint_database()
    projectiles = pygame.sprite.Group()

    pygame.joystick.quit()
    pygame.joystick.init()
    joysticks = []

    try:
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            joysticks.append(joystick)
            print(f"Manette détectée: {joystick.get_name()}")
            print(f"Nombre de boutons: {joystick.get_numbuttons()}")
            print(f"Nombre d'axes: {joystick.get_numaxes()}")
    except pygame.error:
        print("Erreur lors de l'initialisation des manettes")

    # Main game loop
    running = True
    while running:
        try:
            events = []
            try:
                events = pygame.event.get()
            except Exception as e:
                print(f"Erreur lors de la récupération des événements: {e}")
                pygame.joystick.quit()
                pygame.joystick.init()
                continue

            for event in events:
                if event.type == QUIT:
                    running = False
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
                        checkpoint_pos = db.get_checkpoint(level_file)

                        if checkpoint_pos:
                            # Respawn player at checkpoint
                            P1, platforms, all_sprites, background, checkpoints = (
                                reset_game_with_checkpoint(level_file, game_resources)
                            )
                            projectiles.empty()
                        else:
                            # No checkpoint found, return to menu
                            current_state = MENU
                    if event.dict.get("action") == "create_projectile":
                        projectile = event.dict.get("projectile")
                        projectiles.add(projectile)

                # Handle menu events
                if current_state == MENU:
                    if current_menu == "main":
                        action = main_menu.handle_event(event)
                        if action == "level_select":
                            level_select_menu = LevelSelectMenu(game_resources)
                            current_menu = "level_select"
                        elif action == "infinite":
                            current_state = INFINITE
                        elif action == "leaderboard":
                            current_state = LEADERBOARD
                        elif action == "quit":
                            pygame.quit()
                            sys.exit()
                    elif current_menu == "level_select":
                        action = level_select_menu.handle_event(event)
                        if action == "back_to_main":
                            current_menu = "main"
                        elif (
                            isinstance(action, dict)
                            and action.get("action") == "select_level"
                        ):
                            level_file = action.get("level_file")
                            print(level_file)
                            (
                                P1,
                                PT1,
                                platforms,
                                all_sprites,
                                background,
                                checkpoints,
                                exits,
                            ) = initialize_game(game_resources, level_file)
                            projectiles.empty()
                            current_state = PLAYING
                        elif action == "open_editor":
                            editor_select_menu = LevelEditorSelectionMenu(
                                game_resources
                            )
                            current_state = "editor_select"

                # Handle leaderboard events
                elif current_state == LEADERBOARD:
                    action = leaderboard.handle_event(event)
                    if action == "menu":
                        current_state = MENU

                elif current_state == "editor_select":
                    action = editor_select_menu.handle_event(event)
                    if action == "back_to_levels":
                        current_state = MENU
                        current_menu = "level_select"
                    elif isinstance(action, dict):
                        if action["action"] == "edit_level":
                            level_editor = LevelEditor(
                                game_resources, action["level_file"]
                            )
                            current_state = "level_editor"
                        elif action["action"] == "new_level":
                            level_editor = LevelEditor(game_resources)
                            current_state = "level_editor"

                elif current_state == "level_editor":
                    result = level_editor.handle_event(event)
                    if result == "back_to_levels":
                        current_state = "editor_select"
        except Exception as e:
            print(f"Erreur lors du traitement de l'événement: {e}")
            continue

        # Clear screen
        displaysurface.fill((0, 0, 0))

        # Draw appropriate screen based on state
        if current_state == MENU:
            if current_menu == "main":
                main_menu.draw(displaysurface)
            elif current_menu == "level_select":
                level_select_menu.draw(displaysurface)
        elif current_state == "editor_select":
            editor_select_menu.draw(displaysurface)
        elif current_state == "level_editor":
            level_editor.draw(displaysurface)
        elif current_state == LEADERBOARD:
            leaderboard.draw(displaysurface)

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

            if checkpoints is not None:
                checkpoints_hit = pygame.sprite.spritecollide(P1, checkpoints, False)
            else:
                checkpoints_hit = []
            for checkpoint in checkpoints_hit:
                checkpoint.activate()

            exits_hit = pygame.sprite.spritecollide(P1, exits, False) if exits else []
            for exit in exits_hit:
                current_level_match = re.search(r"(\d+)\.json$", level_file)
                if current_level_match:
                    current_level = int(current_level_match.group(1))
                    next_level = current_level + 1

                    # Unlock next level
                    db = LevelDB()
                    db.unlock_level(next_level)
                    db.close()

                    # Return to level select menu
                    current_state = MENU
                    current_menu = "level_select"
                    level_select_menu = LevelSelectMenu(game_resources)

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
