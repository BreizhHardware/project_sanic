import os
import json
import glob
from src.Map.Infinite.InfiniteMapGenerator import InfiniteMapGenerator


class InfiniteMapManager:
    """Handle infinite map generation and management."""

    def __init__(self, game_resources):
        self.game_resources = game_resources
        self.map_generator = InfiniteMapGenerator(game_resources)
        self.current_level = 0
        self.active_maps = []
        self.difficulty = 1

    def start_infinite_mode(self):
        """Start the infinite mode by generating the first two maps."""
        self._clean_old_maps()

        # Generate the first two maps
        first_map = self.map_generator.generate_map(difficulty=self.difficulty)
        second_map = self.map_generator.generate_map(difficulty=self.difficulty)

        # Configure the first map to point to the second map
        self._update_exit_target(first_map, second_map)

        self.active_maps = [first_map, second_map]
        self.current_level = 1

        return first_map

    def advance_to_next_level(self):
        """Progress to the next level in infinite mode and delete the previous one."""
        # Delete the oldest map
        if self.active_maps:
            old_map = self.active_maps.pop(0)
            try:
                os.remove(old_map)
            except:
                print(f"Erreur: Impossible de supprimer {old_map}")

        # Up the difficulty every 3 levels
        self.current_level += 1
        if self.current_level % 3 == 0:
            self.difficulty = min(10, self.difficulty + 1)

        # Generate a new map
        new_map = self.map_generator.generate_map(difficulty=self.difficulty)

        # Update the exit target of the last map to point to the new one
        if self.active_maps:
            self._update_exit_target(self.active_maps[0], new_map)

        self.active_maps.append(new_map)

        return self.active_maps[0]

    def _update_exit_target(self, map_path, next_map_path):
        """Update the exit of the current map to point to the next map."""
        try:
            with open(map_path, "r") as f:
                map_data = json.load(f)

            if "exits" in map_data and map_data["exits"]:
                for exit_obj in map_data["exits"]:
                    exit_obj["next_level"] = next_map_path

            with open(map_path, "w") as f:
                json.dump(map_data, f, indent=2)

        except Exception as e:
            print(f"Error while updating exit: {e}")

    def _clean_old_maps(self):
        """Delete all old infinite maps."""
        map_files = glob.glob("map/infinite/*.json")
        for file in map_files:
            try:
                os.remove(file)
            except:
                print(f"Error: Unable to delete {file}")
