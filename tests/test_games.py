
import unittest
from server.user import User
from server.games import Game, RockPaperScissors


class TestGame(unittest.TestCase):
    def setUp(self):
        self.player1 = User("Alice")
        self.player2 = User("Bob")
        self.game = Game(self.player1, "Test Game")

    def test_initialization(self):
        self.assertEqual(self.game.host_player, self.player1)
        self.assertEqual(self.game.game_name, "Test Game")
        self.assertIn(self.player1, self.game.players)
        self.assertFalse(self.game.is_game_started)

    def test_invite(self):
        self.game.invite(self.player2)
        self.assertIn(self.player2, self.game.players)

    def test_start_not_enough_players(self):
        result = self.game.start()
        self.assertEqual(result, "Not enough players to start the game.")
        self.assertFalse(self.game.is_game_started)

    def test_start_game(self):
        self.game.invite(self.player2)
        result = self.game.start()
        self.assertEqual(result, "Game started. Good luck!")
        self.assertTrue(self.game.is_game_started)


class TestRockPaperScissors(unittest.TestCase):
    def setUp(self):
        self.player1 = User("Alice")
        self.player2 = User("Bob")
        self.rps_game = RockPaperScissors(self.player1)

    def test_initialization(self):
        self.assertIsInstance(self.rps_game, RockPaperScissors)
        self.assertEqual(self.rps_game.game_name, "Rock Paper Scissors")

    def test_play_invalid_action(self):
        result = self.rps_game.play(self.player1, "lizard")
        self.assertEqual(result, "The action 'lizard' is not valid.")

    def test_play_valid_action(self):
        self.rps_game.invite(self.player2)
        self.rps_game.start()
        result = self.rps_game.play(self.player1, "rock")
        self.assertIn("played rock", result)

    def test_game_outcome(self):
        self.rps_game.invite(self.player2)
        self.rps_game.start()
        self.rps_game.play(self.player1, "rock")
        self.rps_game.play(self.player2, "scissors")
        self.assertIsNotNone(self.rps_game.winner)
        self.assertEqual(self.rps_game.check_win(), f"{self.player1.username} has won the game!")


if __name__ == "__main__":
    unittest.main()
