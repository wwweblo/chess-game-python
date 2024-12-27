import chess
from typing import Optional
from database import ChessDatabase  # Импортируем класс базы данных


def get_opening_name() -> tuple:
    """Запрашивает у пользователя название дебюта на английском и русском языках."""
    print("Дебют не найден в базе данных.")
    name_en = input("Введите название дебюта на английском: ").strip()
    name_ru = input("Введите название дебюта на русском: ").strip()
    return name_en, name_ru


def get_variation_name() -> Optional[tuple]:
    """Запрашивает у пользователя название варианта дебюта на английском и русском языках."""
    print("Введите название варианта дебюта (если есть). Нажмите Enter, чтобы пропустить.")
    variation_name_en = input("Название варианта на английском: ").strip()
    variation_name_ru = input("Название варианта на русском: ").strip()
    if variation_name_en or variation_name_ru:
        return variation_name_en, variation_name_ru
    return None


def main():
    db_path = "data/openings/new_chess_openings.db"
    with ChessDatabase(db_path) as db:
        board = chess.Board()
        move_history = []

        while not board.is_game_over():
            print(board)
            print("-" * 30)
            print("Введите ваш ход в формате SAN (например, Nf3) или 'back' для отмены последнего хода:")
            user_input = input("Ход: ").strip()

            if user_input.lower() == 'back':
                if move_history:
                    board.pop()
                    move_history.pop()
                    print("Последний ход отменен.")
                else:
                    print("Нет ходов для отмены.")
                continue

            try:
                move = board.parse_san(user_input)
                if move in board.legal_moves:
                    board.push(move)
                    move_history.append(user_input)

                    # Получаем текущий FEN и проверяем, есть ли он в базе данных
                    fen = board.fen()
                    opening_name = db.get_full_opening_name_by_fen(fen)

                    if opening_name == "Unknown Position" or opening_name == "Неизвестная позиция":
                        print("Позиция не найдена в базе данных.")
                        # Запрашиваем название дебюта
                        name_en, name_ru = get_opening_name()

                        # Добавляем дебют, если его еще нет
                        opening_id = None
                        existing_openings = db.read_openings()
                        for opening in existing_openings:
                            if opening[1] == name_en and opening[2] == name_ru:
                                opening_id = opening[0]
                                break
                        if opening_id is None:
                            db.create_opening(name_en, name_ru)
                            opening_id = db.execute_query(
                                "SELECT id FROM OpeningsMain WHERE name_en = ? AND name_ru = ?",
                                (name_en, name_ru),
                                fetchone=True
                            )[0]

                        # Запрашиваем название варианта
                        variation = get_variation_name()
                        variation_id = None
                        if variation:
                            variation_name_en, variation_name_ru = variation
                            db.create_variation(opening_id, variation_name_en, variation_name_ru)
                            variation_id = db.execute_query(
                                "SELECT id FROM OpeningVariations WHERE variation_name_en = ? AND variation_name_ru = ?",
                                (variation_name_en, variation_name_ru),
                                fetchone=True
                            )[0]

                        # Добавляем запись с FEN
                        move_str = ",".join(move_history)
                        db.create_opening_record(opening_id, variation_id, move_str, fen)
                        print(f"Дебют \"{name_en}\" (\"{name_ru}\") добавлен в базу данных.")
                    else:
                        # Разбиваем вывод на английский и русский
                        opening_name_en, opening_name_ru = opening_name.split(':', 1) if ':' in opening_name else (opening_name, opening_name)
                        print(f"EN:{opening_name_en.strip()}\nRU:{opening_name_ru.strip()}")
                else:
                    print("Недопустимый ход. Попробуйте снова.")
            except ValueError:
                print("Некорректный формат хода. Попробуйте снова.")

        print("Игра завершена!")


if __name__ == "__main__":
    main()
