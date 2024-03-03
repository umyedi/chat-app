import random


class User:
    def __init__(self, user_id: bytes = None, username: str = None, color: str = None) -> None:
        self.user_id = user_id
        self.username = username
        self.color = color

    def __repr__(self) -> str:
        user_id, username, color = self.user_id, self.username, self.color
        return f"User({user_id=}, {username=}, {color=})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.user_id == other.user_id
        return False

    def get_config(self) -> dict:
        return {"user_id": self.user_id, "username": self.username, "color": self.color}

    def set_config(self, config: dict) -> None:
        self.user_id = config.get("user_id", self.user_id)
        self.username = config.get("username", self.username)
        self.color = config.get("color", self.color)

    def set_random_color(self):
        self.color = random.choice(  # Colors from Twitch
            [
                "#FE0000",
                "#0000FE",
                "#028002",
                "#B22222",
                "#FE7E4F",
                "#9BCA31",
                "#FE4300",
                "#2E8A57",
                "#D9A420",
                "#D3681E",
                "#609E9E",
                "#1E90FF",
                "#FF69B2",
                "#8A2BE1",
            ]
        )
