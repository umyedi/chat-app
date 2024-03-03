from user import User
from message import Message
from chatroom import ChatRoom
from commands import CommandsHandler
from games import Game
from log import logger

import zmq
import json
import traceback
from threading import Thread


class Server:
    def __init__(self, ip: str = "127.0.0.1", port: str = "5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)

        self.ip = ip
        self.port = port
        self.address = f"tcp://{self.ip}:{self.port}"

        self.chat_rooms = []
        self.users = []
        self.current_game = Game()

    def start(self):
        self.socket.bind(self.address)
        logger.info(f"Server started at {self.address}")
        self.thread = Thread(target=self.listener)
        self.thread.start()

    def _get_user(self, user_id: bytes) -> User | None:
        for usr in self.users:
            if usr.user_id == user_id:
                return usr
        return None

    def _get_chat_room(self, chat_room_id: str) -> ChatRoom | None:
        for chat_room in self.chat_rooms:
            if chat_room.chat_room_id == chat_room_id:
                return chat_room
        return None

    def listener(self):
        while True:
            try:
                client_id, query = self.socket.recv_multipart()
                query = json.loads(query.decode())
                action = query.get("action")

                match action:
                    case "join":
                        self._handle_join(client_id, query)
                    case "message":
                        self._handle_message(client_id, query)
            except Exception:
                logger.error(traceback.format_exc())

    def _handle_join(self, client_id, message_data):
        # Creates a new user for the client if he hasn't one yet
        if not self._get_user(client_id):
            user = User(user_id=client_id)
            user.set_config(message_data["user"])
            user.set_random_color()
            self.users.append(user)
        else:
            user = self._get_user(client_id)
            if user.username != message_data["user"]["username"]:
                user.username = message_data["user"]["username"]

        # Creates a new chat rooms if it doesn't already exists
        if not self._get_chat_room(message_data["room_id"]):
            chat_room = ChatRoom(message_data["room_id"])
            self.chat_rooms.append(chat_room)
        else:
            chat_room = self._get_chat_room(message_data["room_id"])

        chat_room.add_user(user)
        welcome_message = Message(
            chat_room.default_user,
            f"The user <b><span style='color:{user.color}'>{user.username}</span><b> has joined the chat!",
        )
        chat_room.add_message(welcome_message)
        self.distribute_message(chat_room, welcome_message)
        logger.info(f"User {user} joined chat room {chat_room.chat_room_id}")

    def _handle_message(self, client_id, message_data):

        chat_room = self._get_chat_room(message_data["room_id"])
        if not chat_room:
            raise ValueError(f"The chat room {message_data['room_id']} doesn't exists.")

        content = message_data["content"]
        user = self._get_user(client_id)

        if user not in chat_room.users:
            raise ValueError(f"The user {user} is not in the chat room {chat_room}")

        if content.startswith("/"):  # If the message is a command
            command, *arguments = content.split()
            command_handler = CommandsHandler(self, user, chat_room, command, arguments)
            command_handler.execute()
        else:
            message = Message(author=user, content=content)
            self.distribute_message(chat_room, message)
            chat_room.add_message(message)

        logger.info(f"Message from {user} in room {chat_room.chat_room_id}: {content}")

    def send_message_to_client(self, client_id, message):
        message_content = json.dumps(
            {"author": {"username": message.author.username, "color": message.author.color}, "content": message.content}
        ).encode("utf-8")
        self.socket.send_multipart([client_id, message_content])

    def distribute_message(self, chat_room: ChatRoom, message: Message):
        message_content = json.dumps(
            {
                "author": {"username": message.author.username, "color": message.author.color},
                "content": message.content,
                "room_id": chat_room.chat_room_id,
            }
        ).encode("utf-8")

        for user in chat_room.users:
            client_id = user.user_id
            if client_id:
                self.socket.send_multipart([client_id, message_content])
