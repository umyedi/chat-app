from utils import *
from api.api_manager import generate_image
import threading

class Commands:
    def __init__(self, username: str, database_path: Path) -> None:

        self.database_path = database_path
        self.data = read_json(database_path)

        self.username = username
        self.usernames = [user["username"] for user in self.data["users"].values()]

        self.commands_list = {
            "/help": self.help,
            "/time": self.time,
            "/image": self.image,
            "/games": self.games,
            "/invite": self.invite,
            "/accept": self.accept,
            "/play": self.play,
        }

        self.commands_description = {
            "/help": "List all the commands.",
            "/time": "Displays current time.",
            "/image [prompt]": "Generate an image with DALL-E.",
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
            self.data["chat_history"][get_current_time()] = self._format_message(
                content=f"The command '{command}' doesn't exists."
            )
        else:
            return_message = self.commands_list[command](*args)
            self.data["chat_history"][get_current_time()] = return_message

        write_json(self.database_path, self.data)

    def _format_message(
        self, username: str = "system", public: bool = False, content: str = None, viewers: list = None
    ):
        if viewers is None:
            viewers = [self.username]
        return {"username": username, "public": public, "content": content, "viewers": viewers}

    def help(self, *args):
        content = "".join(
            f"<br>{'&nbsp;'*4}{cmd} - {self.commands_description[cmd]}" for cmd in self.commands_description
        )
        return self._format_message(content=content)

    def time(self, *args):
        return self._format_message(content=f"It's {datetime.now().strftime('%I:%M %p')}.")

    def _generate_image(self, prompt):
        url = generate_image(prompt)
        data = read_json(self.database_path)
        data["chat_history"][get_current_time()] = self._format_message(content=url)
        write_json(self.database_path, data)

    def image(self, *args):
        if not args:
            return self._format_message(content="Invalid number of options. You should run '/image [prompt]'.")

        prompt = " ".join(str(word) for word in args)

        download_thread = threading.Thread(target=self._generate_image, args=(prompt,)) # 
        download_thread.start()

        return self._format_message(content="Wait for the image to generate...")

    def games(self, *args):
        content = "".join(f"<br>{'&nbsp;'*4}{game} - {self.games_description[game]}" for game in self.games_description)
        return self._format_message(content=content)

    def _update_game(self, name: str, status: str, players: list[str], actions: list[str] = None):
        if actions is None:
            actions = []
        self.data["game"] = {
            "name": name,
            "host": self.username,
            "status": status,
            "current_round": 0,
            "players": players,
            "actions": actions,
        }

    def invite(self, *args):

        if len(args) != 2:
            return self._format_message(content="Invalid number of options. You should run '/invite [game] [user]'.")

        game = args[0]
        opponent = args[1]

        if game not in self.games_description:
            content = f"The game '{game}' doesn't exists. Run '/games' to see the list of the games available."
            return self._format_message(content=content)
        if opponent not in self.usernames:
            return self._format_message(content=f"The user '{opponent}' isn't connected.")
        if self.data["game"]["status"] == "running":
            content = f"The game {self.data['game']['name']} is still running. The host of the game should run '/end {self.data['game']['name']}' to end the game."
            return self._format_message(content=content)

        self._update_game(name=game, status="waiting", players=[opponent])

        content = f"{self.username} invites {opponent} to play Rock Paper Scissors. Run '/accept {self.username}' to accept the invitation."
        return self._format_message(public=True, content=content)

    def accept(self, *args):
        if len(args) != 1:
            return self._format_message(content="Invalid number of options. You should run '/accept [user]'.")

        host_player = args[0]

        if host_player not in self.usernames:
            return self._format_message(content=f"The user '{host_player}' isn't connected.")

        invited_players = self.data["game"]["players"]

        if len(invited_players) != 1:
            return self._format_message(content=f"The number of users invited ({len(invited_players)}) is invalid.")

        if self.username != invited_players[0]:
            return self._format_message(content="You are not the one invited to play.")

        if host_player != self.data["game"]["host"]:
            return self._format_message(content=f"The player '{host_player}' has not started a game.")

        self.data["game"]["status"] = "running"
        return self._format_message(
            public=True,
            content=f"The game {self.data['game']['name']} has started. Run /play [action] (rock, paper or scissors).",
        )

    def _play_rps(self, action: str):

        current_round = self.data["game"]["current_round"]

        if len(self.data["game"]["actions"]) < current_round + 1:
            self.data["game"]["actions"].append(
                {self.data["game"]["host"]: None, self.data["game"]["players"][0]: None, "winner": None}
            )

        self.data["game"]["actions"][current_round][self.username] = action
        return self._format_message(
            content=f"You played {action}. Waiting for {self.data['game']['players'][0]} to play."
        )

    def play(self, *args):

        if len(args) != 1:
            return self._format_message(content="Invalid number of options. You should run '/play [action]'.")

        game = self.data["game"]
        # Rock Paper Scissors
        if (
            game["name"] == "rps"
            and game["status"] == "running"
            and self.username
            in [
                game["host"],
                game["players"][0],
            ]
        ):
            return self._play_rps(args[0])
