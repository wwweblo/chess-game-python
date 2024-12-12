import chess
import math
import time

r'''
/ ============================ \

            CHESS BOT

\ ============================ /
'''

class ChessBot:
    def __init__(self, depth=3):
        self.depth = depth
        self.position_history = set()  # Храним хэши позиций
        self.transposition_table = {}  # Таблица транспозиции
        self.killer_moves = {}         # Сохраняем хорошие ходы для каждой глубины

    def center_control(self, board, color):
        """Оценка контроля центра (сильные квадраты)."""
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        control = 0
        for square in center_squares:
            if board.attackers(color, square):
                control += 10
        return control

    def calculate_pawn_islands(self, board, color):
        """Возвращает количество пешечных островов для указанного цвета."""
        files_with_pawns = set(chess.square_file(square) for square in board.pieces(chess.PAWN, color))
        islands = 0
        last_file = -2
        for file in sorted(files_with_pawns):
            if file > last_file + 1:
                islands += 1
            last_file = file
        return islands

    def calculate_isolated_pawns(self, board, color):
        """Возвращает количество изолированных пешек."""
        isolated_pawns = 0
        for square in board.pieces(chess.PAWN, color):
            file = chess.square_file(square)
            left_adjacent_file = file - 1 if file > 0 else None
            right_adjacent_file = file + 1 if file < 7 else None

            # Проверяем пешки на соседних вертикалях (файлах)
            has_left_pawn = any(board.piece_at(chess.square(left_adjacent_file, rank)) == chess.PAWN for rank in range(8)) if left_adjacent_file is not None else False
            has_right_pawn = any(board.piece_at(chess.square(right_adjacent_file, rank)) == chess.PAWN for rank in range(8)) if right_adjacent_file is not None else False

            if not has_left_pawn and not has_right_pawn:
                isolated_pawns += 1

        return isolated_pawns

    def calculate_doubled_pawns(self, board, color):
        """Возвращает количество удвоенных пешек."""
        doubled_pawns = 0
        for file in chess.FILE_NAMES:
            pawns_in_file = board.pieces(chess.PAWN, color) & chess.BB_FILES[chess.FILE_NAMES.index(file)]
            if len(pawns_in_file) > 1:
                doubled_pawns += 1
        return doubled_pawns

    def control_of_open_lines(self, board, color):
        """Возвращает оценку контроля открытых и полузакрытых линий для ладей."""
        open_lines = 0
        semi_open_lines = 0

        for file in range(8):
            pawns_on_file = any(
                board.piece_at(chess.square(file, rank)) and board.piece_at(
                    chess.square(file, rank)).piece_type == chess.PAWN
                for rank in range(8)
            )
            if not pawns_on_file:
                for rank in range(8):
                    piece = board.piece_at(chess.square(file, rank))
                    if piece and piece.piece_type == chess.ROOK and piece.color == color:
                        open_lines += 1
            elif any(
                    board.piece_at(chess.square(file, rank)) and board.piece_at(
                        chess.square(file, rank)).piece_type == chess.PAWN
                    and board.piece_at(chess.square(file, rank)).color != color
                    for rank in range(8)
            ):
                for rank in range(8):
                    piece = board.piece_at(chess.square(file, rank))
                    if piece and piece.piece_type == chess.ROOK and piece.color == color:
                        semi_open_lines += 1

        return open_lines * 20 + semi_open_lines * 10

    def spatial_advantage(self, board, color):
        """Оценка пространственного преимущества (число полей, контролируемых фигурами указанного цвета)."""
        control = 0
        for square in chess.SQUARES:
            attackers = board.attackers(color, square)
            if len(attackers) > 0:
                control += 1
        return control

    def evaluate_board(self, board):
        if board.is_checkmate():
            return -9999 if board.turn else 9999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        eval = 0
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 10000
        }

        # Материальная оценка
        for piece in chess.PIECE_TYPES:
            eval += len(board.pieces(piece, chess.WHITE)) * piece_values[piece]
            eval -= len(board.pieces(piece, chess.BLACK)) * piece_values[piece]

        # Пешечные структуры
        eval -= 20 * self.calculate_pawn_islands(board, chess.WHITE)
        eval += 20 * self.calculate_pawn_islands(board, chess.BLACK)

        eval -= 15 * self.calculate_isolated_pawns(board, chess.WHITE)
        eval += 15 * self.calculate_isolated_pawns(board, chess.BLACK)

        eval -= 10 * self.calculate_doubled_pawns(board, chess.WHITE)
        eval += 10 * self.calculate_doubled_pawns(board, chess.BLACK)

        # Контроль центра
        eval += 2 * self.center_control(board, chess.WHITE)
        eval -= 2 * self.center_control(board, chess.BLACK)

        # Пространственное преимущество
        eval += self.spatial_advantage(board, chess.WHITE) * 15
        eval -= self.spatial_advantage(board, chess.BLACK) * 15

        # Дебютные принципы
        if board.fullmove_number <= 10:  # Первые 10 ходов
            eval += self.evaluate_opening_principles(board, chess.WHITE)
            eval -= self.evaluate_opening_principles(board, chess.BLACK)

        # Контроль над открытыми линиями
        eval += self.control_of_open_lines(board, chess.WHITE)
        eval -= self.control_of_open_lines(board, chess.BLACK)

        # Развитие фигур
        for square in board.pieces(chess.KNIGHT, chess.WHITE):
            if chess.square_rank(square) >= 2:
                eval += 30
        for square in board.pieces(chess.KNIGHT, chess.BLACK):
            if chess.square_rank(square) <= 5:
                eval -= 30

        for square in board.pieces(chess.BISHOP, chess.WHITE):
            if chess.square_rank(square) >= 2:
                eval += 20
        for square in board.pieces(chess.BISHOP, chess.BLACK):
            if chess.square_rank(square) <= 5:
                eval -= 20

        return eval

    def evaluate_opening_principles(self, board, color):
        """Оценивает соблюдение дебютных принципов."""
        score = 0

        # Бонус за контроль центра пешками
        center_pawn_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        for square in center_pawn_squares:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                score += 50

        # Бонус за развитие коней и слонов
        developed_knight_positions = [chess.C3, chess.F3, chess.C6, chess.F6]
        developed_bishop_positions = [chess.C4, chess.F4, chess.C5, chess.F5]

        for square in board.pieces(chess.KNIGHT, color):
            if square in developed_knight_positions:
                score += 30

        for square in board.pieces(chess.BISHOP, color):
            if square in developed_bishop_positions:
                score += 30

        # Штраф за ферзя в центре доски
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        for square in board.pieces(chess.QUEEN, color):
            if square in center_squares:
                score -= 1000  # Значительный штраф за ферзя в центре доски

        # Штраф за повторное движение одной фигуры
        piece_moves = {}
        for move in board.move_stack:
            piece = board.piece_at(move.from_square)
            if piece and piece.color == color:
                piece_moves[piece] = piece_moves.get(piece, 0) + 1

        for piece, moves in piece_moves.items():
            if moves > 1:
                score -= 20 * (moves - 1)  # Штраф за повторные ходы

        return score

    def threatens_mate(self, board, move):
        """
        Проверяет, создаёт ли ход угрозу мата.
        """
        board.push(move)
        is_threatening = any(board.is_checkmate() for move in board.legal_moves)
        board.pop()
        return is_threatening

    def sort_moves(self, board, moves, killer_moves, depth):
        def move_priority(move):
            score = 0
            piece = board.piece_at(move.from_square)

            # Штраф за ферзя в центре
            center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
            if piece and piece.piece_type == chess.QUEEN and move.to_square in center_squares:
                score -= 2000  # Повторяем штраф в сортировке

            # Приоритет хода пешек в центр
            if piece and piece.piece_type == chess.PAWN and move.to_square in center_squares:
                score += 300

            # Приоритет развития лёгких фигур
            developed_positions = [chess.C3, chess.F3, chess.C6, chess.F6, chess.C4, chess.F4, chess.C5, chess.F5]
            if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP] and move.to_square in developed_positions:
                score += 200

            # Захват фигуры
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    score += 1000 + captured_piece.piece_type * 100

            return score

        return sorted(moves, key=move_priority, reverse=True)

    def store_transposition(self, board_fen, depth, eval, best_move):
        """
        Сохраняет позицию в таблице транспозиции.
        """
        self.transposition_table[board_fen] = {
            'eval': eval,
            'depth': depth,
            'best_move': best_move
        }

    def minimax(self, board, depth, alpha, beta, maximizing_player, previous_best_move=None):
        """
        Реализация минимакса с альфа-бета отсечением и использованием транспозиционной таблицы.
        """
        board_fen = board.fen()

        # Проверяем транспозиционную таблицу
        if board_fen in self.transposition_table:
            transposition = self.transposition_table[board_fen]
            if transposition['depth'] >= depth:
                return transposition['eval'], transposition.get('best_move')

        # Проверка на окончание игры или максимальную глубину
        if depth == 0 or board.is_game_over():
            eval = self.evaluate_board(board)
            self.store_transposition(board_fen, depth, eval, None)
            return eval, None

        best_move = None
        moves = list(board.legal_moves)

        # Сортируем ходы
        if previous_best_move and previous_best_move in moves:
            # Проверяем лучший ход из предыдущей итерации первым
            moves.insert(0, moves.pop(moves.index(previous_best_move)))

        moves = self.sort_moves(board, moves, self.killer_moves, depth)

        if maximizing_player:
            max_eval = -math.inf
            for move in moves:
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, False, best_move)
                board.pop()

                if eval > max_eval:
                    max_eval = eval
                    best_move = move

                alpha = max(alpha, eval)
                if alpha >= beta:
                    # Сохраняем "убийственный" ход
                    self.killer_moves.setdefault(depth, []).append(move)
                    break

            # Сохраняем в таблицу транспозиции
            self.store_transposition(board_fen, depth, max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in moves:
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, True, best_move)
                board.pop()

                if eval < min_eval:
                    min_eval = eval
                    best_move = move

                beta = min(beta, eval)
                if beta <= alpha:
                    self.killer_moves.setdefault(depth, []).append(move)
                    break

            # Сохраняем в таблицу транспозиции
            self.store_transposition(board_fen, depth, min_eval, best_move)
            return min_eval, best_move

    def find_best_move(self, board, max_time=5):
        start_time = time.time()
        best_move = None

        for depth in range(1, self.depth + 1):
            if time.time() - start_time > max_time:
                break
            _, move = self.minimax(board, depth, -math.inf, math.inf, board.turn,
                                   best_move if best_move in board.legal_moves else None)
            if move:
                best_move = move

        return best_move
