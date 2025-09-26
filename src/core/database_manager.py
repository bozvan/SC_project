import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple


class DatabaseManager:
    """Класс для управления всеми операциями с базой данных."""

    def __init__(self, db_path: str = "smart_organizer.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Возвращает соединение с БД (создает если нужно)."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection

    def _init_db(self):
        """Инициализирует базу данных, создавая таблицы."""
        create_tables_queries = [
            # Таблица заметок
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Таблица тегов
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            """,
            # Таблица связи 'многие-ко-многим' между заметками и тегами
            """
            CREATE TABLE IF NOT EXISTS note_tag_relation (
                note_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
            """
        ]

        conn = self._get_connection()
        cursor = conn.cursor()
        for query in create_tables_queries:
            cursor.execute(query)
        conn.commit()
        print(f"База данных инициализирована: {self.db_path}")

    # --- Методы для работы с заметками ---
    def create_note(self, title: str, content: str) -> Optional[int]:
        """Создает новую заметку и возвращает её ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (title, content) VALUES (?, ?)",
                (title, content)
            )
            conn.commit()
            return cursor.lastrowid  # Возвращает ID новой заметки
        except sqlite3.Error as e:
            print(f"Ошибка при создании заметки: {e}")
            return None

    def get_all_notes(self) -> List[Tuple]:
        """Возвращает список всех заметок."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении заметок: {e}")
            return []

    def get_note_by_id(self, note_id: int) -> Optional[Tuple]:
        """Возвращает заметку по ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка при получении заметки: {e}")
            return None

    def search_notes(self, search_term: str) -> List[Tuple]:
        """Ищет заметки по заголовку и содержимому."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            search_pattern = f"%{search_term}%"
            cursor.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC",
                (search_pattern, search_pattern)
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при поиске заметок: {e}")
            return []

    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Обновляет существующую заметку."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (title, content, note_id)
            )
            conn.commit()
            return cursor.rowcount > 0  # True если заметка была обновлена
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении заметки: {e}")
            return False

    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку по ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0  # True, если заметка была удалена
        except sqlite3.Error as e:
            print(f"Ошибка при удалении заметки: {e}")
            return False

    def close(self):
        """Закрывает соединение с БД."""
        if self.connection:
            self.connection.close()
            self.connection = None

    # --- Методы для работы с тегами (пока заглушки) ---
    def create_tag(self, name: str) -> Optional[int]:
        """Создает новый тег и возвращает его ID."""
        # TODO: Реализовать когда понадобится
        pass

    def get_note_tags(self, note_id: int) -> List[Tuple]:
        """Возвращает теги для указанной заметки."""
        # TODO: Реализовать когда понадобится
        return []
