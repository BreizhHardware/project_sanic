import json
import pygame
import os
from src.Entity.Platform import Platform
from src.Entity.Player import Player
from src.Entity.Enemy import Enemy
from src.Entity.Checkpoint import Checkpoint
from src.Entity.Exit import Exit


class MapParser:
    def __init__(self, game_resources):
        self.game_resources = game_resources
        self.all_sprites = self.game_resources.all_sprites
        self.platforms = self.game_resources.platforms
        self.exits = self.game_resources.exits
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.checkpoints = pygame.sprite.Group()
        self.player = None

    def load_map(self, map_file):
        """Load and parse a map from JSON file"""
        try:
            with open(map_file, "r") as file:
                map_data = json.load(file)

            # Create all game objects from map data
            self.create_map_objects(map_data, map_file)

            return {
                "player": self.player,
                "all_sprites": self.all_sprites,
                "platforms": self.platforms,
                "enemies": self.enemies,
                "collectibles": self.collectibles,
                "map_properties": {
                    "name": map_data.get("name", "Unnamed Level"),
                    "width": map_data.get("width", self.game_resources.WIDTH),
                    "height": map_data.get("height", self.game_resources.HEIGHT),
                },
                "checkpoints": self.checkpoints,
                "exits": self.exits,
            }
        except Exception as e:
            print(f"Error loading map: {e}")
            return None

    def create_map_objects(self, map_data, map_file):
        """Create all game objects from map data"""
        # Clear existing sprites
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.collectibles.empty()
        self.checkpoints.empty()
        self.exits.empty()

        # Create enemies
        if "enemies" in map_data:
            # Create enemies
            for enemy_data in map_data["enemies"]:
                enemy = Enemy(enemy_data)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

        # Create platforms
        if "platforms" in map_data:
            for platform_data in map_data["platforms"]:
                platform = Platform(
                    platform_data["width"],
                    platform_data["height"],
                    platform_data["x"] + platform_data["width"] / 2,
                    platform_data["y"],
                    (255, 0, 0),
                    platform_data["texture"],
                )

                # Add moving platform properties if needed
                if platform_data.get("is_moving", False):
                    platform.is_moving = True
                    movement = platform_data["movement"]
                    platform.movement_type = movement["type"]

                    if movement["type"] == "linear":
                        platform.movement_points = movement["points"]
                        platform.movement_speed = movement["speed"]
                        platform.wait_time = movement.get("wait_time", 0)
                        platform.current_point = 0
                        platform.current_direction = 1
                        platform.wait_counter = 0

                    elif movement["type"] == "circular":
                        platform.center = movement["center"]
                        platform.radius = movement["radius"]
                        platform.angle = 0
                        platform.angular_speed = movement["speed"]
                        platform.clockwise = movement.get("clockwise", True)

                self.platforms.add(platform)
                self.all_sprites.add(platform)

        # Create collectibles (requires Collectible class implementation)
        if "collectibles" in map_data:
            pass  # You'll need to implement collectible creation

        # Create background image
        if "background" in map_data:
            if os.path.isfile(map_data["background"]):
                background = pygame.image.load(map_data["background"]).convert_alpha()
                background = pygame.transform.scale(
                    background, (self.game_resources.WIDTH, self.game_resources.HEIGHT)
                )
                self.background = background
            else:
                print(f"Background image not found: {map_data['background']}")
        else:
            self.background = None

        if "checkpoints" in map_data:
            for checkpoint_data in map_data["checkpoints"]:
                pos = (checkpoint_data["x"], checkpoint_data["y"])
                size = (checkpoint_data["width"], checkpoint_data["height"])
                sprite = checkpoint_data["sprite"]
                checkpoint = Checkpoint(
                    pos, size, texture_path=sprite, map_name=map_file
                )
                self.checkpoints.add(checkpoint)
                self.all_sprites.add(checkpoint)

        if "exits" in map_data:
            for exit_data in map_data["exits"]:
                exit = Exit(
                    exit_data["x"],
                    exit_data["y"],
                    exit_data["width"],
                    exit_data["height"],
                    exit_data["next_level"],
                    exit_data.get("sprite"),
                )
                self.exits.add(exit)
                self.all_sprites.add(exit)

        # Create player at spawn point
        spawn = map_data.get("spawn_point", {"x": 50, "y": 700})
        self.player = Player(self.game_resources)
        self.player.pos.x = spawn["x"]
        self.player.pos.y = spawn["y"]
        self.all_sprites.add(self.player)
