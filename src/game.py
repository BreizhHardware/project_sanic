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


def reset_game():
    """Reset the game to initial state"""
    global platforms, all_sprites, camera

    # Empty all sprite groups
    platforms.empty()
    all_sprites.empty()

    # Reload game objects
    player, _, platforms, all_sprites, background = initialize_game("map_test.json")

    return player, platforms, all_sprites, background


if __name__ == "__main__":
    print("Please run the game using main.py")
