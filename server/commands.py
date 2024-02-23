from datetime import datetime
from utils import *


class Commands:
    def __init__(self, username: str, database_path: str) -> None:

        self.database_path = database_path
        self.data = read_json(database_path)

        self.username = username
        self.usernames = [user["username"] for user in self.data["users"].values()]

        self.commands_list = {
            "/help": self.help,
            "/time": self.time,
            "/games": self.games,
            "/invite": self.invite,
            "/accept": self.accept,
            "/play": self.play,
        }

        self.commands_description = {
            "/help": "List all the commands.",
            "/time": "Displays current time.",
            "/games": "Displays the games available",
            "/invite [game] [username]": "Invite a user to play a game.",
        }

        self.games_description = {"rps": "Rock Paper Scissors."}

    def is_command(self, command: str) -> bool:
        return command[0] == "/"

    def execute_command(self, command: str) -> None:
        command = command.split()
        args = command[1:]
        command = command[0]

        if command not in self.commands_list:
            self.data["chat_history"][get_current_time()] = self.format_message(content=f"The command '{command}' doesn't exists.")
        else: 
            return_message = self.commands_list[command](*args)
            self.data["chat_history"][get_current_time()] = return_message

        write_json(self.database_path, self.data)

    def format_message(self, username: str = "system", public: bool = False, content: str = None, viewers: list = None):
        if viewers is None:
            viewers = [self.username]
        return {"username": username, "public": public, "content": content, "viewers": viewers}

    def help(self, *args):
        content = "".join(f"\n\t{cmd} - {self.commands_description[cmd]}" for cmd in self.commands_description)
        return self.format_message(content=content)

    def time(self, *args):
        return self.format_message(content=f"It's {datetime.now().strftime('%I:%M %p')}.")

    def games(self, *args):
        content = "".join(f"{game} - {self.games_description[game]}" for game in self.games_description)
        return self.format_message(content=content)

    def invite(self, *args):

        if len(args) != 2:
            return self.format_message(content="Invalid number of options. You should run '/invite [game] [user]'.")

        game = args[0]
        opponent = args[1]

        if game not in self.games_description:
            return self.format_message(content=f"The game '{game}' doesn't exists. Run '/games' to see the list of the games available.")

        if opponent not in self.usernames:
            return self.format_message(content=f"The user '{opponent}' isn't connected.")

        if self.data["game"]["status"] not in ["stopped", ""]: # If no game is still running
            content = f"The game {self.data['game']['name']} is still running. The host of the game should run '/end {self.data['game']['name']}' to end the game."
            return self.format_message(content=content)

        self.data["game"] = {
            "name": game,
            "host": self.username,
            "status": "waiting",
            "players": [opponent],
            "actions": [],
        }

        content = f"{self.username} invites {opponent} to play Rock Paper Scissors. Run '/accept {self.username}' to accept the invitation."
        return self.format_message(public=True, content=content)

    def accept(self, *args):
        if len(args) != 1:
            return self.format_message(content="Invalid number of options. You should run '/accept [user]'.")
        
        host_player = args[0]

        if host_player not in self.data["users"].values():
            return self.format_message(content=f"The user '{host_player}' isn't connected.")
        
        invited_players = self.data["game"]["players"]

        if len(invited_players) != 1:
            return self.format_message(content=f"The number of users invited ({len(invited_players)}) is invalid.")

        if self.username != invited_players[0]:
            return self.format_message(content="You are not the one invited to play.")
        
        if host_player != self.data["game"]["host"]:
            return self.format_message(content=f"The player '{host_player}' has not started a game.")

        self.data["game"]["status"] = "running"
        return self.format_message(public=True, content=f"The game {self.data['game']['name']} has started. Run /play [action] (rock, paper or scissors).")
    
    def play(self, *args):

        if len(args) != 1:
            return self.format_message(content="Invalid number of options. You should run '/play [action]'.")
        
        game = self.data["game"]
        print(game )

        # Rock Paper Scissors
        if game["name"] == "rps" and game["status"] == "running" and self.username in [
            game["host"],
            game["players"][0],
        ]:
            print(args[0])
        return self.format_message()


