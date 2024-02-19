"""

Ce fichier contient les fonctions basiques pour le serveur.

"""

import json
from datetime import datetime


def get_current_time():
    return datetime.now().strftime("%d/%m/%y-%H:%M:%S")


def get_database(database: str):
    with open(database, "r", encoding="utf-8") as file:
        return json.load(file)


def write_database(database: str, data: str):
    with open(database, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def get_game_status(user_id, game_id):
    data = get_database(f"games/game_{game_id}.json")

    for i in range(1, 5):
        if data["status"][f"user{i}-deck"]["user-id"] != user_id:
            del data["status"][f"user{i}-deck"]
        if data["users"][f"user{i}"]["user-id"] != user_id:
            del data["users"][f"user{i}"]["user-id"]

    return {"status": "success", "result": data}
