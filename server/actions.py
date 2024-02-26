"""

Ce fichier contient les fonctions exécutées par le client.

"""

import re
import inspect
import random
from commands import Commands
from utils import *


class Actions:
    def __init__(self, session_id: str) -> None:

        self.action_handlers = {
            "help": self.help,
            "join_session": self.join_session,
            "get_session_status": self.get_session_status,
            "send_message": self.submit_message,
        }

        self.database_path = Path(f"sessions/{session_id}.json")
        if os.path.exists(self.database_path):
            self.data = read_json(self.database_path)
        else:
            raise ValueError("The session id provided is not valid")

    def _output_data(self) -> None:
        write_json(self.database_path, self.data)

    def exists(self, action: str, **kwargs) -> bool:
        return action in self.action_handlers

    def execute(self, action, params, **kwargs) -> dict:
        return self.action_handlers[action](**params)

    def help(self, **kwargs) -> dict:
        """List all the function available to the client with their parameters and docstring.

        Returns:
            dict: List of the functions with their parameters and docstring
        """
        return {
            action: {
                "params": tuple(inspect.signature(function).parameters),  # Get the params of 'function'
                "docstring": function.__doc__,  # Get the documentation of 'function'
            }
            for action, function in self.action_handlers.items()
        }

    def _add_user(self, user_id, username) -> None:
        self.data["users"][user_id] = {
            "username": username,
            "color": random.choice(COLORS),
            "last-active": get_current_seconds(),
        }

    def _generate_new_user_id(self, max_attempts: int = 100) -> str:
        for _ in range(max_attempts):
            user_id = random_digits(6)
            if user_id not in self.data["users"]:
                return user_id
        raise ValueError("Couldn't find a valid user_id.")

    def join_session(self, username: str, **kwargs) -> dict:
        """Join a specific session with a username and returns a random id.

        Args:
            username (str): Username provided to be used in the session

        Raises:
            ValueError: Username provided already exists in the session
            ValueError: The lenght of the username in not valid
            ValueError: Some characters in the username are invalid
            ValueError: The username contains banned words

        Returns:
            dict: Returns the user id associated with the username provided
        """
        usernames = [user_info["username"] for user_info in self.data["users"].values()]
        if username in usernames:
            raise ValueError("This username already exists.")
        if not (3 <= len(username) < 18):
            raise ValueError("The user name must be between 3 and 18 characters long.")
        if not re.match(r"^\w+$", username):
            raise ValueError("The user name must contains only letters, digits, and underscores.")
        if "sys" in username.lower():
            raise ValueError("You cannot use a username containing 'sys'.")

        user_id = self._generate_new_user_id()
        self._add_user(user_id, username)
        self._output_data()
        return {"user-id": user_id}

    def _remove_private_messages(self, user_id: str):
        username = self.data["users"][user_id]["username"]
        self.data["chat_history"] = {
            timestamp: message
            for timestamp, message in self.data["chat_history"].items()
            if message["public"] or username in message["viewers"]
        }

    def _update_last_active(self, user_id):
        self.data["users"][user_id]["last-active"] = get_current_seconds()
        self._output_data()

    def get_session_status(self, user_id: str, **kwargs) -> dict:
        """Returns all the data of a session where the user is logged in.

        Args:
            user_id (str): Id of the user who's asking for the session's data

        Raises:
            ValueError: The user id is not in the session

        Returns:
            dict: Content of the json file containing the session
        """

        if user_id not in self.data["users"].keys():
            raise ValueError("The user id provided doesn't match.")

        self._remove_private_messages(user_id)
        self._update_last_active(user_id)
        self.data["users"] = list(self.data["users"].values())  # Remove the ids of the users

        return self.data

    def _write_message(self, username: str, message: str):
        self.data["chat_history"][get_current_time()] = {
            "username": username,
            "content": message,
            "public": True,
            "viewers": [],
        }
        self._output_data()

    def submit_message(self, user_id: str, message: str, **kwargs):
        """Write a message sent by a user in a session. If the message is a command, it runs it.

        Args:
            user_id (str): User who wants to write the messages
            message (str): Content of the message

        Raises:
            ValueError: The user id is not in the session
        """

        if user_id not in self.data["users"].keys():
            raise ValueError("The user id provided doesn't match.")

        username = self.data["users"][user_id]["username"]
        cmd = Commands(username, self.database_path)

        if cmd.is_command(message):
            cmd.execute_command(message)
        else:
            self._write_message(username, message)