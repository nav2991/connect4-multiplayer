class Connect4Game:
    def __init__(self):
        self.board = [[0] * 7 for _ in range(6)]
        self.current_player = 1
        self.is_game_over = False
        self.winner = None

    def make_move(self, column):
        pass

    def check_winner(self):
        pass

    def switch_turn(self):
        self.current_player = 3 - self.current_player

    def is_valid_move(self, column):
        pass

    def reset(self):
        self.board = [[0] * 7 for _ in range(6)]
        self.current_player = 1
        self.is_game_over = False
        self.winner = None

    def get_state(self):
        return {
            "board": self.board,
            "current_player": self.current_player,
            "is_game_over": self.is_game_over,
            "winner": self.winner
        }
