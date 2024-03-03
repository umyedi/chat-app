import unittest
from server.user import User
from server.message import Message
from server.chatroom import ChatRoom

class TestChatRoom(unittest.TestCase):
    def setUp(self):
        self.chat_room = ChatRoom("test_room")
        self.user1 = User("1", "Alice", "blue")
        self.user2 = User("2", "Bob", "red")
        self.message1 = Message(self.user1, "Hello, Bob!", 123456789.0)

    def test_initialization(self):
        self.assertEqual(self.chat_room.chat_room_id, "test_room")
        self.assertEqual(len(self.chat_room.users), 1)  # Includes the default system user
        self.assertEqual(len(self.chat_room.messages), 1)  # Includes the default system message

    def test_add_user(self):
        self.assertTrue(self.chat_room.add_user(self.user1))
        self.assertFalse(self.chat_room.add_user(self.user1))  # Adding the same user again
        self.assertEqual(len(self.chat_room.users), 2)

    def test_add_message(self):
        self.chat_room.add_message(self.message1)
        self.assertEqual(len(self.chat_room.messages), 2)  # Includes the default system message

    def test_remove_user(self):
        self.chat_room.add_user(self.user1)
        self.assertTrue(self.chat_room.remove_user(self.user1))
        self.assertFalse(self.chat_room.remove_user(self.user1))  # Removing the same user again
        self.assertEqual(len(self.chat_room.users), 1)  # Back to just the default system user

    def test_eq(self):
        another_chat_room = ChatRoom("test_room")
        self.assertEqual(self.chat_room, another_chat_room)

    def test_get_config(self):
        config = self.chat_room.get_config()
        self.assertIn("chat_room_id", config)
        self.assertIn("users", config)
        self.assertIn("messages", config)

    def test_set_config(self):
        new_config = {
            "chat_room_id": "new_room",
            "users": [{"username": "Charlie", "color": "green"}],
            "messages": [{"content": "Welcome, Charlie!", "sent_time": 987654321.0}]
        }
        self.chat_room.set_config(new_config)
        self.assertEqual(self.chat_room.chat_room_id, "new_room")
        self.assertEqual(len(self.chat_room.users), 2)  # Includes the default system user
        self.assertEqual(len(self.chat_room.messages), 2)  # Includes the default system message

if __name__ == '__main__':
    unittest.main()
