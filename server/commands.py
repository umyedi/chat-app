from user import User
from message import Message
from chatroom import ChatRoom
from games import Game, RockPaperScissors
from api.api import generate_image

import threading
from datetime import datetime


class CommandsHandler:
    def __init__(self, server, user: User, chat_room: ChatRoom, command: str, arguments: list[str] = None) -> None:

        self.server = server  # Server instance
        self.user = user
        self.chat_room = chat_room
        self.command = command
        self.arguments = arguments

        self.default_user = self.chat_room.default_user

        self.command_map = {
            "/help": self.help,
            "/time": self.time,
            "/users": self.users,
            "/games": self.games,
            "/image": self.image,
            "/invite": self.invite,
            "/start": self.start,
            "/play": self.play,
        }

        self.commands = {
            "/help": "List all the commands.",
            "/time": "Displays current time.",
            "/users": "List the connected users.",
            "/games": "Displays the games available",
            "/image [prompt]": "Generate an image with DALL-E.",
            "/invite [game] [username]": "Invite a user to play a game.",
            "/start": "Start the selected game.",
            "/play [action]": "Play an action in the current game.",
        }

        self.games_map = {"rps": RockPaperScissors}

        self.games = {"rps": "Rock Paper Scissors"}

    def _get_user_from_username(self, username: str) -> User:
        """Returns the first user found with the username provided.

        Args:
            username (str): Username you're looking for

        Returns:
            User: User object if it was found. None otherwise.
        """
        return next((usr for usr in self.chat_room.users if usr.username == username), None)

    def execute(self):
        if function := self.command_map.get(self.command):
            response = function()  # Executes the desired function
        else:
            response = f"The command '{self.command}' doesn't exist."

        if response:
            self.server.send_message_to_client(self.user.user_id, Message(self.chat_room.default_user, response))

    def help(self):
        return "".join(f"<br>{'&nbsp;'*4}{cmd} - {des}" for cmd, des in self.commands.items())

    @staticmethod
    def time(self):
        return f"It's {datetime.now().strftime('%H:%M:%S')}."

    def users(self):
        return "".join(
            f"<br>{'&nbsp;'*4}- <span style='color:{user.color}'>{user.username}</span>"
            for user in self.chat_room.users
        )

    def games(self):
        return "".join(f"<br>{'&nbsp;'*4}{game} - {des}" for game, des in self.games.items())

    def image(self):
        if self.arguments:
            prompt = " ".join(self.arguments)
            threading.Thread(target=self._handle_image_generation, args=(self.chat_room, prompt)).start()
            return "Wait while the image generates..."
        return "You must provide a prompt to generate an image."

    def invite(self):
        if len(self.arguments) != 2:
            return "Invalid number of arguments"

        game_name, username_invited = self.arguments
        player_invited = self._get_user_from_username(username_invited)

        if not player_invited:
            return f"The user called '{username_invited}' cannot be found."

        self.server.current_game = self.games_map[game_name](host_player=self.user)

        message = Message(author=self.default_user, content=self.server.current_game.invite(player=player_invited))
        print(f"{self.server.current_game=}")
        self.chat_room.add_message(message)
        self.server.distribute_message(self.chat_room, message)
        return None

    def start(self):
        if not self.server.current_game:
            return "You must invite players before starting a game."
        if self.user != self.server.current_game.host_player:
            return "You don't have the right to start the game if you haven't created it."

        message = Message(author=self.default_user, content=self.server.current_game.start())
        self.chat_room.add_message(message)
        self.server.distribute_message(self.chat_room, message)
        return None

    def play(self):
        if len(self.arguments) != 1:
            return "Invalid number of arguments"

        if not self.server.current_game:
            return "You must start a game before playing."

        if self.user not in self.server.current_game.players:
            return "You are not in the game."

        output = self.server.current_game.play(self.user, action=self.arguments[0])

        self.server.send_message_to_client(self.user.user_id, Message(self.default_user, output))

        if self.server.current_game.check_win():
            win_message = Message(self.default_user, self.server.current_game.check_win())
            self.chat_room.add_message(win_message)
            self.server.distribute_message(self.chat_room, win_message)
            self.server.current_game = None
        return None

    def _handle_image_generation(self, chat_room_id, prompt):
        url = generate_image(prompt)
        message = Message(self.default_user, url)
        self.chat_room.add_message(message)
        self.server.distribute_message(chat_room_id, message)
