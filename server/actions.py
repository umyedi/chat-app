"""

Ce fichier contient les fonctions exécutées par le client.

"""

import os
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
            "write_message": self.write_message,
        }

        self.colors = [
            "FE0000",
            "0000FE",
            "028002",
            "B22222",
            "FE7E4F",
            "9BCA31",
            "FE4300",
            "2E8A57",
            "D9A420",
            "D3681E",
            "609E9E",
            "1E90FF",
            "FF69B2",
            "8A2BE1",
        ]

        self.database_path = Path(f"sessions/{session_id}.json")
        if not os.path.exists(self.database_path):
            print(self.database_path)
            raise ValueError("The session id provided is not valid")
        self.data = read_json(self.database_path)

    def exists(self, action: str) -> bool:
        return action in self.action_handlers

    def execute(self, action, params):
        return self.action_handlers[action](**params)

    def help(self):
        """List all the function available to the client with their parameters and docstring.

        Returns:
            dict: Functions available
        """

        return {
            action: {
                "params": tuple(inspect.signature(function).parameters),
                "docstring": function.__doc__,
            }
            for action, function in self.action_handlers.items()
        }

    def join_session(self, username: str) -> dict:

        if username in self.data["users"].values():
            raise ValueError("This username already exists.")
        if not (3 <= len(username) < 18):
            raise ValueError("The user name must be between 3 and 18 characters long.")
        if not re.match(r"^\w+$", username):
            raise ValueError("The user name must contains only letters, digits, and underscores.")
        if "sys" in username.lower():
            raise ValueError("You cannot use a username containing 'sys'.")

        # Generate new user_id
        max_attempts = 100
        for _ in range(max_attempts):
            user_id = random_digits(6)
            if user_id not in self.data["users"]:
                break
        else:  # If the loop completes all iterations without breaking
            raise ValueError("Couldn't find a valid user_id.")

        # Adds the user to the database
        self.data["users"][user_id] = {
            "username": username,
            "color": random.choice(self.colors),
            "last-active": get_current_seconds(),
        }
        write_json(self.database_path, self.data)

        return {"user-id": user_id}

    def get_session_status(self, user_id: str) -> json:

        if user_id not in self.data["users"].keys():
            raise ValueError("The user id provided doesn't match.")

        # Identify private messages not sent by the specified user and mark them for removal
        username = self.data["users"][user_id]["username"]
        remove_timestamp = [
            timestamp
            for timestamp, message in self.data["chat_history"].items()
            if not message["public"] and username not in message["viewers"]
        ]
        # Remove the identified private messages from the chat history
        for timestamp in remove_timestamp:
            del self.data["chat_history"][timestamp]

        # Remove the ids of the users but keeps the usernames
        self.data["users"] = list(self.data["users"].values())

        return self.data

    def write_message(self, user_id: str, message: str):

        if user_id not in self.data["users"].keys():
            return {"status": "error", "result": "The user id provided doesn't match."}

        username = self.data["users"][user_id]["username"]

        cmd = Commands(username, self.database_path)
        if cmd.is_command(message):  # TODO: merge 'is_command' into 'execute_command'
            cmd.execute_command(message)
        else:
            self.data["chat_history"][get_current_time()] = {
                "username": username,
                "content": message,
                "public": True,
                "viewers": [],
            }
            write_json(self.database_path, self.data)
