import os
import sqlite3
import logging
from typing import Tuple, List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class ChessDatabase:
    def __init__(self, db_path: str):
        """
        Инициализация базы данных. Создает соединение с базой данных
        и вызывает метод для создания таблиц, если их нет.
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)  # Создание соединения
        self.create_tables()  # Создание таблиц

    def __enter__(self):
        """
        Поддержка контекстного менеджера. Возвращает объект базы данных.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Закрытие соединения при выходе из контекста.
        """
        self.conn.close()

    def create_tables(self):
        """
        Создает таблицы базы данных, если они еще не существуют.
        """
        with self.conn:
            logging.info("Создание таблиц, если они отсутствуют...")
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS OpeningsMain (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_en TEXT NOT NULL,
                    name_ru TEXT
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS OpeningVariations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opening_id INTEGER NOT NULL,
                    variation_name_en TEXT,
                    variation_name_ru TEXT,
                    FOREIGN KEY (opening_id) REFERENCES OpeningsMain (id)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS Openings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opening_id INTEGER NOT NULL,
                    variation_id INTEGER,
                    move TEXT NOT NULL,
                    fen TEXT NOT NULL UNIQUE,
                    FOREIGN KEY (opening_id) REFERENCES OpeningsMain (id),
                    FOREIGN KEY (variation_id) REFERENCES OpeningVariations (id)
                )
            ''')

    def execute_query(self, query: str, params: Tuple = (), fetchone: bool = False, fetchall: bool = False):
        """
        Универсальный метод для выполнения SQL-запросов.
        :param query: SQL-запрос.
        :param params: Параметры для запроса.
        :param fetchone: Возвращать одну запись.
        :param fetchall: Возвращать все записи.
        :return: Результат запроса (одна или несколько записей) или None.
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        if fetchone:
            return cursor.fetchone()
        elif fetchall:
            return cursor.fetchall()
        self.conn.commit()

    def create_opening(self, name_en: str, name_ru: str):
        """
        Создает запись дебюта.
        :param name_en: Название дебюта на английском.
        :param name_ru: Название дебюта на русском.
        """
        query = 'INSERT INTO OpeningsMain (name_en, name_ru) VALUES (?, ?)'
        self.execute_query(query, (name_en, name_ru))
        logging.info(f"Создан дебют: {name_en} ({name_ru})")

    def read_openings(self) -> List[Tuple]:
        """
        Возвращает все дебюты.
        :return: Список всех дебютов.
        """
        query = 'SELECT * FROM OpeningsMain'
        return self.execute_query(query, fetchall=True)

    def update_opening(self, opening_id: int, name_en: str, name_ru: str):
        """
        Обновляет запись дебюта.
        :param opening_id: ID дебюта.
        :param name_en: Новое название дебюта на английском.
        :param name_ru: Новое название дебюта на русском.
        """
        query = 'UPDATE OpeningsMain SET name_en = ?, name_ru = ? WHERE id = ?'
        self.execute_query(query, (name_en, name_ru, opening_id))
        logging.info(f"Обновлен дебют ID {opening_id}: {name_en} ({name_ru})")

    def delete_opening(self, opening_id: int):
        """
        Удаляет запись дебюта.
        :param opening_id: ID дебюта.
        """
        query = 'DELETE FROM OpeningsMain WHERE id = ?'
        self.execute_query(query, (opening_id,))
        logging.info(f"Удален дебют ID {opening_id}")

    def get_full_opening_name_by_fen(self, fen: str, language: str = 'EN') -> str:
        """
        Возвращает полное название дебюта (включая вариант) по FEN.
        :param fen: Позиция в формате FEN.
        :param language: Язык ('EN' или 'RU').
        :return: Строка с названием дебюта или "Unknown Position" / "Неизвестная позиция".
        """
        query = '''
            SELECT om.name_en, om.name_ru, ov.variation_name_en, ov.variation_name_ru
            FROM Openings o
            LEFT JOIN OpeningsMain om ON o.opening_id = om.id
            LEFT JOIN OpeningVariations ov ON o.variation_id = ov.id
            WHERE o.fen = ?
        '''
        result = self.execute_query(query, (fen,), fetchone=True)
        if not result:
            return "Unknown Position" if language == 'EN' else "Неизвестная позиция"

        opening_name_en, opening_name_ru, variation_name_en, variation_name_ru = result
        if language == 'EN':
            return f"{opening_name_en}: {variation_name_en}" if variation_name_en else opening_name_en
        else:
            return f"{opening_name_ru}: {variation_name_ru}" if variation_name_ru else opening_name_ru

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        self.conn.close()
