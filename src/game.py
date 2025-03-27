import pygame
import sys
from pygame.locals import *
from src.Entity.Platform import Platform
from src.Entity.Player import Player
from src.constant import displaysurface, FramePerSec, font, FPS, platforms, all_sprites
from src.Map.parser import MapParser


def initialize_game(map_file="map_test.json"):
    """Initialize game with map from JSON file"""
    parser = MapParser()
    map_objects = parser.load_map(map_file)

    if not map_objects:
        # Fallback to default setup if map loading fails
        platforms.empty()
        all_sprites.empty()

        PT1 = Platform(1200, 20, 600, 400)
        P1 = Player()

        platforms.add(PT1)
        all_sprites.add(PT1)
        all_sprites.add(P1)

        return P1, PT1, platforms, all_sprites, None  # Return None for background

    return (
        map_objects["player"],
        None,  # No specific platform reference needed
        map_objects["platforms"],
        map_objects["all_sprites"],
        parser.background,  # Return the loaded background
    )


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
