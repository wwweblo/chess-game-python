from database import Database

class OpeningManager:
    def __init__(self, db: Database):
        """Инициализация менеджера дебютов."""
        self.db = db

    def add_opening(self, name, parents, move, fen):
        """Добавляет дебют в базу данных."""
        parents_str = ",".join(map(str, parents)) if parents else None
        self.db.execute("""
        INSERT INTO Openings (name, parents, move, fen)
        VALUES (?, ?, ?, ?);
        """, (name, parents_str, move, fen))
        print(f"Added opening: {name}")

    def get_opening(self, opening_id):
        """Получает дебют по ID."""
        result = self.db.execute("SELECT * FROM Openings WHERE id = ?;", (opening_id,))
        return result.fetchone()

    def get_children(self, parent_id):
        """Получает дочерние узлы для указанного ID родителя."""
        parent_str = str(parent_id)
        query = """
        SELECT * FROM Openings
        WHERE parents LIKE ? OR parents LIKE ? OR parents = ?;
        """
        return self.db.execute(query, (f"{parent_str},%", f"%,{parent_str},%", parent_str)).fetchall()

    def build_tree(self, root_id):
        """Построение дерева дебютов."""
        def recursive_tree(node_id):
            node = self.get_opening(node_id)
            if not node:
                return None

            children = self.get_children(node_id)
            return {
                "id": node[0],
                "name": node[1],
                "move": node[3],
                "fen": node[4],
                "children": [recursive_tree(child[0]) for child in children]
            }

        return recursive_tree(root_id)

    def delete_opening(self, opening_id):
        """Удаляет дебют из базы данных."""
        self.db.execute("DELETE FROM Openings WHERE id = ?;", (opening_id,))
        print(f"Deleted opening with ID: {opening_id}")

    def update_opening(self, opening_id, name=None, parents=None, move=None, fen=None):
        """Обновляет данные дебюта."""
        fields = []
        params = []

        if name:
            fields.append("name = ?")
            params.append(name)
        if parents is not None:
            fields.append("parents = ?")
            params.append(",".join(map(str, parents)) if parents else None)
        if move:
            fields.append("move = ?")
            params.append(move)
        if fen:
            fields.append("fen = ?")
            params.append(fen)

        params.append(opening_id)
        query = f"UPDATE Openings SET {', '.join(fields)} WHERE id = ?;"
        self.db.execute(query, params)
