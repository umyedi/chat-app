# Chat-app

## Aperçu

Pour ce sujet libre, nous avons choisit de réaliser un chatbot. On pourra envoyer et recevoir des messages avec des utilisateurs ou des bots avec qui on pourra jouer à des jeux simples comme Pierre-Feuille-Ciseaux.

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
├── client/                      # Contient les fichiers relatifs à la partie cliente de l'application
│   ├── application.py           # Point d'entrée de l'application client, gère l'interface utilisateur
│   ├── client.py                # Gère la logique de connexion et la communication avec le serveur
│   └── worker.py                # Implémente la récupération de données en arrière plan
├── design/                      # Contient les fichiers de design d'interface utilisateur (Qt Designer)
│   └── application.ui           # Interface de l'application client
├── server/                      # Contient les fichiers relatifs à la partie serveur de l'application
│   ├── api/                     # Dossier pour les clés d'API et autres configurations spécifiques à l'API
│   │   ├── keys.json            # Stocke les clés d'API et les tokens
│   │   └── api_manager.py       # Gère l'authentification et les fonction relatives aux API
│   ├── sessions/                # Dossier pour stocker les données de session
│   │   └── foo.json             # Exemple de fichier de données de session
│   ├── actions.py               # Définit les actions que le serveur peut exécuter en réponse aux requêtes client
│   ├── commands.py              # Traite les commandes reçues du client et déclenche les actions correspondantes
│   ├── filters.py               # Contient des fonctions de filtrage des sessions
│   ├── log.py                   # Configuration et gestion des logs pour enregistrer les activités du serveur
│   ├── server.log               # Fichier de log où sont enregistrées les activités du serveur
│   ├── server.py                # Point d'entrée du serveur, initialise le serveur et écoute les requêtes client
│   └── utils.py                 # Fonctions utilitaires communes à tous les fichiers du server
├── README.md                    # Documentation du repository
└── requirements.txt             # Liste toutes les dépendances Python (pip) nécessaires pour exécuter l'application
```

### Classes

![alt text](/ressources/schema.png)

## Installation Windows

### Généralitées

Ce projet gère des relation client/serveur avec le module `zmq`, il est donc impératif de vérifier qu'il n'y ait pas
d'antivirus bloquant les connexion sortantes/entrantes de l'application.

Pour installer le code tel quel, vérifiez que vous avez la dernière version de Python (que vous pouvez télécharger
[ici](https://www.python.org/downloads/)) et que pip est à jour (en exécutant `python -m pip install --upgrade pip`).

Pour contenir les packages, il est préférable de mettre en place un environnement virtuel avec Python. Pour cela, ouvrez
un terminal (en administrateur) dans le dossier contenant le repository et exécutez les commandes suivantes :

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

