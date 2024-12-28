import sqlite3
import os

class ChessDatabaseMigration:
    def __init__(self, old_db_path, new_db_path):
        self.old_db_path = old_db_path
        self.new_db_path = new_db_path
        os.makedirs(os.path.dirname(new_db_path), exist_ok=True)
        self.old_conn = sqlite3.connect(old_db_path)
        self.new_conn = sqlite3.connect(new_db_path)

    def create_new_tables(self):
        """Создаем новую структуру базы данных."""
        with self.new_conn:
            # Таблица для дебютов
            self.new_conn.execute('''
                CREATE TABLE IF NOT EXISTS OpeningsMain (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_en TEXT NOT NULL,
                    name_ru TEXT NOT NULL,
                    UNIQUE(name_en, name_ru)  -- Уникальность для предотвращения дубликатов
                )
            ''')

            # Таблица для вариантов дебютов (без привязки к дебютам)
            self.new_conn.execute('''
                CREATE TABLE IF NOT EXISTS OpeningVariations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    variation_name_en TEXT NOT NULL,
                    variation_name_ru TEXT NOT NULL,
                    UNIQUE(variation_name_en, variation_name_ru)  -- Уникальность вариаций
                )
            ''')

            # Основная таблица для дебютов с их ходами и FEN
            self.new_conn.execute('''
                CREATE TABLE IF NOT EXISTS Openings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opening_id INTEGER NOT NULL,
                    variation_id INTEGER,
                    move TEXT NOT NULL,
                    fen TEXT NOT NULL UNIQUE,  -- Уникальность для FEN
                    FOREIGN KEY (opening_id) REFERENCES OpeningsMain (id),
                    FOREIGN KEY (variation_id) REFERENCES OpeningVariations (id)
                )
            ''')

    def migrate_data(self):
        """Мигрируем данные из старой базы данных в новую."""
        cursor_old = self.old_conn.cursor()
        cursor_old.execute('SELECT * FROM Openings')

        # Начинаем транзакцию
        self.new_conn.isolation_level = None  # Отключаем авто-коммит
        cursor_new = self.new_conn.cursor()
        cursor_new.execute('BEGIN TRANSACTION;')  # Явное начало транзакции

        # Обработка всех записей из старой таблицы
        for row in cursor_old.fetchall():
            name_en = row[1]
            name_ru = row[2]
            parents = row[3]
            move = row[4]
            fen = row[5]

            # Разбираем дебют и вариант из текущей строки
            opening_name_en, variation_name_en = name_en.split(":", 1) if ":" in name_en else (name_en, "")
            opening_name_ru, variation_name_ru = name_ru.split(":", 1) if ":" in name_ru else (name_ru, "")

            # Проверяем, существует ли дебют в базе данных
            try:
                cursor_new.execute('''INSERT INTO OpeningsMain (name_en, name_ru) VALUES (?, ?)''', 
                                   (opening_name_en.strip(), opening_name_ru.strip()))
                opening_id = cursor_new.lastrowid  # Получаем ID дебюта
            except sqlite3.IntegrityError:
                # Если запись уже существует, получаем ее ID
                cursor_new.execute('''SELECT id FROM OpeningsMain WHERE name_en = ? AND name_ru = ?''', 
                                   (opening_name_en.strip(), opening_name_ru.strip()))
                opening_id = cursor_new.fetchone()[0]

            # Проверяем, существует ли вариант дебюта
            if not variation_name_en.strip() and not variation_name_ru.strip():
                variation_id = None  # Пропускаем пустые варианты
            else:
                try:
                    cursor_new.execute('''INSERT INTO OpeningVariations (variation_name_en, variation_name_ru) VALUES (?, ?)''', 
                                       (variation_name_en.strip(), variation_name_ru.strip()))
                    variation_id = cursor_new.lastrowid  # Получаем ID варианта
                except sqlite3.IntegrityError:
                    # Если запись уже существует, получаем ее ID
                    cursor_new.execute('''SELECT id FROM OpeningVariations WHERE variation_name_en = ? AND variation_name_ru = ?''', 
                                       (variation_name_en.strip(), variation_name_ru.strip()))
                    variation_id = cursor_new.fetchone()[0]

            # Проверяем, существует ли запись с данным FEN
            cursor_new.execute('''SELECT id FROM Openings WHERE fen = ?''', (fen,))
            existing_fen = cursor_new.fetchone()

            if existing_fen:
                continue  # Пропускаем запись, если FEN уже есть

            # Вставляем запись с ходами и FEN в таблицу Openings
            cursor_new.execute('''INSERT INTO Openings (opening_id, variation_id, move, fen) VALUES (?, ?, ?, ?)''', 
                               (opening_id, variation_id, move, fen))

        # Завершаем транзакцию
        self.new_conn.commit()

    def close(self):
        """Закрываем соединения с базами данных."""
        self.old_conn.close()
        self.new_conn.close()

def main():
    old_db_path = "data/openings/old_chess_openings.db"
    new_db_path = "data/openings/chess_openings.db"
    
    migration = ChessDatabaseMigration(old_db_path, new_db_path)
    migration.create_new_tables()
    migration.migrate_data()
    migration.close()
    print("Миграция завершена!")

if __name__ == "__main__":
    main()
