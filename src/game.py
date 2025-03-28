import pygame
import sys
from pygame.locals import *

from src.Database.LevelDB import LevelDB
from src.Entity.Platform import Platform
from src.Entity.Player import Player
from src.Map.parser import MapParser
from src.Database.CheckpointDB import CheckpointDB


def initialize_game(game_resources, map_file="map/levels/1.json"):
    """
    Initialize game with map from JSON file

    Args:
        game_resources: GameResources object containing pygame resources
        map_file (str): Name of the map JSON file to load

    Returns:
        tuple: (player, platform, platforms_group, all_sprites, background, checkpoints, exits)
    """
    parser = MapParser(game_resources)
    map_objects = parser.load_map(map_file)

    if not map_objects:
        # Fallback to default setup if map loading fails
        game_resources.platforms.empty()
        game_resources.all_sprites.empty()

        PT1 = Platform(1200, 20, 600, 400)
        P1 = Player(game_resources)

        game_resources.platforms.add(PT1)
        game_resources.all_sprites.add(PT1)
        game_resources.all_sprites.add(P1)

        return (
            P1,
            PT1,
            game_resources.platforms,
            game_resources.all_sprites,
            None,
            None,
            None,
        )

    # Set player reference for exits if they exist
    exits = map_objects.get("exits", None)
    if exits and map_objects["player"]:
        for exit_obj in exits:
            exit_obj.set_player(map_objects["player"])

    return (
        map_objects["player"],
        None,
        map_objects["platforms"],
        map_objects["all_sprites"],
        parser.background,
        map_objects["checkpoints"],
        exits,
    )


def reset_game_with_checkpoint(map_name, game_resources):
    """
    Reset the game and respawn player at checkpoint if available

    Args:
        map_name: Name of the current map
        game_resources: GameResources object
    """
    # Check the checkpoint database for saved checkpoint
    db = CheckpointDB()
    checkpoint_pos = db.get_checkpoint(map_name)

    # Initialize game
    player, _, platforms, all_sprites, background, checkpoints, exits = initialize_game(
        game_resources, map_name
    )

    # If checkpoint exists, respawn player at checkpoint
    if checkpoint_pos:
        player.pos = game_resources.vec(checkpoint_pos[0], checkpoint_pos[1])
        player.update_rect()

    return player, platforms, all_sprites, background, checkpoints


def clear_checkpoint_database():
    """
    Clear all checkpoints from the database.
    Used when starting a new game session.
    """
    try:
        db = CheckpointDB()
        db.clear_all()
        db.close()
        print("Checkpoint database cleared successfully")
    except Exception as e:
        print(f"Error clearing checkpoint database: {e}")


def clear_level_progress():
    """
    Clear all level progress from the database.
    Used when starting a new game session.
    """
    try:
        db = LevelDB()
        db.reset_progress()
        db.close()
        print("Level progress cleared successfully")
    except Exception as e:
        print(f"Error clearing level progress: {e}")


if __name__ == "__main__":
    print("Please run the game using main.py")
