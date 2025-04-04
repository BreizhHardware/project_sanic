import pygame
import os
import json
from pygame.locals import *

from src.Entity.Platform import Platform
from src.Menu.Button import Button
from src.Map.parser import MapParser
from src.Map.Editor.EditorSprites import (
    EditorPlatform,
    EditorCheckpoint,
    EditorEnemy,
    EditorExit,
    EditorCollectible,
)


class LevelEditor:
    """
    A graphical level editor for creating and modifying game levels.
    Allows placing and configuring game elements and saving to JSON files.
    """

    def __init__(self, game_resources, level_file=None):
        """Initialize the level editor."""
        self.game_resources = game_resources
        self.level_file = level_file
        self.grid_size = 20  # Grid size for snapping

        # Initialize level data
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.checkpoints = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.player_start = None
        self.exit_point = None

        # UI elements
        self.buttons = []
        self.tools = [
            "select",
            "player",
            "platform",
            "enemy",
            "checkpoint",
            "exit",
            "collectible",
        ]
        self.current_tool = "select"
        self.selected_object = None

        # For creating platforms
        self.start_pos = None
        self.creating = False

        # For moving objects
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        # For platform properties
        self.platform_moving = False
        self.platform_speed = 2
        self.platform_direction = "horizontal"
        self.platform_distance = 100

        # For collectible properties
        self.collectible_type = "coin"

        # Create toolbar buttons
        self._create_toolbar()

        # Load level if specified
        if level_file:
            self._load_level(level_file)

        self.panning = False
        self.pan_start_pos = None
        self.camera_offset = [0, 0]

        self.platform_textures = [
            "assets/map/platform/grass_texture.png",
            "assets/map/platform/stone_texture.png",
            "assets/map/platform/wood_texture.png",
        ]
        self.backgrounds = [
            "assets/map/background/forest_bg.jpg",
            "assets/map/background/desert_bg.jpg",
            "assets/map/background/mountain_bg.jpg",
            "assets/map/background/cave_bg.png",
        ]
        self.background = self.backgrounds[0]

    def _create_toolbar(self):
        """Create buttons for the editor toolbar"""
        # Tool selection buttons
        button_width = 100
        button_height = 30
        x = 10
        y = 10

        for tool in self.tools:
            self.buttons.append(
                Button(
                    tool.capitalize(),
                    x,
                    y,
                    button_width,
                    button_height,
                    {"action": "select_tool", "tool": tool},
                )
            )
            y += button_height + 5

        # Save and exit buttons
        self.buttons.append(
            Button(
                "Save",
                10,
                self.game_resources.HEIGHT - 70,
                button_width,
                button_height,
                "save_level",
            )
        )

        self.buttons.append(
            Button(
                "Exit",
                10,
                self.game_resources.HEIGHT - 35,
                button_width,
                button_height,
                "exit_editor",
            )
        )

    def _load_level(self, level_file):
        """Load an existing level for editing"""
        parser = MapParser(self.game_resources)
        map_objects = parser.load_map(level_file)

        if not map_objects:
            return

        # Convert loaded platforms to editor platforms
        if "platforms" in map_objects:
            for platform in map_objects["platforms"]:
                editor_platform = EditorPlatform(
                    platform.rect.width,
                    platform.rect.height,
                    platform.rect.x,
                    platform.rect.y,
                )

                # Transfer movement properties if any
                if hasattr(platform, "moving") and platform.moving:
                    editor_platform.moving = platform.moving
                    editor_platform.direction = platform.direction
                    editor_platform.speed = platform.speed
                    editor_platform.distance = platform.distance

                self.platforms.add(editor_platform)
                self.all_sprites.add(editor_platform)

        # Set player start position
        if "player" in map_objects and map_objects["player"]:
            self.player_start = map_objects["player"].pos

        # Convert checkpoints
        if "checkpoints" in map_objects:
            for checkpoint in map_objects["checkpoints"]:
                editor_checkpoint = EditorCheckpoint(
                    checkpoint.rect.x, checkpoint.rect.y
                )
                self.checkpoints.add(editor_checkpoint)
                self.all_sprites.add(editor_checkpoint)

        # Handle exits
        if "exits" in map_objects and map_objects["exits"]:
            exits_sprites = list(map_objects["exits"])
            if exits_sprites:
                exit_sprite = exits_sprites[0]
                self.exit_point = EditorExit(
                    exit_sprite.rect.x,
                    exit_sprite.rect.y,
                    exit_sprite.rect.width,
                    exit_sprite.rect.height,
                )
                self.all_sprites.add(self.exit_point)

        # Load enemies
        if "enemies" in map_objects:
            for enemy in map_objects["enemies"]:
                editor_enemy = EditorEnemy(
                    self.game_resources, enemy.rect.x, enemy.rect.y
                )
                if hasattr(enemy, "enemy_type"):
                    editor_enemy.enemy_type = enemy.enemy_type

                self.enemies.add(editor_enemy)
                self.all_sprites.add(editor_enemy)

    def _snap_to_grid(self, pos):
        """Snap a position to the grid"""
        world_pos = self.screen_to_world(pos)
        x, y = world_pos
        return (
            round(x / self.grid_size) * self.grid_size,
            round(y / self.grid_size) * self.grid_size,
        )

    def save_level(self):
        """Save the level to a JSON file"""
        if not self.level_file:
            # If no file specified, create a new one
            level_dir = "map/levels/"
            # Find the next available level number
            existing_levels = [
                int(f.split(".")[0])
                for f in os.listdir(level_dir)
                if f.endswith(".json") and f.split(".")[0].isdigit()
            ]
            new_level_num = 1 if not existing_levels else max(existing_levels) + 1
            self.level_file = f"{level_dir}{new_level_num}.json"

        # Name of the level based on the file name
        level_name = f"Level {self.level_file.split('/')[-1].split('.')[0]}"

        level_data = {
            "name": level_name,
            "width": 2400,
            "height": 800,
            "background": self.background,
            "gravity": 1.0,
            "platforms": [],
            "enemies": [],
            "checkpoints": [],
            "exits": [],
            "collectibles": [],
            "spawn_point": {
                "x": self.player_start.x if self.player_start else 100,
                "y": self.player_start.y if self.player_start else 100,
            },
        }

        # Add platforms
        for i, platform in enumerate(self.platforms):
            platform_data = {
                "id": f"platform{i + 1}",
                "x": platform.rect.x,
                "y": platform.rect.y,
                "width": platform.rect.width,
                "height": platform.rect.height,
                "texture": platform.texture,
                "is_moving": False,
            }

            # Add movement data if platform moves
            if hasattr(platform, "moving") and platform.moving:
                platform_data["is_moving"] = True

                if platform.direction == "horizontal":
                    platform_data["movement"] = {
                        "type": "linear",
                        "points": [
                            {"x": platform.rect.x, "y": platform.rect.y},
                            {
                                "x": platform.rect.x + platform.distance,
                                "y": platform.rect.y,
                            },
                        ],
                        "speed": platform.speed,
                        "wait_time": 1.0,
                    }
                else:  # vertical
                    platform_data["movement"] = {
                        "type": "linear",
                        "points": [
                            {"x": platform.rect.x, "y": platform.rect.y},
                            {
                                "x": platform.rect.x,
                                "y": platform.rect.y + platform.distance,
                            },
                        ],
                        "speed": platform.speed,
                        "wait_time": 1.0,
                    }

            level_data["platforms"].append(platform_data)

        # Add collectibles
        for i, collectible in enumerate(self.collectibles):
            collectible_data = {
                "id": f"collectible{i + 1}",
                "type": collectible.collectible_type,
                "x": collectible.rect.x,
                "y": collectible.rect.y,
                "sprite": f"assets/map/collectibles/{collectible.collectible_type}.png",
            }

            # Add specific attributes based on type
            if collectible.collectible_type == "coin":
                collectible_data["value"] = 10
            elif collectible.collectible_type == "speed_boost":
                collectible_data["duration"] = 5.0

            level_data["collectibles"].append(collectible_data)

        # Add checkpoints
        for i, checkpoint in enumerate(self.checkpoints):
            level_data["checkpoints"].append(
                {
                    "id": f"checkpoint{i + 1}",
                    "x": checkpoint.rect.x,
                    "y": checkpoint.rect.y,
                    "width": 50,
                    "height": 50,
                    "sprite": "assets/map/checkpoints/checkpoint.png",
                }
            )

        # Add exit
        if self.exit_point:
            next_level_num = int(self.level_file.split("/")[-1].split(".")[0]) + 1
            next_level = f"Level {next_level_num}"

            level_data["exits"].append(
                {
                    "x": self.exit_point.rect.x,
                    "y": self.exit_point.rect.y,
                    "width": 50,
                    "height": 80,
                    "next_level": getattr(self.exit_point, "next_level", next_level),
                    "sprite": "assets/map/exit/Zeldo.png",
                }
            )

        # Add enemies
        for i, enemy in enumerate(self.enemies):
            enemy_type = getattr(enemy, "enemy_type", "walker")
            enemy_data = {
                "id": f"enemy{i + 1}",
                "type": enemy_type,
                "x": enemy.rect.x,
                "y": enemy.rect.y,
                "health": 1,
                "damage": 1,
                "sprite_sheet": f"assets/map/enemy/{enemy_type}_enemy.png",
            }

            if enemy_type == "walker":
                enemy_data["behavior"] = "patrol"
                enemy_data["patrol_points"] = [
                    {"x": enemy.rect.x - 100, "y": enemy.rect.y},
                    {"x": enemy.rect.x + 100, "y": enemy.rect.y},
                ]
                enemy_data["speed"] = 1.5
            elif enemy_type == "flyer":
                enemy_data["behavior"] = "chase"
                enemy_data["detection_radius"] = 200
                enemy_data["speed"] = 2.0
            elif enemy_type == "turret":
                enemy_data["behavior"] = "stationary"
                enemy_data["attack_interval"] = 2.0
                enemy_data["attack_range"] = 300

            level_data["enemies"].append(enemy_data)

        # Save to file
        try:
            with open(self.level_file, "w") as f:
                json.dump(level_data, f, indent=2)
            print(f"Level saved to {self.level_file}")
            return True
        except Exception as e:
            print(f"Error saving level: {e}")
            return False

    def handle_event(self, event):
        """
        Handle user input events.

        Args:
            event: Pygame event to process

        Returns:
            str/dict/None: Action to perform based on user interaction, or None
        """
        # Check for CTRL+S to save
        if (
            event.type == KEYDOWN
            and event.key == K_s
            and pygame.key.get_mods() & KMOD_CTRL
        ):
            self.save_level()
            return None

        # Check UI button clicks
        for button in self.buttons:
            action = button.handle_event(event)
            if action:
                if action == "save_level":
                    self.save_level()
                    return None
                elif action == "exit_editor":
                    return "back_to_levels"
                elif isinstance(action, dict) and action.get("action") == "select_tool":
                    self.current_tool = action.get("tool")
                    self.selected_object = None
                    self.creating = False
                return None

        # Handle mouse actions based on current tool
        if event.type == MOUSEBUTTONDOWN:
            pos = self._snap_to_grid(pygame.mouse.get_pos())

            # Select object
            if self.current_tool == "select":
                self.selected_object = None
                for sprite in self.all_sprites:
                    if sprite.rect.collidepoint(event.pos):
                        self.selected_object = sprite
                        self.dragging = True
                        self.offset_x = sprite.rect.x - event.pos[0]
                        self.offset_y = sprite.rect.y - event.pos[1]
                        break

            # Place player start point
            elif self.current_tool == "player":
                self.player_start = self.game_resources.vec(pos[0], pos[1])

            # Start creating platform
            elif self.current_tool == "platform":
                self.creating = True
                self.start_pos = pos

            # Place checkpoint
            elif self.current_tool == "checkpoint":
                checkpoint = EditorCheckpoint(pos[0], pos[1])
                self.checkpoints.add(checkpoint)
                self.all_sprites.add(checkpoint)

            # Place exit
            elif self.current_tool == "exit":
                if self.exit_point:
                    self.all_sprites.remove(self.exit_point)
                self.exit_point = EditorExit(pos[0], pos[1], 50, 50)
                self.all_sprites.add(self.exit_point)

            # Place enemy
            elif self.current_tool == "enemy":
                enemy = EditorEnemy(self.game_resources, pos[0], pos[1])
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

            # Place collectible
            elif self.current_tool == "collectible":
                collectible = EditorCollectible(pos[0], pos[1], self.collectible_type)
                self.collectibles.add(collectible)
                self.all_sprites.add(collectible)

        # Handle mouse movement during platform creation or object dragging
        elif event.type == MOUSEMOTION:
            if self.dragging and self.selected_object:
                pos = self._snap_to_grid(
                    (event.pos[0] + self.offset_x, event.pos[1] + self.offset_y)
                )
                self.selected_object.rect.x = pos[0]
                self.selected_object.rect.y = pos[1]

                # Update position attribute if exists
                if hasattr(self.selected_object, "pos"):
                    self.selected_object.pos.x = pos[0]
                    self.selected_object.pos.y = pos[1]

        # Finish creating object or stop dragging
        elif event.type == MOUSEBUTTONUP:
            if self.creating and self.current_tool == "platform":
                end_pos = self._snap_to_grid(pygame.mouse.get_pos())
                width = abs(end_pos[0] - self.start_pos[0])
                height = abs(end_pos[1] - self.start_pos[1])

                # Ensure minimum size
                width = max(width, 20)
                height = max(height, 20)

                x = min(self.start_pos[0], end_pos[0])
                y = min(self.start_pos[1], end_pos[1])

                platform = EditorPlatform(width, height, x, y)
                self.platforms.add(platform)
                self.all_sprites.add(platform)
                self.selected_object = platform

            self.creating = False
            self.dragging = False

        # Handle keyboard controls for platform properties
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE and self.selected_object:
                # Vérifier que l'objet est bien dans les groupes avant de le supprimer
                if self.selected_object in self.all_sprites:
                    self.all_sprites.remove(self.selected_object)
                if isinstance(self.selected_object, EditorPlatform):
                    if self.selected_object in self.platforms:
                        self.platforms.remove(self.selected_object)
                elif isinstance(self.selected_object, EditorCheckpoint):
                    self.checkpoints.remove(self.selected_object)
                elif isinstance(self.selected_object, EditorEnemy):
                    self.enemies.remove(self.selected_object)
                elif isinstance(self.selected_object, EditorCollectible):
                    self.collectibles.remove(self.selected_object)
                elif self.selected_object == self.exit_point:
                    self.exit_point = None
                self.selected_object = None

            if event.key == K_b:
                try:
                    current_index = self.backgrounds.index(self.background)
                except ValueError:
                    current_index = 0

                next_index = (current_index + 1) % len(self.backgrounds)
                self.background = self.backgrounds[next_index]
                print(f"Background set to: {self.background}")

            if self.selected_object and isinstance(
                self.selected_object, EditorPlatform
            ):
                if event.key == K_m:  # Toggle movement
                    if not hasattr(self.selected_object, "moving"):
                        self.selected_object.moving = True
                        self.selected_object.direction = "horizontal"
                        self.selected_object.speed = 2
                        self.selected_object.distance = 100
                        self.selected_object.start_pos = self.game_resources.vec(
                            self.selected_object.rect.x, self.selected_object.rect.y
                        )
                    else:
                        self.selected_object.moving = not self.selected_object.moving

                elif event.key == K_d:  # Toggle direction
                    if (
                        hasattr(self.selected_object, "moving")
                        and self.selected_object.moving
                    ):
                        self.selected_object.direction = (
                            "vertical"
                            if self.selected_object.direction == "horizontal"
                            else "horizontal"
                        )

                elif event.key == K_UP:  # Increase speed
                    if (
                        hasattr(self.selected_object, "moving")
                        and self.selected_object.moving
                    ):
                        self.selected_object.speed += 0.5

                elif event.key == K_DOWN:  # Decrease speed
                    if (
                        hasattr(self.selected_object, "moving")
                        and self.selected_object.moving
                    ):
                        self.selected_object.speed = max(
                            0.5, self.selected_object.speed - 0.5
                        )

                elif event.key == K_RIGHT:  # Increase distance
                    if (
                        hasattr(self.selected_object, "moving")
                        and self.selected_object.moving
                    ):
                        self.selected_object.distance += 20

                elif event.key == K_LEFT:  # Decrease distance
                    if (
                        hasattr(self.selected_object, "moving")
                        and self.selected_object.moving
                    ):
                        self.selected_object.distance = max(
                            20, self.selected_object.distance - 20
                        )

                elif event.key == K_p:
                    current_texture = self.selected_object.texture
                    try:
                        current_index = self.platform_textures.index(current_texture)
                    except ValueError:
                        current_index = 0

                    next_index = (current_index + 1) % len(self.platform_textures)
                    self.selected_object.texture = self.platform_textures[next_index]
                    self.selected_object.update_appearance()
                    print(f"Platform texture set to: {self.selected_object.texture}")

            elif self.selected_object and isinstance(
                self.selected_object, EditorCollectible
            ):
                if event.key == K_t:
                    types = ["coin", "speed_boost", "health", "shield"]
                    current_index = (
                        types.index(self.selected_object.collectible_type)
                        if self.selected_object.collectible_type in types
                        else 0
                    )
                    next_index = (current_index + 1) % len(types)
                    self.selected_object.collectible_type = types[next_index]

                    # Update appearance based on type
                    if self.selected_object.collectible_type == "coin":
                        self.selected_object.image.fill((255, 215, 0))  # Gold
                    elif self.selected_object.collectible_type == "speed_boost":
                        self.selected_object.image.fill((0, 0, 255))  # Blue
                    elif self.selected_object.collectible_type == "health":
                        self.selected_object.image.fill((255, 0, 0))  # Red
                    elif self.selected_object.collectible_type == "shield":
                        self.selected_object.image.fill((128, 128, 128))  # Gray

            elif self.selected_object and isinstance(self.selected_object, EditorExit):
                if event.key == K_n:
                    # Navigation between levels
                    level_dir = "map/levels/"
                    levels = [f for f in os.listdir(level_dir) if f.endswith(".json")]

                    if not hasattr(
                        self.selected_object, "next_level"
                    ) or self.selected_object.next_level not in [
                        level_dir + l for l in levels
                    ]:
                        self.selected_object.next_level = (
                            level_dir + levels[0] if levels else "map/levels/1.json"
                        )
                    else:
                        current_index = levels.index(
                            self.selected_object.next_level.replace(level_dir, "")
                        )
                        next_index = (current_index + 1) % len(levels)
                        self.selected_object.next_level = level_dir + levels[next_index]

                    print(f"Next level set to: {self.selected_object.next_level}")

            elif self.selected_object and isinstance(self.selected_object, EditorEnemy):
                if event.key == K_t:
                    types = ["walker", "flyer", "turret"]
                    current_index = (
                        types.index(self.selected_object.enemy_type)
                        if self.selected_object.enemy_type in types
                        else 0
                    )
                    next_index = (current_index + 1) % len(types)
                    self.selected_object.enemy_type = types[next_index]
                    self.selected_object.update_appearance()
                    print(f"Enemy type set to: {self.selected_object.enemy_type}")

        if event.type == MOUSEBUTTONDOWN and event.button == 3:
            self.panning = True
            self.pan_start_pos = event.pos
            return None

        elif event.type == MOUSEMOTION and self.panning:
            dx = event.pos[0] - self.pan_start_pos[0]
            dy = event.pos[1] - self.pan_start_pos[1]

            self.camera_offset[0] += dx
            self.camera_offset[1] += dy

            self.pan_start_pos = event.pos
            return None

        elif event.type == MOUSEBUTTONUP and event.button == 3:
            self.panning = False
            return None

        return None

    def draw(self, surface):
        """
        Draw the level editor and all its elements.

        Args:
            surface: Pygame surface to draw on
        """
        # Clear the screen
        surface.fill((40, 40, 40))

        # Draw grid with camera offset
        for x in range(
            -self.camera_offset[0] % self.grid_size,
            self.game_resources.WIDTH,
            self.grid_size,
        ):
            pygame.draw.line(
                surface, (60, 60, 60), (x, 0), (x, self.game_resources.HEIGHT)
            )
        for y in range(
            -self.camera_offset[1] % self.grid_size,
            self.game_resources.HEIGHT,
            self.grid_size,
        ):
            pygame.draw.line(
                surface, (60, 60, 60), (0, y), (self.game_resources.WIDTH, y)
            )

        # Draw all sprites
        for sprite in self.all_sprites:
            screen_pos = self.world_to_screen((sprite.rect.x, sprite.rect.y))
            temp_rect = sprite.rect.copy()
            temp_rect.x, temp_rect.y = screen_pos
            surface.blit(sprite.image, temp_rect)

        # Draw player start position
        if self.player_start:
            screen_pos = self.world_to_screen(
                (self.player_start.x, self.player_start.y)
            )
            pygame.draw.circle(
                surface,
                (0, 255, 0),
                (int(screen_pos[0]), int(screen_pos[1])),
                10,
            )

        # Draw outline for selected object
        if self.selected_object:
            pygame.draw.rect(surface, (255, 255, 0), self.selected_object.rect, 2)

            # Show properties for selected platform
            if isinstance(self.selected_object, EditorPlatform):
                info_text = [
                    f"Size: {self.selected_object.rect.width}x{self.selected_object.rect.height}",
                    f"Pos: ({self.selected_object.rect.x}, {self.selected_object.rect.y})",
                ]

                if (
                    hasattr(self.selected_object, "moving")
                    and self.selected_object.moving
                ):
                    info_text.extend(
                        [
                            f"Moving: Yes",
                            f"Direction: {self.selected_object.direction}",
                            f"Speed: {self.selected_object.speed}",
                            f"Distance: {self.selected_object.distance}",
                        ]
                    )
                else:
                    info_text.append("Moving: No")

                y_offset = 20
                for text in info_text:
                    text_surf = self.game_resources.font.render(
                        text, True, (255, 255, 255)
                    )
                    x_pos = self.game_resources.WIDTH - text_surf.get_width() - 10
                    surface.blit(text_surf, (x_pos, y_offset))
                    y_offset += 25

        # Draw platform being created
        if self.creating and self.current_tool == "platform":
            start_pos = self.start_pos
            end_pos = self._snap_to_grid(pygame.mouse.get_pos())
            rect = pygame.Rect(
                min(start_pos[0], end_pos[0]),
                min(start_pos[1], end_pos[1]),
                abs(end_pos[0] - start_pos[0]) or self.grid_size,
                abs(end_pos[1] - start_pos[1]) or self.grid_size,
            )
            pygame.draw.rect(surface, (0, 150, 255), rect, 2)

        # Draw UI buttons
        for button in self.buttons:
            button.draw(surface, self.game_resources.font)

        # Draw current tool indicator
        tool_text = f"Current Tool: {self.current_tool.capitalize()}"
        tool_surf = self.game_resources.font.render(tool_text, True, (255, 255, 255))
        surface.blit(tool_surf, (self.game_resources.WIDTH - 250, 10))

        # Draw help text
        help_text = [
            "Controls:",
            "CTRL+S: Save level",
            "DEL: Delete selected object",
            "For platforms:",
            "  M: Toggle movement",
            "  D: Toggle direction",
            "  Arrow keys: Adjust speed/distance",
            "  P: Change texture",
            "For collectibles:",
            "  T: Change type",
            "Pour les sorties:",
            "  N: Changer le niveau suivant",
            "Pour les ennemis:",
            "  T: Changer le type d'ennemi",
            "B: Change background",
        ]

        y_offset = self.game_resources.HEIGHT - 300
        for text in help_text:
            text_surf = self.game_resources.font.render(text, True, (200, 200, 200))
            surface.blit(text_surf, (self.game_resources.WIDTH - 250, y_offset))
            y_offset += 20

    def world_to_screen(self, pos):
        """Convert world coordinates to screen coordinates."""
        return pos[0] + self.camera_offset[0], pos[1] + self.camera_offset[1]

    def screen_to_world(self, pos):
        """Convert screen coordinates to world coordinates."""
        return pos[0] - self.camera_offset[0], pos[1] - self.camera_offset[1]
