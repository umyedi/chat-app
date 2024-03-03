from user import User


class Message:
    def __init__(self, author: User = None, content: str = None, sent_time: float = None) -> None:
        self.author = author
        self.content = content
        self.sent_time = sent_time

    def __repr__(self) -> str:
        author, content, sent_time = self.author, self.content, self.sent_time
        return f"Message({author=}, {content=}, {sent_time=})"

    def get_config(self) -> dict:
        return {"author": self.author.get_config(), "content": self.content, "sent_time": self.sent_time}

    def set_config(self, config: dict) -> None:
        self.author = config.get("author", self.author)
        self.content = config.get("content", self.content)
        self.sent_time = config.get("sent_time", self.sent_time)
