import pygame
import sys
from pygame.locals import *

# Import from pygame_basics
from src.pygame_basics import (
    WIDTH,
    HEIGHT,
    FPS,
    displaysurface,
    FramePerSec,
    font,
    initialize_game,
)

# Import from menu
from src.menu import Menu, Leaderboard


def main():
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
    P1, PT1, platforms, all_sprites = initialize_game()

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

            # Handle menu events
            if current_state == MENU:
                action = menu.handle_event(event)
                if action == "play":
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
            for entity in all_sprites:
                displaysurface.blit(entity.surf, entity.rect)

            # Display FPS and coordinates
            fps = int(FramePerSec.get_fps())
            fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
            displaysurface.blit(fps_text, (10, 10))

            pos_text = font.render(
                f"X: {int(P1.pos.x)}, Y: {int(P1.pos.y)}", True, (255, 255, 255)
            )
            displaysurface.blit(pos_text, (10, 40))

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
