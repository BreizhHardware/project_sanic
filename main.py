import re

import pygame
import sys
from pygame.locals import *
import numpy as np

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
    handler()


if __name__ == "__main__":
    main()
