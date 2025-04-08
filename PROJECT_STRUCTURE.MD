# Structure du projet

----
## Vue d'ensemble
Ce projet est un jeu de plateforme 2D développé avec Python et Pygame. Le jeu comprend plusieurs niveaux avec des plateformes fixes et mobiles, des ennemis variés, des collectibles, et un système de progression.
## Organisation des dossiers
```
/
├── src/                                 # Code source principal
│   ├── Menu/                            # Système de menus du jeu
│   │   ├── Menu.py                      # Classe principale du menu
│   │   ├── Button.py                    # Classe de bouton
│   │   ├── Leaderboard.py               # Classe de tableau des scores
│   │   ├── LevelEditorSelectionMenu.py  # Menu de sélection de l'éditeur de niveaux
│   │   └── LevelSelectMenu.py           # Menu de sélection de niveaux
│   ├── Map/                             # Gestion des niveaux
│   │   ├── parser.py                    # Analyseur de fichiers JSON
│   │   ├── Editor/                      # Éditeur de niveaux
│   │   │   ├── LevelEditor.py           # Éditeur de niveaux
│   │   │   └── EditorSprites.py         # Sprites de l'éditeur
│   │   ├── Infinite/                    # Niveaux infinis
│   │   │   ├── InfiniteMapGenerator.py  # Générateur de niveaux infinis
│   │   │   └── InfiniteMapManager.py    # Gestionnaire de niveaux infinis
│   ├── Entity/                          # Entités du jeu
│   │   ├── Entity.py                    # Classe de base pour les entités
│   │   ├── Player.py                    # Joueur
│   │   ├── Enemy.py                     # Ennemis
│   │   ├── Checkpoint.py                # Points de sauvegarde
│   │   ├── Exit.py                      # Sorties de niveau
│   │   ├── Platform.py                  # Plateformes
│   │   ├── Coin.py                      # Pièces
│   │   └── Projectile.py                # Projétiles
│   ├── Database/                        # Gestion de la base de données
│   │   ├── CheckpointDB.py              # Gestion des checkpoints
│   │   └── LevelDB.py                   # Gestion des niveaux
│   ├── Camera.py                        # Gestion de la caméra
│   ├── constant.py                      # Constantes du jeu
│   ├── game.py                          # Fonction principale du jeu
│   └── handler.py                       # Boucle principale du jeu
├── map/                                 # Données des niveaux
│   ├── levels/                          # Fichiers JSON de définition des niveaux
│   │   ├── 1.json                       # Premier niveau
│   │   └── ...
│   └── infinite/                        # Fichiers JSON pour les niveaux infinis
│       ├── uuid.json                    # premier niveau infini (généré)
│       └── ...
├── assets/                              # Ressources graphiques et audio
│   ├── fonts/                           # Polices de caractères
│   │   ├── sanicfont.ttf                # Police de caractères
│   ├── map/
│   │   ├── background/                  # Images de fond
│   │   ├── platform/                    # Textures des plateformes
│   │   ├── enemy/                       # Sprites des ennemis
│   │   ├── collectibles/                # Objets à collecter
│   │   ├── checkpoints/                 # Points de sauvegarde
│   │   └── exit/                        # Sorties de niveau
│   ├── player/                          # Sprites du joueur
│   └── sound/                           # Sons et musique
├── main.py                              # Point d'entrée du jeu
└── requirements.txt                     # Dépendances du projet
```

## Exemple de JSON pour une carte
```JSON
{
  "name": "Level 1",
  "width": 2400,
  "height": 800,
  "background": "assets/map/background/cave_bg.png",
  "gravity": 1.0,
  "platforms": [
    {
      "id": "main_ground",
      "x": -1000,
      "y": 780,
      "width": 1800,
      "height": 200,
      "texture": "assets/map/platform/grass_texture.png"
    },
    {
      "id": "main_ground_2",
      "x": 1000,
      "y": 900,
      "width": 1800,
      "height": 200,
      "texture": "assets/map/platform/stone_texture.png"
    },
    {
      "id": "platform1",
      "x": 300,
      "y": 600,
      "width": 200,
      "height": 20,
      "texture": "assets/map/platform/grass_texture.png",
      "is_moving": false
    },
    {
      "id": "platform2",
      "x": 700,
      "y": 500,
      "width": 150,
      "height": 20,
      "texture": "assets/map/platform/wood_texture.png",
      "is_moving": true,
      "movement": {
        "type": "linear",
        "points": [
          {"x": 700, "y": 300},
          {"x": 700, "y": 600}
        ],
        "speed": 2.0,
        "wait_time": 1.0
      }
    },
    {
      "id": "platform21",
      "x": 1200,
      "y": 750,
      "width": 150,
      "height": 20,
      "texture": "assets/map/platform/grass_texture.png",
      "is_moving": true,
      "movement": {
        "type": "linear",
        "points": [
          {"x": 1200, "y": 550},
          {"x": 1500, "y": 550}
        ],
        "speed": 2.0,
        "wait_time": 1.0
      }
    },
    {
      "id": "platform3",
      "x": 1200,
      "y": 400,
      "width": 100,
      "height": 20,
      "texture": "assets/map/platform/wood_texture.png",
      "is_moving": true,
      "movement": {
        "type": "circular",
        "center": {"x": 1200, "y": 400},
        "radius": 3,
        "speed": 0.02,
        "clockwise": true
      }
    }
  ],

  "enemies": [
    {
      "id": "enemy1",
      "type": "walker",
      "x": 500,
      "y": 660,
      "health": 1,
      "damage": 1,
      "behavior": "patrol",
      "patrol_points": [
        {"x": 400, "y": 660},
        {"x": 600, "y": 660}
      ],
      "speed": 1.5,
      "sprite_sheet": "assets/map/enemy/walker_enemy.png",
      "size": [50,50]
    },
    {
      "id": "enemy2",
      "type": "flyer",
      "x": 1000,
      "y": 400,
      "health": 1,
      "damage": 1,
      "behavior": "chase",
      "detection_radius": 200,
      "speed": 2.0,
      "sprite_sheet": "assets/map/enemy/flying_enemy.png",
      "size": [50,50]
    },
    {
      "id": "enemy3",
      "type": "turret",
      "x": 1500,
      "y": 700,
      "health": 1,
      "damage": 1,
      "behavior": "stationary",
      "attack_interval": 2.0,
      "attack_range": 300,
      "sprite_sheet": "assets/map/enemy/turret.gif",
      "size": [50,100]
    }
  ],

  "collectibles": [
    {
      "id": "coin1",
      "type": "coin",
      "x": 1220,
      "y": 320,
      "sprite": "assets/map/collectibles/Sanic_Coin.png"
    },
    {
      "id": "coin2",
      "type": "coin",
      "x": 400,
      "y": 540,
      "sprite": "assets/map/collectibles/Sanic_Coin.png"
    }
  ],

  "checkpoints": [
    {
      "id": "checkpoint1",
      "x": 1200,
      "y": 760,
      "width": 50,
      "height": 50,
      "sprite": "assets/map/checkpoints/checkpoint.png"
    }
  ],

  "spawn_point": {
    "x": 50,
    "y": 650
  },

  "exits": [
    {
      "x": 2300,
      "y": 700,
      "width": 50,
      "height": 80,
      "next_level": "Level 2",
      "sprite": "assets/map/exit/Zeldo.png"
    }
  ]
}
```
## Technologies utilisées
- Python: Langage de programmation principal
- Pygame: Bibliothèque pour le rendu graphique et la gestion des événements
- JSON: Format de données pour la définition des niveaux
- SQLite (implicite): Pour la sauvegarde de progression