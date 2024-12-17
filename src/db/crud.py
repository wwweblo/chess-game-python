import sqlite3

def connect_db(db_path):
    """Подключается к базе данных и возвращает соединение."""
    return sqlite3.connect(db_path)

def create_opening(conn, name_en, name_ru, parents, move, fen):
    """Добавляет новый дебют в базу данных."""
    with conn:
        conn.execute('''
            INSERT INTO Openings (name_en, name_ru, parents, move, fen)
            VALUES (?, ?, ?, ?, ?)
        ''', (name_en, name_ru, parents, move, fen))
    print(f"Дебют '{name_en}' добавлен.")

def read_all_openings(conn):
    """Возвращает все записи из таблицы Openings."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name_en, name_ru FROM Openings")
    return cursor.fetchall()

def search_openings_by_name(conn, name):
    """Ищет дебюты по имени (английскому или русскому)."""
    cursor = conn.cursor()
    query = f"%{name}%"
    cursor.execute("SELECT id, name_en, name_ru FROM Openings WHERE name_en LIKE ? OR name_ru LIKE ?", (query, query))
    return cursor.fetchall()

def update_opening(conn, opening_id, name_en=None, name_ru=None):
    """Обновляет название дебюта по ID."""
    with conn:
        if name_en:
            conn.execute("UPDATE Openings SET name_en = ? WHERE id = ?", (name_en, opening_id))
        if name_ru:
            conn.execute("UPDATE Openings SET name_ru = ? WHERE id = ?", (name_ru, opening_id))
    print(f"Дебют с ID {opening_id} обновлен.")

def delete_opening(conn, opening_id):
    """Удаляет дебют из базы данных по ID."""
    with conn:
        conn.execute("DELETE FROM Openings WHERE id = ?", (opening_id,))
    print(f"Дебют с ID {opening_id} удален.")

def display_openings_as_table(openings):
    """Отображает записи в формате таблицы."""
    if not openings:
        print("Данные не найдены.")
        return

    column_widths = [5, 30, 30]
    header = f"{'ID'.ljust(column_widths[0])} | {'Название (EN)'.ljust(column_widths[1])} | {'Название (RU)'.ljust(column_widths[2])}"
    separator = "-" * len(header)
    print(header)
    print(separator)

    for opening in openings:
        row = f"{str(opening[0]).ljust(column_widths[0])} | {opening[1].ljust(column_widths[1])} | {opening[2].ljust(column_widths[2])}"
        print(row)

def main():
    db_path = "data/openings/chess_openings.db"
    conn = connect_db(db_path)

    while True:
        print("\nВыберите действие:")
        print("1. Добавить новый дебют")
        print("2. Показать все дебюты")
        print("3. Найти дебют по названию")
        print("4. Обновить дебют")
        print("5. Удалить дебют")
        print("6. Выход")

        choice = input("Введите номер действия: ").strip()

        if choice == "1":
            name_en = input("Введите название дебюта на английском: ").strip()
            name_ru = input("Введите название дебюта на русском: ").strip()
            parents = input("Введите список родителей (через запятую): ").strip()
            move = input("Введите последовательность ходов (через запятую): ").strip()
            fen = input("Введите FEN для позиции: ").strip()
            create_opening(conn, name_en, name_ru, parents, move, fen)

        elif choice == "2":
            openings = read_all_openings(conn)
            display_openings_as_table(openings)

        elif choice == "3":
            search_term = input("Введите название дебюта для поиска: ").strip()
            results = search_openings_by_name(conn, search_term)
            display_openings_as_table(results)

        elif choice == "4":
            opening_id = input("Введите ID дебюта для обновления: ").strip()
            name_en = input("Введите новое название дебюта на английском (оставьте пустым, чтобы не менять): ").strip()
            name_ru = input("Введите новое название дебюта на русском (оставьте пустым, чтобы не менять): ").strip()
            update_opening(conn, opening_id, name_en or None, name_ru or None)

        elif choice == "5":
            opening_id = input("Введите ID дебюта для удаления: ").strip()
            delete_opening(conn, opening_id)

        elif choice == "6":
            print("Выход.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")

    conn.close()

if __name__ == "__main__":
    main()
