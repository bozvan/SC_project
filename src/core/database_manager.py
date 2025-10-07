import sqlite3
import traceback
from pathlib import Path
from typing import List, Optional, Tuple


class DatabaseManager:
    """Класс для управления всеми операциями с базой данных."""

    def __init__(self, db_path: str = "smart_organizer.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Возвращает новое соединение с БД."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")  # Улучшаем производительность
            return conn
        except sqlite3.Error as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise

    def _init_db(self):
        """Инициализирует базу данных, создавая таблицы."""
        try:
            print(f"🔧 Инициализация БД по пути: {self.db_path}")
            print(f"🔧 Существует ли файл: {self.db_path.exists()}")
            create_tables_queries = [
                # Таблица заметок (остается без изменений)
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    content_type TEXT DEFAULT 'plain',
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
                # Таблица связи многие-ко-многим между заметками и тегами
                """
                CREATE TABLE IF NOT EXISTS note_tag_relation (
                    note_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (note_id, tag_id),
                    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                )
                """,
                # Таблица задач
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    due_date DATETIME NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
                )
                """,
                # НОВАЯ ТАБЛИЦА: Закладки (отдельно от заметок)
                """
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    favicon_url TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """,
                # Таблица связи многие-ко-многим между закладками и тегами
                """
                CREATE TABLE IF NOT EXISTS bookmark_tag_relation (
                    bookmark_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (bookmark_id, tag_id),
                    FOREIGN KEY (bookmark_id) REFERENCES bookmarks (id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                )
                """
            ]

            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Создаем таблицы
                for query in create_tables_queries:
                    cursor.execute(query)

                # Миграция: добавляем новые поля если их нет
                try:
                    cursor.execute("ALTER TABLE notes ADD COLUMN note_type TEXT DEFAULT 'note'")
                    print("✅ Добавлена колонка note_type в таблицу notes")
                except sqlite3.OperationalError:
                    pass

                try:
                    cursor.execute("ALTER TABLE notes ADD COLUMN url TEXT")
                    print("✅ Добавлена колонка url в таблицу notes")
                except sqlite3.OperationalError:
                    pass

                try:
                    cursor.execute("ALTER TABLE notes ADD COLUMN page_title TEXT")
                    print("✅ Добавлена колонка page_title в таблицу notes")
                except sqlite3.OperationalError:
                    pass

                try:
                    cursor.execute("ALTER TABLE notes ADD COLUMN page_description TEXT")
                    print("✅ Добавлена колонка page_description в таблицу notes")
                except sqlite3.OperationalError:
                    pass

                conn.commit()
                print(f"✅ База данных инициализирована: {self.db_path}")
        except Exception as e:
            print(f"❌ Критическая ошибка инициализации БД: {e}")
            traceback.print_exc()
            raise

    def migrate_database(self):
        """Миграция базы данных для добавления новых полей"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Добавляем content_type если не существует
                cursor.execute("PRAGMA table_info(notes)")
                columns = [column[1] for column in cursor.fetchall()]

                if 'content_type' not in columns:
                    cursor.execute("ALTER TABLE notes ADD COLUMN content_type TEXT DEFAULT 'plain'")
                    print("✅ Миграция: добавлена колонка content_type")

                conn.commit()
                print("✅ Миграция базы данных завершена")

        except Exception as e:
            print(f"❌ Ошибка миграции базы данных: {e}")

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
        """Закрывает все соединения с БД."""
        if hasattr(self, '_connection') and self._connection:
            try:
                self._connection.close()
                print("✅ Соединение с БД закрыто")
            except:
                pass
            finally:
                self._connection = None

    # --- Методы для работы с тегами (пока заглушки) ---
    def create_tag(self, name: str) -> Optional[int]:
        """Создает новый тег и возвращает его ID."""
        # TODO: Реализовать когда понадобится
        pass

    def get_note_tags(self, note_id: int) -> List[Tuple]:
        """Возвращает теги для указанной заметки."""
        # TODO: Реализовать когда понадобится
        return []
