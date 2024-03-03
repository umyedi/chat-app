from user import User
from message import Message


class ChatRoom:
    def __init__(self, chat_room_id: str = None, users: list[User] = None, messages: list[Message] = None) -> None:
        self.chat_room_id = chat_room_id

        # Empty dicts as default
        self.users = users if users is not None else []
        self.messages = messages if messages is not None else []

        self.default_user = self._init_default_user("system", "black")

    def __repr__(self) -> str:
        chat_room_id, users, messages = self.chat_room_id, self.users, self.messages
        return f"ChatRoom({chat_room_id=}, {users=}, {messages=})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ChatRoom):
            return self.chat_room_id == other.chat_room_id
        return False

    def _init_default_user(self, username, color) -> User:
        default_user = User(user_id=None, username=username, color=color)
        self.users.insert(0, default_user)
        self.messages.insert(0, Message(author=default_user, content="Chat room created."))
        return default_user

    def add_user(self, user: User) -> bool:
        if user not in self.users:
            self.users.append(user)
            return True
        return False

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def remove_user(self, user: User) -> bool:
        if user in self.users:
            self.users.remove(user)
            return True
        return False

    def get_config(self) -> dict:
        return {"chat_room_id": self.chat_room_id, "users": self.users, "messages": self.messages}

    def set_config(self, config: dict) -> None:
        self.chat_room_id = config.get("chat_room_id", self.chat_room_id)

        messages = config.get("messages", self.messages)
        users = config.get("users", self.messages)

        for msg_data in messages:
            self.add_message(Message().set_config(msg_data))

        for usr_data in users:
            self.add_user(User().set_config(usr_data))