import os
import sqlite3
import chess
import chess.pgn

class ChessDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS Openings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_en TEXT NOT NULL,
                    name_ru TEXT NOT NULL,
                    parents TEXT,
                    move TEXT NOT NULL,
                    fen TEXT NOT NULL
                )
            ''')

    def add_opening(self, name_en, name_ru, parents, move, fen):
        with self.conn:
            self.conn.execute('''
                INSERT INTO Openings (name_en, name_ru, parents, move, fen)
                VALUES (?, ?, ?, ?, ?)
            ''', (name_en, name_ru, parents, move, fen))

    def find_opening_by_fen(self, fen):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Openings WHERE fen = ?', (fen,))
        return cursor.fetchone()

    def update_opening_name(self, fen, name_en, name_ru):
        with self.conn:
            self.conn.execute('''
                UPDATE Openings
                SET name_en = ?, name_ru = ?
                WHERE fen = ?
            ''', (name_en, name_ru, fen))

    def close(self):
        self.conn.close()

def get_opening_name():
    """Запрашивает у пользователя название дебюта на английском и русском языках."""
    print("Дебют не найден в базе данных.")
    name_en = input("Введите название дебюта на английском: ")
    name_ru = input("Введите название дебюта на русском: ")
    return name_en, name_ru

def main():
    db_path = "data/openings/chess_openings.db"
    db = ChessDatabase(db_path)

    board = chess.Board()
    move_history = []

    while not board.is_game_over():
        print(board)
        print("Введите ваш ход в формате SAN (например, Nf3) или 'back' для отмены последнего хода, или 'rn' для переименования дебюта:")
        user_input = input("Ход: ").strip()

        if user_input.lower() == 'back':
            if move_history:
                board.pop()
                move_history.pop()
                print("Последний ход отменен.")
            else:
                print("Нет ходов для отмены.")
            continue

        if user_input.lower() == 'rn':
            fen = board.fen()
            opening = db.find_opening_by_fen(fen)

            if opening:
                print(f"Текущий дебют: EN: {opening[1]} | RU: {opening[2]}")
                name_en = input("Введите новое название дебюта на английском: ")
                name_ru = input("Введите новое название дебюта на русском: ")
                db.update_opening_name(fen, name_en, name_ru)
                print(f"Дебют обновлен: {name_en} (English), {name_ru} (Русский)")
            else:
                print("Дебют не найден в базе данных для текущей позиции.")
            continue
        try:
            move = board.parse_san(user_input)
            if move in board.legal_moves:
                board.push(move)
                move_history.append(user_input)

                # Проверяем, есть ли текущая позиция в базе данных
                fen = board.fen()
                opening = db.find_opening_by_fen(fen)

                if opening:
                    print(f"EN: {opening[1]}\nRU: {opening[2]}")
                else:
                    # Если дебют не найден, запрашиваем название у пользователя
                    name_en, name_ru = get_opening_name()
                    parents = ",".join(move_history[:-1])
                    move_str = ",".join(move_history)
                    db.add_opening(name_en, name_ru, parents, move_str, fen)
                    print(f"Дебют \"{name_en}\" (\"{name_ru}\") добавлен в базу данных.")

            else:
                print("Недопустимый ход. Попробуйте снова.")
        except ValueError:
            print("Некорректный формат хода. Попробуйте снова.")

    print("Игра завершена!")
    db.close()

if __name__ == "__main__":
    main()
