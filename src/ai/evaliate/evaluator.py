# evaluator.py

from tabulate import tabulate
from ai.evaliate.evaluator_utils import *

# Глобальная переменная для отслеживания вывода заголовков для каждой фазы игры
header_printed = {
    "opening": False,
    "middlegame": False,
    "endgame": False
}

def evaluate_board(board, logging=False, move=None):
    """
    Оценка позиции в зависимости от стадии игры и тактических угроз.
    """
    phase = determine_game_phase(board)
    
    # Оценка фазы игры
    if phase == "opening":
        phase_score, phase_details = evaluate_opening(board, logging, move)
    elif phase == "middlegame":
        phase_score, phase_details = evaluate_middlegame(board, logging, move)
    elif phase == "endgame":
        phase_score, phase_details = evaluate_endgame(board, logging, move)
    else:
        phase_score, phase_details = 0, {}

    # Оценка тактических угроз
    x_ray_score = evaluate_x_ray(board)
    hidden_attack_score = evaluate_hidden_attacks(board)
    
    # Общая оценка позиции с учётом тактических угроз
    total_score = phase_score + x_ray_score + hidden_attack_score
    details = {
        **phase_details,
        'Оценка рентгена': x_ray_score,
        'Оценка скрытых атак': hidden_attack_score,
        'Общая оценка': total_score
    }

    if logging and move:
        print_evaluation_table(details, move, phase=phase)

    return total_score, details


def evaluate_opening(board, logging=False, move=None):
    """
    Оценка позиции в дебюте.
    """
    material_score = evaluate_material(board)
    king_safety_score = evaluate_king_safety(board)
    piece_development_score = evaluate_piece_development(board)
    center_control_score = evaluate_center_control(board) + evaluate_center_pawns(board)  # Улучшенная оценка контроля центра
    castling_score = evaluate_castling(board)
    piece_safety_score = evaluate_piece_safety(board)
    mobility_score = evaluate_mobility(board)

    total_score = (1.0 * material_score +
                   0.8 * king_safety_score +
                   1.0 * piece_development_score +  # Повышенная оценка развития фигур
                   2.0 * center_control_score +  # Повышенная оценка контроля центра
                   0.5 * castling_score +
                   0.5 * piece_safety_score +
                   0.5 * mobility_score)

    details = {
        'Материальная оценка': material_score,
        'Безопасность короля': king_safety_score,
        'Развитие фигур': piece_development_score,
        'Контроль центра': center_control_score,
        'Оценка рокировки': castling_score,
        'Оценка защищенности фигур': piece_safety_score,
        'Оценка мобильности': mobility_score,
        'Общая оценка (Дебют)': total_score
    }

    if logging and move:
        print_evaluation_table(details, move, phase="opening")

    return total_score, details

def evaluate_middlegame(board, logging=False, move=None):
    """
    Оценка позиции в миттельшпиле.
    """
    material_score = evaluate_material(board)
    piece_activity_score = evaluate_piece_activity(board)
    mobility_score = evaluate_mobility(board)
    attacking_chances_score = evaluate_attacking_chances(board)
    king_safety_score = evaluate_king_safety(board)

    total_score = (1.0 * material_score +
                   1.0 * piece_activity_score +
                   0.8 * mobility_score +
                   1.0 * attacking_chances_score +
                   1.2 * king_safety_score)

    details = {
        'Материальная оценка': material_score,
        'Активность фигур': piece_activity_score,
        'Мобильность': mobility_score,
        'Шансы на атаку': attacking_chances_score,
        'Безопасность короля': king_safety_score,
        'Общая оценка (Миттельшпиль)': total_score
    }

    if logging and move:
        print_evaluation_table(details, move, phase="middlegame")

    return total_score, details

def evaluate_endgame(board, logging=False, move=None):
    """
    Оценка позиции в эндшпиле.
    """
    material_score = evaluate_material(board)
    king_activity_score = evaluate_king_activity(board)
    pawn_structure_score = evaluate_pawn_structure(board)

    total_score = (1.0 * material_score +
                   1.5 * king_activity_score +
                   1.2 * pawn_structure_score)

    details = {
        'Материальная оценка': material_score,
        'Активность короля': king_activity_score,
        'Структура пешек': pawn_structure_score,
        'Общая оценка (Эндшпиль)': total_score
    }

    if logging and move:
        print_evaluation_table(details, move, phase="endgame")

    return total_score, details

def print_evaluation_table(details, move, phase):
    """Функция для вывода таблицы логирования с общей оценкой."""
    global header_printed

    # Подготовка данных для строки таблицы
    row = [
        move,
        details.get('Материальная оценка', 'N/A'),
        details.get('Безопасность короля', 'N/A'),
        details.get('Развитие фигур', 'N/A'),
        details.get('Контроль центра', 'N/A'),
        details.get('Оценка рокировки', 'N/A'),
        details.get('Оценка защищенности фигур', 'N/A'),
        details.get('Оценка мобильности', 'N/A'),
        details.get('Общая оценка (Дебют)', 'N/A'),
        details.get('Активность фигур', 'N/A'),
        details.get('Мобильность', 'N/A'),
        details.get('Шансы на атаку', 'N/A'),
        details.get('Активность короля', 'N/A'),
        details.get('Структура пешек', 'N/A'),
        details.get(f'Общая оценка ({phase.capitalize()})', 'N/A')
    ]

    # Заголовки для таблицы в зависимости от фазы игры
    if phase == "opening":
        headers = [
            "Ход", "Материальная оценка", "Безопасность короля", "Развитие фигур", "Контроль центра", 
            "Оценка рокировки", "Оценка защищенности фигур", "Оценка мобильности", "Общая оценка (Дебют)"
        ]
    elif phase == "middlegame":
        headers = [
            "Ход", "Материальная оценка", "Активность фигур", "Мобильность", "Шансы на атаку", 
            "Безопасность короля", "Общая оценка (Миттельшпиль)"
        ]
    elif phase == "endgame":
        headers = [
            "Ход", "Материальная оценка", "Активность короля", "Структура пешек", 
            "Общая оценка (Эндшпиль)"
        ]

    # Выводим заголовок таблицы только один раз на фазу игры
    if not header_printed[phase]:
        print(tabulate([], headers=headers, tablefmt='orgtbl'))
        header_printed[phase] = True  # Обновляем статус после вывода заголовка

    # Вывод строки с оценками
    print(tabulate([row], tablefmt='orgtbl'))

