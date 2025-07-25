class Connect4Game:
    def __init__(self):
        self.board = [[0] * 7 for _ in range(6)]
        self.current_player = 1
        self.is_game_over = False
        self.winner = None

    def make_move(self, column):
        if not self.is_valid_move(column):
            return

        for row in range(5, -1, -1):
            if self.board[row][column] == 0:
                self.board[row][column] = self.current_player
                break

    def check_winner(self):
        rows = len(self.board)
        cols = len(self.board[0])

        # Horizontal check
        for row in range(rows):
            for col in range(cols - 3):
                if all(self.board[row][col + i] == self.current_player for i in range(4)):
                    self.is_game_over = True
                    self.winner = self.current_player
                    return

        # Vertical check
        for col in range(cols):
            for row in range(rows - 3):
                if all(self.board[row + i][col] == self.current_player for i in range(4)):
                    self.is_game_over = True
                    self.winner = self.current_player
                    return

        # Diagonal (down-right)
        for row in range(rows - 3):
            for col in range(cols - 3):
                if all(self.board[row + i][col + i] == self.current_player for i in range(4)):
                    self.is_game_over = True
                    self.winner = self.current_player
                    return

        # Diagonal (up-right)
        for row in range(3, rows):
            for col in range(cols - 3):
                if all(self.board[row - i][col + i] == self.current_player for i in range(4)):
                    self.is_game_over = True
                    self.winner = self.current_player
                    return

    def switch_turn(self):
        self.current_player = 3 - self.current_player

    def is_valid_move(self, column):
        for row in self.board:
            if row[column] == 0:
                return True
        return False

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
