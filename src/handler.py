import re
import pygame
import sys
from pygame.locals import *
import numpy as np

from src.Database.LeaderboardDB import LeaderboardDB
from src.Database.LevelDB import LevelDB
from src.Entity.Enemy import Enemy
from src.Menu.LevelSelectMenu import LevelSelectMenu
from src.game import (
    initialize_game,
    reset_game_with_checkpoint,
    clear_checkpoint_database,
    start_infinite_mode,
    handle_exit_collision,
)
from src.constant import GameResources
from src.Menu.Menu import Menu
from src.Menu.Leaderboard import Leaderboard
from src.Camera import Camera
from src.Database.CheckpointDB import CheckpointDB
from src.Map.Editor.LevelEditor import LevelEditor
from src.Menu.LevelEditorSelectionMenu import LevelEditorSelectionMenu
from src.Map.Speedrun.SpeedrunTimer import SpeedrunTimer
from src.Menu.InstructionsScreen import InstructionsScreen


def initialize_game_resources():
    """Initialize game resources and initial states"""
    game_resources = GameResources()
    displaysurface = game_resources.displaysurface
    camera = Camera(game_resources.WIDTH, game_resources.HEIGHT, game_resources)

    # Initialize death screen resources
    death_timer = 0
    death_display_time = 2
    try:
        death_image = pygame.image.load("assets/player/dead.jpg")
    except Exception as e:
        print(f"Error loading image: {e}")
        death_image = None

    try:
        death_sound = pygame.mixer.Sound("assets/sound/Death.mp3")
        death_display_time = death_sound.get_length()
    except Exception as e:
        print(f"Error loading Death.mp3 sound: {e}")
        death_sound = None

    # Initialize joysticks
    pygame.joystick.quit()
    pygame.joystick.init()
    joysticks = []
    try:
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            joysticks.append(joystick)
    except pygame.error:
        print("Error while initializing joysticks")

    clear_checkpoint_database()
    projectiles = pygame.sprite.Group()

    # Game states initialization
    current_state = 5  # INSTRUCTIONS
    current_menu = "main"
    instructions_screen = InstructionsScreen(game_resources)
    main_menu = Menu(game_resources)
    level_select_menu = None
    editor_select_menu = None
    level_file = "map/levels/1.json"
    leaderboard_db = LeaderboardDB()
    leaderboard = Leaderboard(
        game_resources.WIDTH, game_resources.HEIGHT, game_resources.font, leaderboard_db
    )

    try:
        pygame.mixer.music.load("assets/sound/main_music.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error loading main music: {e}")

    return (
        game_resources,
        displaysurface,
        camera,
        death_timer,
        death_display_time,
        death_image,
        death_sound,
        current_state,
        current_menu,
        main_menu,
        level_select_menu,
        level_file,
        leaderboard,
        projectiles,
        joysticks,
        editor_select_menu,
        leaderboard_db,
        instructions_screen,
    )


def handle_system_events(
    event, current_state, fullscreen, displaysurface, ORIGINAL_WIDTH, ORIGINAL_HEIGHT
):
    """Handle system events like quit, resolution changes, etc."""
    if event.type == QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            if current_state in [1, 2]:  # PLAYING, INFINITE
                current_state = 0  # MENU
            else:
                pygame.quit()
                sys.exit()
        elif event.key == K_F11:
            fullscreen = not fullscreen
            if fullscreen:
                # Store current window size before going fullscreen
                ORIGINAL_WIDTH, ORIGINAL_HEIGHT = displaysurface.get_size()
                displaysurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                # Return to windowed mode with previous size
                displaysurface = pygame.display.set_mode(
                    (ORIGINAL_WIDTH, ORIGINAL_HEIGHT), pygame.RESIZABLE
                )
    elif event.type == VIDEORESIZE:
        if not fullscreen:
            displaysurface = pygame.display.set_mode(
                (event.w, event.h), pygame.RESIZABLE
            )
            # Update window dimensions
            ORIGINAL_WIDTH, ORIGINAL_HEIGHT = event.w, event.h
    elif event.type == pygame.JOYBUTTONDOWN:
        try:
            if event.button == 4:  # Triangle sur la plupart des manettes
                if current_state in [1, 2]:  # PLAYING, INFINITE
                    current_state = 0  # MENU
                else:
                    pygame.quit()
                    sys.exit()
        except Exception as e:
            print(f"Error while handling joystick button: {e}")

    return current_state, fullscreen, displaysurface, ORIGINAL_WIDTH, ORIGINAL_HEIGHT


def handle_game_events(
    event,
    current_state,
    death_timer,
    death_sound,
    level_file,
    game_resources,
    projectiles,
):
    """Handle game-specific events like player death and projectile creation"""
    checkpoint_data = None

    if event.type == USEREVENT:
        if event.dict.get("action") == "player_death":
            current_state = 4  # DEATH_SCREEN
            death_timer = 0
            if death_sound:
                death_sound.play()

            is_infinite_mode = (
                hasattr(game_resources, "infinite_mode")
                and game_resources.infinite_mode
            )

            if not is_infinite_mode:
                db = CheckpointDB()
                checkpoint_data = db.get_checkpoint(level_file)
            else:
                checkpoint_data = None

        if event.dict.get("action") == "create_projectile":
            projectile = event.dict.get("projectile")
            projectiles.add(projectile)

    return current_state, death_timer, checkpoint_data, projectiles


def handle_menu_events(
    event,
    current_state,
    current_menu,
    main_menu,
    level_select_menu,
    game_resources,
    level_file,
):
    """Handle menu interaction events"""
    P1, PT1, platforms, all_sprites, background, checkpoints, exits, collectibles = [
        None
    ] * 8
    editor_select_menu = None

    if current_menu == "main":
        action = main_menu.handle_event(event)
        if action == "level_select":
            level_select_menu = LevelSelectMenu(game_resources)
            current_menu = "level_select"
        elif action == "infinite":
            current_state = 2  # INFINITE
        elif action == "leaderboard":
            current_state = 3  # LEADERBOARD
        elif action == "quit":
            pygame.quit()
            sys.exit()
    elif current_menu == "level_select":
        action = level_select_menu.handle_event(event)
        if action == "back_to_main":
            current_menu = "main"
        elif isinstance(action, dict) and action.get("action") == "select_level":
            level_file = action.get("level_file")
            (
                P1,
                PT1,
                platforms,
                all_sprites,
                background,
                checkpoints,
                exits,
                collectibles,
            ) = initialize_game(game_resources, level_file)

            level_id = level_file.split("/")[-1].split(".")[0]
            speedrun_timer = SpeedrunTimer(level_id)
            speedrun_timer.start()
            speedrun_timer.total_items = len(
                [
                    c
                    for c in collectibles
                    if hasattr(c, "__class__")
                    and c.__class__.__name__ not in ["JumpBoost", "SpeedBoost"]
                ]
            )
            speedrun_timer.collected_items = 0

            projectiles = pygame.sprite.Group()
            current_state = 1  # PLAYING
            return (
                current_state,
                current_menu,
                level_select_menu,
                level_file,
                P1,
                PT1,
                platforms,
                all_sprites,
                background,
                checkpoints,
                exits,
                collectibles,
                projectiles,
                editor_select_menu,
                speedrun_timer,
            )
        elif action == "open_editor":
            editor_select_menu = LevelEditorSelectionMenu(game_resources)
            current_state = "editor_select"
            return (
                current_state,
                current_menu,
                level_select_menu,
                level_file,
                P1,
                PT1,
                platforms,
                all_sprites,
                background,
                checkpoints,
                exits,
                collectibles,
                None,
                editor_select_menu,
                None,
            )

    return (
        current_state,
        current_menu,
        level_select_menu,
        level_file,
        P1,
        PT1,
        platforms,
        all_sprites,
        background,
        checkpoints,
        exits,
        collectibles,
        None,
        editor_select_menu,
        None,
    )


def handle_leaderboard_events(event, current_state, leaderboard):
    """Handle leaderboard events"""
    action = leaderboard.handle_event(event)
    if action == "menu":
        current_state = 0  # MENU
    return current_state


def handle_editor_events(
    event, current_state, editor_select_menu, current_menu, game_resources
):
    """Handle level editor events"""
    level_editor = None
    action = editor_select_menu.handle_event(event)

    if action == "back_to_levels":
        current_state = 0  # MENU
        current_menu = "level_select"
    elif isinstance(action, dict):
        if action["action"] == "edit_level":
            level_editor = LevelEditor(game_resources, action["level_file"])
            current_state = "level_editor"
        elif action["action"] == "new_level":
            level_editor = LevelEditor(game_resources)
            current_state = "level_editor"

    return current_state, current_menu, level_editor


def update_playing_state(
    P1, platforms, projectiles, WIDTH, HEIGHT, camera, all_sprites
):
    """Update game state while playing"""
    # Update player
    P1.move()
    P1.update()
    P1.attack()
    projectiles.update(WIDTH, HEIGHT, P1, camera)

    # Update camera to follow player
    camera.update(P1)

    # Handle moving platforms
    for platform in platforms:
        if platform.is_moving and platform.movement_type == "linear":
            if platform.movement_points[0]["x"] - platform.movement_points[1]["x"] == 0:
                dir = 0
            else:
                dir = 1
                if P1.rect.colliderect(platform.rect) and P1.pos.y == platform.rect.y:
                    P1.pos.x += platform.movement_speed * platform.coeff

            platform.move_linear(
                dir,
                platform.movement_points,
                platform.movement_speed,
                platform.wait_time,
                platform.coeff,
            )

        if platform.is_moving and platform.movement_type == "circular":
            if (
                P1.rect.colliderect(platform.rect)
                and P1.pos.y == platform.rect.y
                and platform.clockwise
            ):
                P1.pos.x = P1.pos.x + platform.radius * np.cos(platform.angle)
                P1.pos.y = P1.pos.y + platform.radius * np.sin(platform.angle)

            if (
                P1.rect.colliderect(platform.rect)
                and P1.pos.y == platform.rect.y
                and not platform.clockwise
            ):
                P1.pos.x = P1.pos.x + platform.radius * np.cos(platform.angle)
                P1.pos.y = P1.pos.y + platform.radius * np.sin(-platform.angle)

            platform.move_circular(
                platform.center,
                platform.angular_speed,
                platform.radius,
                platform.clockwise,
            )

    # Update all sprites
    for sprite in all_sprites:
        if isinstance(sprite, Enemy):
            sprite.update(P1)
            projectiles.update(WIDTH, HEIGHT, P1, camera, sprite)
        else:
            sprite.update()


def draw_background(displaysurface, background, camera, WIDTH, HEIGHT):
    """Draw background with parallax effect"""
    bg_width = WIDTH * 1.5
    bg_height = HEIGHT * 1.5

    # Resize if necessary
    if background.get_width() != bg_width or background.get_height() != bg_height:
        background = pygame.transform.scale(background, (bg_width, bg_height))

    # Parallax effect
    parallax_factor = 0.3

    bg_x = (camera.camera.x * parallax_factor) % bg_width
    bg_y = (camera.camera.y * parallax_factor) % bg_height

    if bg_x > 0:
        bg_x -= bg_width
    if bg_y > 0:
        bg_y -= bg_height

    # Draw background in all directions to create seamless effect
    displaysurface.blit(background, (bg_x, bg_y))

    if bg_x > 0:
        displaysurface.blit(background, (bg_x - bg_width, bg_y))
    if bg_x + bg_width < WIDTH:
        displaysurface.blit(background, (bg_x + bg_width, bg_y))

    if bg_y > 0:
        displaysurface.blit(background, (bg_x, bg_y - bg_height))
        if bg_x > 0:
            displaysurface.blit(background, (bg_x - bg_width, bg_y - bg_height))
        if bg_x + bg_width < WIDTH:
            displaysurface.blit(background, (bg_x + bg_width, bg_y - bg_height))

    if bg_y + bg_height < HEIGHT:
        displaysurface.blit(background, (bg_x, bg_y + bg_height))
        if bg_x > 0:
            displaysurface.blit(background, (bg_x - bg_width, bg_y + bg_height))
        if bg_x + bg_width < WIDTH:
            displaysurface.blit(background, (bg_x + bg_width, bg_y + bg_height))


def draw_playing_state(
    displaysurface,
    background,
    all_sprites,
    P1,
    camera,
    WIDTH,
    HEIGHT,
    font,
    projectiles,
    checkpoints,
    exits,
    collectibles,
    game_resources,
    level_file,
    FramePerSec,
    speedrun_timer=None,
):
    """Draw game state while playing"""
    # Draw background
    if background:
        draw_background(displaysurface, background, camera, WIDTH, HEIGHT)

    # Draw all sprites with camera offset
    for entity in all_sprites:
        camera_adjusted_rect = entity.rect.copy()
        camera_adjusted_rect.x += camera.camera.x
        camera_adjusted_rect.y += camera.camera.y
        displaysurface.blit(entity.surf, camera_adjusted_rect)

    # Draw projectiles with camera offset
    for projectile in projectiles:
        camera_adjusted_rect = projectile.rect.copy()
        camera_adjusted_rect.x += camera.camera.x
        camera_adjusted_rect.y += camera.camera.y
        displaysurface.blit(projectile.surf, camera_adjusted_rect)

    # Handle checkpoints
    if checkpoints is not None:
        checkpoints_hit = pygame.sprite.spritecollide(P1, checkpoints, False)
        for checkpoint in checkpoints_hit:
            checkpoint.activate()

    # Handle exit collisions
    result = handle_exits(P1, exits, game_resources, level_file, speedrun_timer)

    # Handle collectibles
    collectibles_hit = pygame.sprite.spritecollide(P1, collectibles, False)
    for collectible in collectibles_hit:
        # Vérifier le type de collectible et appeler la méthode appropriée
        if (
            hasattr(collectible, "__class__")
            and collectible.__class__.__name__ == "JumpBoost"
        ):
            collectible.on_collision(P1)
        elif (
            hasattr(collectible, "__class__")
            and collectible.__class__.__name__ == "SpeedBoost"
        ):
            collectible.on_collision(P1, game_resources)
        else:
            # Pour les pièces standard et autres collectibles
            collectible.on_collision()
            P1.collect_coin(displaysurface, speedrun_timer)

    for text in P1.floating_texts:
        text.draw(displaysurface)

    # Draw UI elements
    draw_ui_elements(displaysurface, P1, FramePerSec, font, speedrun_timer)

    return result


def handle_exits(P1, exits, game_resources, level_file, speedrun_timer=None):
    """Handle collisions with level exits"""
    exits_hit = pygame.sprite.spritecollide(P1, exits, False) if exits else []
    for exit in exits_hit:
        if not exit.locked:
            if speedrun_timer and speedrun_timer.is_running:
                collected_coins = speedrun_timer.collected_items
                total_coins = speedrun_timer.total_items

                speedrun_timer.stop()
                speedrun_timer.save_time(collected_coins, total_coins)
            if (
                hasattr(game_resources, "infinite_mode")
                and game_resources.infinite_mode
            ):
                # Infinite mode: load the next level without going back to menu
                if hasattr(game_resources, "infinite_mode_db"):
                    # Zeldo : add 100 points
                    game_resources.infinite_mode_db.add_score("player", 100)
                    # Add coins points also
                    game_resources.infinite_mode_db.add_score("player", P1.coins * 10)
                result = handle_exit_collision(exit, game_resources, level_file)
                return {"action": "continue_infinite", "result": result}
            else:
                # Normal mode: unlock the next level and return to menu
                current_level_match = re.search(r"(\d+)\.json$", level_file)
                if current_level_match:
                    current_level = int(current_level_match.group(1))
                    next_level = current_level + 1

                    # Unlock next level
                    db = LevelDB()
                    db.unlock_level(next_level)
                    db.close()

                    # Return to level select menu
                    return {
                        "action": "return_to_level_select",
                        "current_state": 0,  # MENU
                        "current_menu": "level_select",
                    }
    return None


def draw_ui_elements(displaysurface, P1, FramePerSec, font, speedrun_timer=None):
    """Draw UI elements like FPS, player position, health, etc."""
    # FPS counter
    # fps = int(FramePerSec.get_fps())
    # fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    # displaysurface.blit(fps_text, (10, 10))

    # Player position
    # pos_text = font.render(
    # f"X: {int(P1.pos.x)}, Y: {int(P1.pos.y)}", True, (255, 255, 255)
    # )
    # displaysurface.blit(pos_text, (10, 40))

    # Player UI elements
    P1.draw_dash_cooldown_bar(displaysurface)
    P1.draw_lives(displaysurface)
    P1.draw_coins(displaysurface)
    P1.draw_projectiles_amount(displaysurface)

    if speedrun_timer:
        speedrun_timer.draw(displaysurface)


def handle_death_screen(
    P1,
    displaysurface,
    death_timer,
    dt,
    death_image,
    death_display_time,
    checkpoint_data,
    level_file,
    game_resources,
    WIDTH,
    HEIGHT,
    leaderboard_db,
):
    """Handle player death screen"""
    # Fill background
    displaysurface.fill((0, 0, 0))

    # Display death image
    if death_image:
        scaled_image = pygame.transform.scale(death_image, (WIDTH, HEIGHT))
        image_rect = scaled_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        displaysurface.blit(scaled_image, image_rect)

    # Update death timer
    death_timer += dt

    # Check if death screen should end
    if death_timer >= death_display_time:
        if checkpoint_data:
            # Restart from checkpoint
            P1, platforms, all_sprites, background, checkpoints, collectibles = (
                reset_game_with_checkpoint(level_file, game_resources)
            )
            projectiles = pygame.sprite.Group()
            return {
                "action": "restart_level",
                "death_timer": 0,
                "current_state": 1,  # PLAYING
                "P1": P1,
                "platforms": platforms,
                "all_sprites": all_sprites,
                "background": background,
                "checkpoints": checkpoints,
                "collectibles": collectibles,
                "projectiles": projectiles,
            }
        else:
            if hasattr(game_resources, "infinite_mode_db"):
                # Save score to database
                game_resources.infinite_mode_db.add_score("player", P1.coins * 10)
                # Get all scores from the database
                all_scores = game_resources.infinite_mode_db.get_all()
                game_resources.infinite_mode_db.clear_InfiniteModeDB()
                game_resources.infinite_mode_db.close()
                # Calculate total points, add them to leaderboard table
                if leaderboard_db:
                    total = 0
                    for i in range(len(all_scores)):
                        total += all_scores[i][1]
                    leaderboard_db.add_score("player", total)

            # Return to menu
            if hasattr(game_resources, "infinite_mode"):
                game_resources.infinite_mode = False
            return {
                "action": "return_to_menu",
                "death_timer": 0,
                "current_state": 0,  # MENU
            }

    return {"action": None, "death_timer": death_timer}


def handler():
    """Main function that handles the game flow"""
    # Game state constants
    MENU, PLAYING, INFINITE, LEADERBOARD, DEATH_SCREEN, INSTRUCTIONS = 0, 1, 2, 3, 4, 5
    previous_state = None

    # Initialize game resources and states
    (
        game_resources,
        displaysurface,
        camera,
        death_timer,
        death_display_time,
        death_image,
        death_sound,
        current_state,
        current_menu,
        main_menu,
        level_select_menu,
        level_file,
        leaderboard,
        projectiles,
        joysticks,
        editor_select_menu,
        leaderboard_db,
        instructions_screen,
    ) = initialize_game_resources()

    # Initialize editor variables
    level_editor = None
    speedrun_timer = None

    # Main game loop
    running = True
    while running:
        try:
            # Get delta time
            dt = game_resources.FramePerSec.get_time() / 1000.0

            # Get events
            try:
                events = pygame.event.get()
            except Exception as e:
                print(f"Error while getting events: {e}")
                pygame.joystick.quit()
                pygame.joystick.init()
                events = []
                continue

            # Process events
            for event in events:
                # Process system events (quit, resolution changes, etc.)
                (
                    current_state,
                    game_resources.fullscreen,
                    displaysurface,
                    game_resources.ORIGINAL_WIDTH,
                    game_resources.ORIGINAL_HEIGHT,
                ) = handle_system_events(
                    event,
                    current_state,
                    game_resources.fullscreen,
                    displaysurface,
                    game_resources.ORIGINAL_WIDTH,
                    game_resources.ORIGINAL_HEIGHT,
                )

                # Process game events based on current state
                if current_state == MENU:
                    # Handle menu interactions
                    result = handle_menu_events(
                        event,
                        current_state,
                        current_menu,
                        main_menu,
                        level_select_menu,
                        game_resources,
                        level_file,
                    )

                    current_state, current_menu, level_select_menu, level_file = result[
                        :4
                    ]
                    if result[4]:  # If level has been selected
                        (
                            P1,
                            PT1,
                            platforms,
                            all_sprites,
                            background,
                            checkpoints,
                            exits,
                            collectibles,
                        ) = result[4:12]
                        projectiles = result[12]
                        editor_select_menu = result[13]
                        speedrun_timer = result[14]

                elif current_state == LEADERBOARD:
                    current_state = handle_leaderboard_events(
                        event, current_state, leaderboard
                    )

                elif current_state == "editor_select":
                    # Create editor_select_menu if it doesn't exist
                    if editor_select_menu is None:
                        editor_select_menu = LevelEditorSelectionMenu(game_resources)

                    current_state, current_menu, level_editor = handle_editor_events(
                        event,
                        current_state,
                        editor_select_menu,
                        current_menu,
                        game_resources,
                    )

                elif current_state == "level_editor":
                    if level_editor is not None:
                        result = level_editor.handle_event(event)
                        if result == "back_to_levels":
                            current_state = "editor_select"
                            if editor_select_menu is None:
                                editor_select_menu = LevelEditorSelectionMenu(
                                    game_resources
                                )

                elif current_state == INSTRUCTIONS:
                    for event in events:
                        result = instructions_screen.handle_event(event)
                        if result == "menu":
                            current_state = MENU
                    instructions_screen.draw(displaysurface)

                # Process general game events (player death, projectiles, etc.)
                if event.type == USEREVENT:
                    current_state, death_timer, checkpoint_data, projectiles = (
                        handle_game_events(
                            event,
                            current_state,
                            death_timer,
                            death_sound,
                            level_file,
                            game_resources,
                            projectiles,
                        )
                    )

                elif event.type == pygame.USEREVENT + 2:
                    if hasattr(P1, "active_jump_boost") and P1.active_jump_boost:
                        P1.jump_power = P1.active_jump_boost["original_power"]
                        P1.jump_boost_active = False
                        P1.active_jump_boost = None

                elif event.type == pygame.USEREVENT + 3:  # Speed boost expiration
                    if hasattr(P1, "active_speed_boost") and P1.active_speed_boost:
                        # Restore original movement speed
                        game_resources.ACC = P1.active_speed_boost["original_ACC"]
                        # Remove visual feedback
                        P1.speed_boost_active = False
                        # Clear boost data
                        P1.active_speed_boost = None

            # Clear screen
            displaysurface.fill((0, 0, 0))

            # Update and render based on current state
            if current_state == MENU:
                if current_menu == "main":
                    main_menu.draw(displaysurface)
                elif current_menu == "level_select":
                    if level_select_menu is None:
                        level_select_menu = LevelSelectMenu(game_resources)
                    level_select_menu.draw(displaysurface)

            elif current_state == "editor_select":
                if editor_select_menu is None:
                    editor_select_menu = LevelEditorSelectionMenu(game_resources)
                editor_select_menu.draw(displaysurface)

            elif current_state == "level_editor":
                if level_editor is not None:
                    level_editor.draw(displaysurface)

            elif current_state == LEADERBOARD:
                if previous_state != "LEADERBOARD":
                    leaderboard.refresh_scores(previous_state)
                    previous_state = "LEADERBOARD"
                leaderboard.draw(displaysurface)

            elif current_state == PLAYING:
                previous_state = "PLAYING"
                # Update game state
                update_playing_state(
                    P1,
                    platforms,
                    projectiles,
                    game_resources.WIDTH,
                    game_resources.HEIGHT,
                    camera,
                    all_sprites,
                )

                if speedrun_timer:
                    speedrun_timer.update()

                # Draw game state and process exit collisions
                exit_result = draw_playing_state(
                    displaysurface,
                    background,
                    all_sprites,
                    P1,
                    camera,
                    game_resources.WIDTH,
                    game_resources.HEIGHT,
                    game_resources.font,
                    projectiles,
                    checkpoints,
                    exits,
                    collectibles,
                    game_resources,
                    level_file,
                    game_resources.FramePerSec,
                    speedrun_timer,
                )

                # Handle level exit result
                if exit_result:
                    if exit_result.get("action") == "return_to_level_select":
                        current_state = exit_result["current_state"]
                        current_menu = exit_result["current_menu"]
                        level_select_menu = LevelSelectMenu(game_resources)
                    elif exit_result.get("action") == "continue_infinite":
                        # Récupérer le résultat du handle_exit_collision
                        infinite_result = exit_result["result"]
                        # Utiliser le résultat pour continuer en mode infini
                        if infinite_result:
                            # Utiliser les valeurs retournées par handle_exit_collision
                            # Adapter selon la structure du tuple retourné
                            (
                                P1,
                                PT1,
                                platforms,
                                all_sprites,
                                background,
                                checkpoints,
                                exits,
                                collectibles,
                            ) = infinite_result

            elif current_state == INFINITE:
                previous_state = "INFINITE"
                # Start infinite mode and switch to playing
                (
                    P1,
                    PT1,
                    platforms,
                    all_sprites,
                    background,
                    checkpoints,
                    exits,
                    collectibles,
                ) = start_infinite_mode(game_resources)
                current_state = PLAYING

            elif current_state == DEATH_SCREEN:
                # Handle death screen
                death_result = handle_death_screen(
                    P1,
                    displaysurface,
                    death_timer,
                    dt,
                    death_image,
                    death_display_time,
                    checkpoint_data,
                    level_file,
                    game_resources,
                    game_resources.WIDTH,
                    game_resources.HEIGHT,
                    leaderboard_db,
                )

                death_timer = death_result["death_timer"]

                if death_result["action"] == "restart_level":
                    current_state = death_result["current_state"]
                    P1 = death_result["P1"]
                    platforms = death_result["platforms"]
                    all_sprites = death_result["all_sprites"]
                    background = death_result["background"]
                    checkpoints = death_result["checkpoints"]
                    collectibles = death_result["collectibles"]
                    projectiles = death_result["projectiles"]

                elif death_result["action"] == "return_to_menu":
                    current_state = death_result["current_state"]

            elif current_state == INSTRUCTIONS:
                for event in events:
                    result = instructions_screen.handle_event(event)
                    if result == "menu":
                        current_state = MENU
                instructions_screen.draw(displaysurface)

            # Update display
            pygame.display.update()
            game_resources.FramePerSec.tick(game_resources.FPS)

        except Exception as e:
            print(f"Error in main game loop: {e}")
            continue
