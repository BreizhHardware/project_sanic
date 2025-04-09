# project_sanic

## Installation
Pour installer le jeu, vous devez cloner le dépôt GitHub sur votre ordinateur. Vous pouvez le faire en exécutant la commande suivante dans votre terminal :

```bash
git clone https://github.com/breizhhardware/project_sanic.git
```

Ensuite, vous devez installer les dépendances du jeu. Vous pouvez le faire en exécutant la commande suivante :

```bash
pip install -r requirements.txt
```

## Lancement
Pour lancer le jeu, vous devez exécuter le fichier `main.py` avec Python. Vous pouvez le faire en exécutant la commande suivante :

```bash
python main.py
```

## Création du requierements.txt
Pour créer le fichier `requirements.txt`, vous pouvez exécuter la commande suivante :

```bash
pip freeze > requirements.txt
```

## Concept de Jeu
### Personnage Principal
Nom : Sanic

Apparence : Sanic est un personnage bleu avec des chaussures rouges, des gants blancs, et une attitude dynamique. Il est inspiré de personnages classiques de jeux de plateforme.

Gameplay :

Contrôles : Sanic peut être contrôlé à l'aide des touches ZQSD ou avec une manette. Le jeu est conçu pour être accessible mais aussi pour offrir un défi avec une manette pour les joueurs plus expérimentés.

Capacités : Sanic peut courir, sauter, et utiliser des power-ups pour surmonter les obstacles et vaincre les ennemis.
## Environnement
### Plateformes :

Apparence : Les plateformes sont colorées et variées, rappelant un environnement de fête foraine ou de parc d'attractions.

Types de Plateformes : Il existe différents types de plateformes, certaines fixes et d'autres mouvantes pour ajouter un défi supplémentaire.

Mouvements : Certaines plateformes sont mobiles, nécessitant un timing précis pour éviter les chutes ou les obstacles.

### Ennemis
#### Types d'Ennemis :

Laser : Un canon qui tire des lasers.

Robot : Lance des pièces mécaniques.

Chauve-souris : Vole et peut gêner le joueur sans attaque spécifique.

#### Attaques Spécifiques :

Robot : Lance des pièces mécaniques.

Chauve-souris : Pas d'attaque spécifique mais peut gêner le joueur.

Laser : Tire des lasers.

#### Élimination : 
Les ennemis peuvent être éliminés en utilisant des power-ups ou en sautant sur leur tête.

### Power-ups
#### Types de Power-ups :

Boule de Feu : Un item à récupérer qui permet de lancer des boules de feu.

Dash : Une capacité rechargeable permettant à Sanic de se déplacer rapidement sur une courte distance.

#### Effets :

Boule de Feu : Permet d'attaquer les ennemis à distance.

Dash : Permet d'esquiver rapidement les attaques ou de traverser des obstacles.

Cachettes : Les power-ups peuvent être trouvés en éliminant des ennemis ou en explorant des caves cachées dans le décor.

### Arrière plan

Un seul gros niveau avec une cave au début : Niveau horizontal, puis un niveau vertical de transition qui nous amène vers une forêt qui sera un deuxième niveau horizontal.

## Interface Utilisateur (UI)
Points de Vie : Affichés sous forme de barre de vie en haut de l'écran.

Power-ups Disponibles : Affichés de manière visible pour que le joueur sache quels power-ups sont disponibles et prêts à être utilisés

## Strcture du Projet
La structure du projet est disponible dans le fichier [PROJECT_STRUCTURE](PROJECT_STRUCTURE.MD). Ce fichier contient une description détaillée de l'organisation des fichiers et des dossiers du projet.

## Utilisation des LLM
L'utilisation est détaillé dans le fichier [CHATGPT](CHATGPT.MD).