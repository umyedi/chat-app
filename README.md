# Chat-app

## Aperçu

Pour ce sujet libre, nous avons choisit de réaliser un système de chat en ligne. On pourra envoyer et recevoir des messages avec des utilisateurs et on aura une liste de commande utilisables pour exécuter des actions dans le chat.

## Consignes

-   Sujet libre
-   A réaliser en binome
-   Date de rendu : 5 mars 2024
-   Support de rendu :
    -   Présentation écrite (format numérique) contenant une présentation du travail, des recherches, de la répartition des
        tâches, des idées d'amélioration du projet, des connaissance acquises pendant les recherches...
    -   Facultatif : présentation orale sous forme d'une vidéo (2 min maximum) qui présente le projet
-   Le code doit pouvoir tourner sur les ordi du lycée (éviter d'installer trop de packages)

## Cahier des charges

-   Démarche projet (25 points)
    -   Respect du programme de NSI (POO, récusivité, TAD...)
    -   Idée globale : originalité et créativité
    -   Organisation du travail : composition de l'équipe, rôles et répartition des taches
-   Fonctionnement et opérationnalité (50 points)
    -   Qualité et structure du code
    -   Test et validation / correction des bugs
    -   Qualité de la documentation technique
-   Communication et qualité du dossier (25 points)
    -   Présentation écrite
    -   Présentation orale (facultatif)
    -   Démonstration du projet
    -   Respect des consignes

## Code

### Arborescence

```bash
.
├── classes.png
├── client                           # Fichiers relatifs au client
│   ├── application.py               # Gère l'interface graphique
│   ├── client.py                    # Gère la transmission des données entre le serveur et le client
│   ├── design                       # Fichiers d'interfaces
│   │   ├── application.ui
│   │   ├── documentation.ui
│   │   └── server.ui
│   ├── dialogs.py                   # Gère les pop-up de la toolbar de l'application
│   ├── download.py                  # Gère le téléchargement d'images
│   ├── fonts                        # Polices d'écritures
│   │   ├── SpaceMono-Bold.ttf
│   │   └── SpaceMono-Regular.ttf
│   ├── images                       # Images téléchargées par 'downloads.py'
│   │   ├── 2024-03-03_10-20-03.png
│   │   └── 2024-03-03_10-34-27.png
│   ├── main.py                      # Code exécutable pour démarrer l'application
│   └── resources                    # Ressources graphiques de l'application
│       └── icon.ico
├── README.md                        # Documentation
├── requirements.txt                 # Librairies nécessaire pour exécuter le code
├── server                           # Fichiers relatifs au serveur
│   ├── api                          # Fichiers relatif aux APIs
│   │   ├── api.py                   # Contient les fonctions créees à partir des APIs
│   │   └── credentials.json         # Contient les tokens d'API
│   ├── chatroom.py                  # Gère les salons de chat
│   ├── commands.py                  # Gère les commandes exécutables par l'utilisateur
│   ├── data                         # Données du serveur
│   │   └── server.log               # Historique des actions du serveur
│   ├── games.py                     # Gère les jeux auquel l'utilisateur peut jouer
│   ├── log.py                       # Gère la manière dont les logs sont gérés
│   ├── main.py                      # Code exécutable pour démarrer le serveur
│   ├── message.py                   # Gère les messages
│   ├── server.py                    # Code principal du serveur
│   └── user.py                      # Gère les utilisateurs
└── tests                            # Contient les unitées de test
    ├── test_chatroom.py
    ├── test_games.py
    ├── test_message.py
    └── test_user.py
```

### Classes

Voici la représentation des liens entre les différentes classes du projet.

![Python classes preview](resources/classes.png)

## Installation Windows

### Généralitées

Ce projet gère des relation client/serveur avec le module `zmq`, il est donc impératif de vérifier qu'il n'y ait pas
d'antivirus bloquant les connexion sortantes/entrantes de l'application. L'antivirus par défault de Windows ne bloquera
normalement pas le programme.

Pour simplement tester l'application, il est possible d'exécuter la version exécutable du code.

Pour interpréter le code suivez les étapes suivantes.

Vérifiez que vous avez la dernière version de Python (que vous pouvez télécharger 
[ici](https://www.python.org/downloads/)) et que pip est à jour (en exécutant `python -m pip install --upgrade pip`).

Pour contenir les packages, il est préférable de mettre en place un environnement virtuel avec Python. Cela permettera
d'installer les packages nécessaires uniquement pour ce projet. Pour cela, ouvrez un terminal (en administrateur) dans
le dossier contenant le repository et exécutez les commandes suivantes :

#### Création de l'environnement virtuel

```bash
python -m venv .venv
```

#### Activation de l'environnement virtuel

```bash
.venv\Scripts\activate.bat
```

On peut désormais installer les packages requis avec la commande suivante :

```bash
pip install -r requirements.txt
```

Une fois l'installation terminée, vous pouvez maintenant exécuter l'application client ou le serveur selon votre choix
avec les commandes suivantes :

#### Serveur

```bash
cd server
python server.py
```

#### Application client

Veillez à spécifier la bonne IP et le bon port du server dans `application.py`. Si le serveur tourne sur la même machine
que le client, l'IP du serveur est `localhost`.

```bash
cd client
python application.py
```
