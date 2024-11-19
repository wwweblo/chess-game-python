# evaluator_utils.py

import chess

def get_piece_value(piece):
    """
    Возвращает ценность фигуры.
    
    Параметры:
        piece (chess.Piece): фигура, для которой возвращается ценность.
    
    Возвращает:
        int: стоимость фигуры.
    """
    if piece is None:
        return 0
    
    value_map = {
        chess.PAWN: 100,
        chess.KNIGHT: 310,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 100000  # Условная высокая цена для короля
    }
    
    return value_map.get(piece.piece_type, 0)

def determine_game_phase(board):
    """
    Определение стадии игры на основе количества ходов и наличия фигур на доске.
    """
    if len(board.move_stack) <= 20:
        return "opening"
    elif len(list(board.pieces(chess.QUEEN, chess.WHITE))) == 0 and len(list(board.pieces(chess.QUEEN, chess.BLACK))) == 0:
        return "endgame"
    else:
        return "middlegame"

def control_of_open_lines(board, piece_type, color):
        """Возвращает оценку контроля открытых линий (для ладей)."""
        open_lines = 0
        for file in range(8):
            if not any(board.piece_at(chess.square(file, rank)) for rank in range(8)):
                # Открытая линия, если нет пешек
                if any(board.piece_at(chess.square(file, rank)) and board.piece_at(chess.square(file, rank)).piece_type == piece_type and board.piece_at(chess.square(file, rank)).color == color for rank in range(8)):
                    open_lines += 1
        return open_lines

def evaluate_piece_safety(board):
    """
    Оценка защищенности фигур: штраф за незащищенные фигуры.
    """
    safety_score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                if not board.is_attacked_by(chess.WHITE, square) and board.is_attacked_by(chess.BLACK, square):
                    safety_score -= 50  # Белая фигура под атакой, но не защищена
            else:
                if not board.is_attacked_by(chess.BLACK, square) and board.is_attacked_by(chess.WHITE, square):
                    safety_score += 50  # Черная фигура под атакой, но не защищена
    return safety_score

def is_kingside_safe(board, color):
        # Пример проверки безопасности рокировки на королевский фланг
        if color == chess.WHITE:
            return not board.is_attacked_by(chess.BLACK, chess.F1) and not board.is_attacked_by(chess.BLACK, chess.G1)
        else:
            return not board.is_attacked_by(chess.WHITE, chess.F8) and not board.is_attacked_by(chess.WHITE, chess.G8)

def is_queenside_safe(board, color):
        # Пример проверки безопасности рокировки на ферзевый фланг
        if color == chess.WHITE:
            return not board.is_attacked_by(chess.BLACK, chess.C1) and not board.is_attacked_by(chess.BLACK, chess.D1)
        else:
            return not board.is_attacked_by(chess.WHITE, chess.C8) and not board.is_attacked_by(chess.WHITE, chess.D8)

def spatial_advantage(board, color):
        """Оценка пространственного преимущества (число полей, контролируемых фигурами указанного цвета)."""
        control = 0
        for square in chess.SQUARES:
            attackers = board.attackers(color, square)
            if len(attackers) > 0:
                control += 1
        return control

def center_control(board, color):
    eval = 0
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    
    # Очки за фигуры на центральных полях
    for square in center_squares:
        piece = board.piece_at(square)
        if piece:
            if piece.color == color:
                eval += 30  # Высокие очки за фигуры на центре
            else:
                eval -= 30
    
    # Очки за контроль над центральными полями
    for square in center_squares:
        attackers = board.attackers(color, square)
        for attacker in attackers:
            eval += 10  # Меньшие очки за контроль

        defenders = board.attackers(not color, square)
        for defender in defenders:
            eval -= 10
    
    return eval

def get_game_stage(board):

    if len(board.move_stack) < 15:  # Opening
        return 'opening'
    elif len(board.move_stack) < 30:  # Middle game
        return 'middle game'
    else:  # Endgame
        return 'endgame'
    
def evaluate_material(board):
    """
    Оценка материала на доске.
    """
    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            piece_value = get_piece_value(piece)
            if piece.color == chess.WHITE:
                score += piece_value
            else:
                score -= piece_value

    return score

def evaluate_mobility(board):
    """
    Оценка мобильности фигур: разница в количестве возможных ходов у белых и черных.
    """
    white_moves = len([move for move in board.legal_moves if board.piece_at(move.from_square) and board.piece_at(move.from_square).color == chess.WHITE])
    black_moves = len([move for move in board.legal_moves if board.piece_at(move.from_square) and board.piece_at(move.from_square).color == chess.BLACK])

    return white_moves - black_moves

def evaluate_center_control(board):
    """
    Оценка контроля центра.
    """
    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    white_control = sum([1 for square in center_squares if board.is_attacked_by(chess.WHITE, square)])
    black_control = sum([1 for square in center_squares if board.is_attacked_by(chess.BLACK, square)])

    return white_control - black_control

def evaluate_king_safety(board):
    """
    Оценка безопасности короля.
    """
    # Пример упрощенной оценки короля
    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)

    white_safety = 0 if white_king else -500  # Условная оценка безопасности белого короля
    black_safety = 0 if black_king else -500  # Условная оценка безопасности черного короля

    return white_safety - black_safety

def evaluate_material(board):
    """
    Оценка материального баланса.
    Возвращает сумму ценностей всех фигур на доске.
    """
    material_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 1000  # Король фактически не теряется, но можно оценить его безопасность
    }

    white_material = sum(material_values[piece.piece_type] for piece in board.piece_map().values() if piece.color == chess.WHITE)
    black_material = sum(material_values[piece.piece_type] for piece in board.piece_map().values() if piece.color == chess.BLACK)

    return white_material - black_material

def evaluate_center_control(board):
    """
    Оценка контроля над центром.
    Возвращает оценку на основе количества фигур, контролирующих центральные поля (D4, E4, D5, E5).
    """
    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    control_bonus = {chess.PAWN: 10, chess.KNIGHT: 20, chess.BISHOP: 20, chess.ROOK: 15, chess.QUEEN: 25}

    white_control = 0
    black_control = 0

    for square in center_squares:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                white_control += control_bonus.get(piece.piece_type, 0)
            else:
                black_control += control_bonus.get(piece.piece_type, 0)

    return white_control - black_control

def evaluate_king_safety(board):
    """
    Оценка безопасности короля.
    Возвращает штраф за открытую позицию короля.
    """
    safety_penalty = 0
    king_positions = [board.king(chess.WHITE), board.king(chess.BLACK)]

    # Оценка короля для каждого цвета
    for king_square in king_positions:
        if king_square:
            if board.is_attacked_by(chess.BLACK, king_square):
                safety_penalty -= 50  # Штраф за небезопасность белого короля
            if board.is_attacked_by(chess.WHITE, king_square):
                safety_penalty += 50  # Штраф за небезопасность черного короля

    return safety_penalty

def evaluate_piece_development(board):
    """
    Оценка развития фигур.
    Возвращает бонус за развитые фигуры и штраф за фигуры, остающиеся на начальных позициях.
    """
    development_bonus = {chess.KNIGHT: 35, chess.BISHOP: 20, chess.ROOK: 10}

    white_development = 0
    black_development = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Развитие белых
            if piece.color == chess.WHITE:
                if square not in [chess.B1, chess.G1, chess.C1, chess.F1]:  # Штраф за начальные позиции
                    white_development += development_bonus.get(piece.piece_type, 0)
            # Развитие черных
            if piece.color == chess.BLACK:
                if square not in [chess.B8, chess.G8, chess.C8, chess.F8]:
                    black_development += development_bonus.get(piece.piece_type, 0)

    return white_development - black_development

def evaluate_piece_activity(board):
    """
    Оценка активности фигур.
    Возвращает бонус за активные фигуры, находящиеся в центре или контролирующие ключевые поля.
    """
    activity_bonus = {chess.KNIGHT: 10, chess.BISHOP: 10, chess.ROOK: 15, chess.QUEEN: 25}

    white_activity = 0
    black_activity = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                if square in [chess.D4, chess.E4, chess.D5, chess.E5]:  # Центральные поля
                    white_activity += activity_bonus.get(piece.piece_type, 0)
            if piece.color == chess.BLACK:
                if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                    black_activity += activity_bonus.get(piece.piece_type, 0)

    return white_activity - black_activity

def evaluate_attacking_chances(board):
    """
    Оценка атакующих возможностей.
    Возвращает бонус за атакующие фигуры, особенно ферзей, слонов и ладьи.
    """
    attacking_bonus = {chess.QUEEN: 50, chess.ROOK: 30, chess.BISHOP: 20, chess.KNIGHT: 20}

    white_attack = 0
    black_attack = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE and board.is_attacked_by(chess.WHITE, square):
                white_attack += attacking_bonus.get(piece.piece_type, 0)
            if piece.color == chess.BLACK and board.is_attacked_by(chess.BLACK, square):
                black_attack += attacking_bonus.get(piece.piece_type, 0)

    return white_attack - black_attack

def evaluate_king_activity(board):
    """
    Оценка активности короля в эндшпиле.
    Возвращает бонус за активность короля (продвижение в центр в эндшпиле).
    """
    king_activity_bonus = 0

    # Проверяем позиции короля
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)

    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]

    if white_king_square in center_squares:
        king_activity_bonus += 50  # Бонус за продвижение белого короля в центр
    if black_king_square in center_squares:
        king_activity_bonus -= 50  # Бонус за продвижение черного короля

    return king_activity_bonus

def evaluate_pawn_structure(board):
    """
    Оценка структуры пешек.
    Возвращает штраф за изолированные или удвоенные пешки и бонус за цепи пешек.
    """
    pawn_structure_penalty = 0

    # Штрафы за слабую структуру пешек
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        files_with_pawns = [chess.square_file(pawn) for pawn in pawns]

        # Проверяем на удвоенные пешки (пешки на одном файле)
        for file in range(8):
            if files_with_pawns.count(file) > 1:
                pawn_structure_penalty += 30 if color == chess.WHITE else -30  # Штраф за удвоенные пешки

        # Проверяем на изолированные пешки (нет пешек на соседних файлах)
        for pawn in pawns:
            file = chess.square_file(pawn)
            if (file - 1 not in files_with_pawns) and (file + 1 not in files_with_pawns):
                pawn_structure_penalty += 20 if color == chess.WHITE else -20  # Штраф за изолированные пешки

    return pawn_structure_penalty

def evaluate_castling(board):
    """
    Оценка рокировки: поощрение за рокировку на безопасную сторону.
    """
    castling_score = 0

    if not board.has_castling_rights(chess.WHITE):
        if is_kingside_safe(board, chess.WHITE):
            castling_score += 50  # Белые успешно рокировались на королевский фланг
        elif is_queenside_safe(board, chess.WHITE):
            castling_score += 25  # Белые успешно рокировались на ферзевый фланг
    
    if not board.has_castling_rights(chess.BLACK):
        if is_kingside_safe(board, chess.BLACK):
            castling_score -= 50  # Черные успешно рокировались на королевский фланг
        elif is_queenside_safe(board, chess.BLACK):
            castling_score -= 25  # Черные успешно рокировались на ферзевый фланг

    return castling_score

def evaluate_center_pawns(board):
    """
    Оценка центральных пешек (на e4, d4, e5, d5).
    """
    central_pawns = [chess.E4, chess.D4, chess.E5, chess.D5]
    score = 0
    
    for square in central_pawns:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE:
                score += 50  # Высокая оценка за белые пешки в центре
            else:
                score -= 50  # Штраф за черные пешки в центре
    
    return score

def evaluate_x_ray(board):
    """
    Оценка рентгеновских атак, в которых фигуры скрытно атакуют или защищают друг друга.
    """
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == board.turn:
            for target_square in board.attacks(square):
                target_piece = board.piece_at(target_square)
                if target_piece and target_piece.color != piece.color:
                    score += 0.3  # Приоритетный вес для рентгеновской атаки
    return score

def evaluate_hidden_attacks(board):
    """
    Оценка скрытых атак, в которых фигура может неожиданно атаковать важную позицию при размене.
    """
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == board.turn:
            for target_square in board.attacks(square):
                target_piece = board.piece_at(target_square)
                if target_piece and target_piece.color != piece.color:
                    if is_hidden_attack(board, square, target_square):
                        score += 0.5  # Приоритетный вес для скрытой атаки
    return score

def is_hidden_attack(board, square, target_square):
    """
    Проверка, является ли данная атака скрытой, то есть атакующей при размене.
    """
    # Временное снятие фигуры для оценки скрытой атаки
    board.push(chess.Move(square, target_square))
    is_hidden = board.is_attacked_by(not board.turn, target_square)
    board.pop()
    return is_hidden
