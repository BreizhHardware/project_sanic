import random
import json
import os
import uuid


class InfiniteMapGenerator:
    """Procedural map generator for infinite levels."""

    def __init__(self, game_resources):
        self.game_resources = game_resources
        self.width = 2400
        self.height = 800
        self.backgrounds = [
            "assets/map/background/forest_bg.jpg",
            "assets/map/background/desert_bg.jpg",
            "assets/map/background/mountain_bg.jpg",
            "assets/map/background/cave_bg.png",
        ]
        self.platform_textures = [
            "assets/map/platform/grass_texture.png",
            "assets/map/platform/stone_texture.png",
            "assets/map/platform/wood_texture.png",
        ]

        # Create the directory for infinite maps if it doesn't exist
        os.makedirs("map/infinite", exist_ok=True)

    def generate_map(self, difficulty=1):
        """Generate a new infinite map with the specified difficulty level."""
        map_data = {
            "name": f"Niveau Infini {difficulty}",
            "width": self.width,
            "height": self.height,
            "background": random.choice(self.backgrounds),
            "gravity": 1.0,
            "platforms": self._generate_platforms(difficulty),
            "enemies": self._generate_enemies(difficulty),
            "checkpoints": [],
            "exits": [self._generate_exit()],
            "collectibles": self._generate_collectibles(difficulty),
            "spawn_point": {"x": 260.0, "y": 200.0},
        }

        # Save the map data to a JSON file
        map_id = str(uuid.uuid4())[:8]
        map_path = f"map/infinite/{map_id}.json"

        with open(map_path, "w") as f:
            json.dump(map_data, f, indent=2)

        return map_path

    def _generate_platforms(self, difficulty):
        platforms = []

        # Starting platform
        platforms.append(
            {
                "id": "platform_start",
                "x": 180,
                "y": 260,
                "width": 540,
                "height": 60,
                "texture": random.choice(self.platform_textures),
                "is_moving": False,
            }
        )

        # Generate additional platforms
        num_platforms = 10 + difficulty * 2
        last_x = 600
        for i in range(num_platforms):
            width = random.randint(
                max(40, 100 - difficulty * 5), max(120, 300 - difficulty * 10)
            )
            gap = random.randint(80, 200)
            x = last_x + gap
            y = random.randint(150, 400)

            is_moving = random.random() < min(0.1 + difficulty * 0.05, 0.5)

            platform = {
                "id": f"platform{i+2}",
                "x": x,
                "y": y,
                "width": width,
                "height": random.choice([20, 40, 60]),
                "texture": random.choice(self.platform_textures),
                "is_moving": is_moving,
            }

            if is_moving:
                move_direction = random.choice(["horizontal", "vertical"])
                distance = random.randint(100, 200)

                if move_direction == "horizontal":
                    platform["movement"] = {
                        "type": "linear",
                        "points": [{"x": x, "y": y}, {"x": x + distance, "y": y}],
                        "speed": random.randint(1, 3),
                        "wait_time": 0.5,
                    }
                else:
                    platform["movement"] = {
                        "type": "linear",
                        "points": [{"x": x, "y": y}, {"x": x, "y": y + distance}],
                        "speed": random.randint(1, 3),
                        "wait_time": 0.5,
                    }

            platforms.append(platform)
            last_x = x + width

        return platforms

    def _generate_enemies(self, difficulty):
        enemies = []
        num_enemies = difficulty * 2
        enemy_types = ["walker", "flyer", "turret"]

        for i in range(num_enemies):
            type = random.choice(enemy_types)
            enemy = {
                "id": f"enemy{i+1}",
                "type": type,
                "x": random.randint(600, self.width - 200),
                "y": random.randint(100, 400),
                "patrol_distance": random.randint(100, 300),
            }
            if type == "flyer":
                enemy["sprite_sheet"] = "assets/map/enemy/flying_enemy.png"
                enemy["health"] = 1
                enemy["damage"] = 1
                enemy["behavior"] = "chase"
                enemy["detection_radius"] = random.randint(100, 500)
                enemy["speed"] = 2.0
                enemy["size"] = [50, 50]
            elif type == "walker":
                enemy["sprite_sheet"] = "assets/map/enemy/walker_enemy.png"
                enemy["health"] = 1
                enemy["damage"] = 1
                enemy["behavior"] = "patrol"
                enemy["patrol_points"] = [
                    {"x": enemy["x"], "y": enemy["y"]},
                    {"x": enemy["x"] + enemy["patrol_distance"], "y": enemy["y"]},
                ]
                enemy["speed"] = 1.5
                enemy["size"] = [50, 50]
            elif type == "turret":
                enemy["sprite_sheet"] = "assets/map/enemy/turret.gif"
                enemy["health"] = 1
                enemy["damage"] = 1
                enemy["behavior"] = "stationary"
                enemy["attack_interval"] = random.uniform(0.5, 3.0)
                enemy["attack_range"] = random.randint(100, 500)
                enemy["size"] = [50, 50]
            enemies.append(enemy)

        return enemies

    def _generate_collectibles(self, difficulty):
        collectibles = []
        num_collectibles = 5 + difficulty
        collectible_types = ["coin"]

        for i in range(num_collectibles):
            rand = random.choice(collectible_types)
            if rand == "coin":
                collectible = {
                    "id": f"collectible{i + 1}",
                    "type": "coin",
                    "x": random.randint(400, self.width - 100),
                    "y": random.randint(100, 400),
                    "sprite": "assets/map/collectibles/Sanic_Coin.png",
                }
            else:
                collectible = {
                    "id": f"collectible{i+1}",
                    "type": random.choice(collectible_types),
                    "x": random.randint(400, self.width - 100),
                    "y": random.randint(100, 400),
                }
            collectibles.append(collectible)

        return collectibles

    def _generate_exit(self):
        return {
            "x": self.width - 100,
            "y": 200,
            "width": 50,
            "height": 80,
            "next_level": "NEXT_INFINITE_LEVEL",
            "sprite": "assets/map/exit/Zeldo.png",
        }
