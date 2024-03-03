import unittest
from server.user import User
from server.message import Message


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.author = User("1", "Alice", "blue")
        self.content = "Hello, world!"
        self.sent_time = 123456789.0
        self.message = Message(self.author, self.content, self.sent_time)

    def test_initialization(self):
        self.assertEqual(self.message.author, self.author)
        self.assertEqual(self.message.content, self.content)
        self.assertEqual(self.message.sent_time, self.sent_time)

    def test_repr(self):
        expected_repr = f"Message(author={repr(self.author)}, content='{self.content}', sent_time={self.sent_time})"
        self.assertEqual(repr(self.message), expected_repr)

    def test_get_config(self):
        expected_config = {
            "author": self.author.get_config(),
            "content": self.content,
            "sent_time": self.sent_time
        }
        self.assertEqual(self.message.get_config(), expected_config)

    def test_set_config(self):
        new_author = User("2", "Bob", "red")
        new_content = "Goodbye, world!"
        new_sent_time = 987654321.0
        new_config = {"author": new_author, "content": new_content, "sent_time": new_sent_time}

        self.message.set_config(new_config)
        self.assertEqual(self.message.author, new_author)
        self.assertEqual(self.message.content, new_content)
        self.assertEqual(self.message.sent_time, new_sent_time)

if __name__ == "__main__":
    unittest.main()
