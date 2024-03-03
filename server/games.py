from user import User


class Game:
    def __init__(self, host_player: User = None, game_name=None):
        self.host_player = host_player
        self.game_name = game_name
        self.players = [self.host_player]
        self.is_game_started = False

    def __repr__(self) -> str:
        host_player, game_name, players = self.host_player, self.game_name, self.players
        return f"Game({host_player=}, {game_name=}): {players=}"

    def invite(self, player: User):
        if not self.is_game_started:
            self.players.append(player)
            return f"{self.host_player.username} has invited {player.username} to play {self.game_name}."
        else:
            return "Can't invite, game already started."

    def start(self):
        if len(self.players) < 2:
            return "Not enough players to start the game."
        else:
            self.is_game_started = True
            return "Game started. Good luck!"


class RockPaperScissors(Game):
    def __init__(self, host_player: User) -> None:
        super().__init__(host_player, game_name="Rock Paper Scissors")

        self.action_player_1 = None
        self.action_player_2 = None

        # None: waiting player moves, User object: winner of the game, False: it's a tie
        self.winner = None

    def __repr__(self) -> str:
        return super().__repr__()

    def check_win(self) -> str:
        if type(self.winner) == User:
            return f"{self.winner.username} has won the game!"
        if self.winner == False:
            return "It's a tie!"
        else:
            return None

    def _update_game_state(self) -> None:
        if None in (self.action_player_1, self.action_player_2):
            # One or both players haven't made a move yet
            return

        win_conditions = {"rock": "scissors", "scissors": "paper", "paper": "rock"}

        if self.action_player_1 == self.action_player_2:
            self.winner = False  # It's a tie
        elif win_conditions[self.action_player_1] == self.action_player_2:
            self.winner = self.players[0]  # Player 1 wins
        else:
            self.winner = self.players[1]  # Player 2 wins

    def play(self, user: User, action: str):
        action = action.lower().strip()

        if not action in ["rock", "paper", "scissors"]:
            return f"The action '{action}' is not valid."

        if user == self.players[0]:
            self.action_player_1 = action
            output = f"{self.players[0].username} played {action}."
        elif user == self.players[1]:
            self.action_player_2 = action
            output = f"{self.players[1].username} played {action}."
        else:
            return f"{user.username} is not in the game"

        self._update_game_state()
        return output


if __name__ == "__main__":
    player1 = User("Alice")
    player2 = User("Bob")
    rps_game = RockPaperScissors(player1)

    print(rps_game.invite(player2))

    print(rps_game.start())

    print(rps_game.play(user=player1, action="rock"))
    print(rps_game.play(user=player2, action="scissors"))
