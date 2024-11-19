# chessbot.py

import math
import time
import chess
from concurrent.futures import ProcessPoolExecutor
from tabulate import tabulate
from ai.evaliate.evaluator import evaluate_board


class ChessBot:
    def __init__(self, depth=3, logging=False, num_threads=4):
        self.depth = depth
        self.logging = logging
        self.num_threads = num_threads  # Количество процессов
        self.position_history = set()
        self.transposition_table = {}
        self.killer_moves = {}
        self.history_heuristic = {}
        self.header_printed = False

    def negamax(self, board, depth, alpha, beta, color):
        """
        Реализация алгоритма negamax с многопроцессорностью для первого уровня глубины.
        """
        if depth == 0 or board.is_game_over():
            evaluation, evaluation_details = evaluate_board(board, logging=self.logging)
            if self.logging:
                self.log_evaluation(board, evaluation, evaluation_details)
            return color * evaluation, evaluation_details

        max_eval = -float('inf')
        best_move = None
        legal_moves = list(board.legal_moves)

        # Используем ProcessPoolExecutor для параллельной обработки ходов на первом уровне
        if depth == self.depth:
            fen = board.fen()  # Сохраняем состояние доски в формате FEN
            with ProcessPoolExecutor(max_workers=self.num_threads) as executor:
                futures = {executor.submit(self._evaluate_move, fen, move, depth, alpha, beta, color): move for move in legal_moves}
                for future in futures:
                    eval, move = future.result()
                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if alpha >= beta:
                        break  # Alpha-beta отсечение
        else:
            for move in legal_moves:
                eval, _ = self._evaluate_move(board.fen(), move, depth, alpha, beta, color)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break  # Alpha-beta отсечение

        return max_eval, best_move

    def _evaluate_move(self, fen, move, depth, alpha, beta, color):
        """
        Оценка конкретного хода с использованием FEN для копии доски.
        """
        board = chess.Board(fen)  # Восстанавливаем доску из FEN
        # Проверяем, является ли ход псевдолегальным
        if move not in board.legal_moves:
            return -float('inf'), move  # Штраф за нелегальный ход

        board.push(move)
        eval, _ = self.negamax(board, depth - 1, -beta, -alpha, -color)
        eval = -eval
        return eval, move

    def log_evaluation(self, board, evaluation, evaluation_details):
        """Логирование оценки позиции в формате таблицы."""
        move = board.peek() if board.move_stack else "Начальная позиция"
        table_data = [[move] + list(evaluation_details.values())]

        # Выводим заголовки только один раз
        if self.logging and not self.header_printed:
            headers = ["Ход"] + list(evaluation_details.keys())
            print(tabulate([], headers=headers, tablefmt='orgtbl'))  # Печатаем заголовки
            self.header_printed = True  # Устанавливаем флаг, что заголовки выведены

        print(tabulate(table_data, tablefmt='orgtbl'))  # Выводим данные

    def find_best_move(self, board, max_time=5):
        """
        Находит лучший ход с учетом временного ограничения.
        """
        start_time = time.time()
        best_move = None

        for depth in range(1, self.depth + 1):
            if time.time() - start_time > max_time:
                break
            eval, move = self.negamax(board, depth, -math.inf, math.inf, 1 if board.turn == chess.WHITE else -1)
            if move:
                best_move = move

        return best_move


