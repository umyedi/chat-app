import unittest
from server.user import User

class TestUser(unittest.TestCase):
    def setUp(self):
        self.user1 = User("1", "Alice", "blue")
        self.user2 = User("2", "Bob", "red")

    def test_initialization(self):
        self.assertEqual(self.user1.user_id, "1")
        self.assertEqual(self.user1.username, "Alice")
        self.assertEqual(self.user1.color, "blue")

    def test_repr(self):
        expected_repr = "User(user_id='1', username='Alice', color='blue')"
        self.assertEqual(repr(self.user1), expected_repr)

    def test_eq(self):
        user1_copy = User("1", "Alice", "blue")
        self.assertEqual(self.user1, user1_copy)
        self.assertNotEqual(self.user1, self.user2)

    def test_get_config(self):
        expected_config = {"user_id": "1", "username": "Alice", "color": "blue"}
        self.assertEqual(self.user1.get_config(), expected_config)

    def test_set_config(self):
        new_config = {"user_id": "3", "username": "Charlie", "color": "green"}
        self.user1.set_config(new_config)
        self.assertEqual(self.user1.user_id, "3")
        self.assertEqual(self.user1.username, "Charlie")
        self.assertEqual(self.user1.color, "green")

        # Test partial update
        partial_config = {"username": "Dave"}
        self.user1.set_config(partial_config)
        self.assertEqual(self.user1.user_id, "3")  # Should remain unchanged
        self.assertEqual(self.user1.username, "Dave")
        self.assertEqual(self.user1.color, "green")  # Should remain unchanged

if __name__ == "__main__":
    unittest.main()
