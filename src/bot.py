from ai.chessbot import ChessBot as AIChessBot

class ChessBotWrapper:
    def __init__(self, depth):
        self.bot = AIChessBot(depth=depth)

    def find_best_move(self, board):
        return self.bot.find_best_move(board)
