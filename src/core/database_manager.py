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
            conn.execute("PRAGMA journal_mode = WAL")
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
                # НОВАЯ ТАБЛИЦА: Рабочие пространства
                """
                CREATE TABLE IF NOT EXISTS workspaces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name)
                )
                """,
                # Таблица заметок (ОБНОВЛЕНА - добавлен workspace_id)
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    content_type TEXT DEFAULT 'plain',
                    note_type TEXT DEFAULT 'note',
                    url TEXT,
                    page_title TEXT,
                    page_description TEXT,
                    workspace_id INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (workspace_id) REFERENCES workspaces (id) ON DELETE SET DEFAULT
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
                # Таблица задач (ОБНОВЛЕНА - добавлен workspace_id)
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    priority TEXT DEFAULT 'medium' CHECK(priority IN ('high', 'medium', 'low')),
                    due_date DATETIME NULL,
                    workspace_id INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                    FOREIGN KEY (workspace_id) REFERENCES workspaces (id) ON DELETE SET DEFAULT
                )
                """,
                # Таблица закладок (ОБНОВЛЕНА - добавлен workspace_id)
                """
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    favicon_url TEXT,
                    workspace_id INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (workspace_id) REFERENCES workspaces (id) ON DELETE SET DEFAULT
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

                # Создаем рабочее пространство по умолчанию "all"
                cursor.execute(
                    "INSERT OR IGNORE INTO workspaces (name, description, is_default) VALUES (?, ?, ?)",
                    ("all", "Все заметки и задачи", True)
                )

                # Миграция: добавляем workspace_id если его нет
                try:
                    cursor.execute("ALTER TABLE notes ADD COLUMN workspace_id INTEGER DEFAULT 1")
                    print("✅ Добавлена колонка workspace_id в таблицу notes")
                except sqlite3.OperationalError:
                    pass

                try:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN workspace_id INTEGER DEFAULT 1")
                    print("✅ Добавлена колонка workspace_id в таблицу tasks")
                except sqlite3.OperationalError:
                    pass

                try:
                    cursor.execute("ALTER TABLE bookmarks ADD COLUMN workspace_id INTEGER DEFAULT 1")
                    print("✅ Добавлена колонка workspace_id в таблицу bookmarks")
                except sqlite3.OperationalError:
                    pass

                # Существующие миграции остаются
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
    def create_note(self, title: str, content: str, workspace_id: int = 1) -> Optional[int]:
        """Создает новую заметку и возвращает её ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO notes (title, content, workspace_id) VALUES (?, ?, ?)",
                    (title, content, workspace_id)
                )
                conn.commit()
                note_id = cursor.lastrowid
                print(f"✅ Создана заметка в workspace {workspace_id}: {title} (ID: {note_id})")
                return note_id
        except sqlite3.Error as e:
            print(f"❌ Ошибка при создании заметки: {e}")
            return None

    def get_notes_by_workspace(self, workspace_id: int) -> List[Tuple]:
        """Возвращает заметки для указанного рабочего пространства."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM notes WHERE workspace_id = ? ORDER BY updated_at DESC",
                    (workspace_id,)
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении заметок workspace {workspace_id}: {e}")
            return []

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

    # --- Методы для работы с рабочими пространствами ---

    def create_workspace(self, name: str, description: str = "") -> Optional[int]:
        """Создает новое рабочее пространство и возвращает его ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO workspaces (name, description) VALUES (?, ?)",
                    (name, description)
                )
                conn.commit()
                workspace_id = cursor.lastrowid
                print(f"✅ Создано рабочее пространство: {name} (ID: {workspace_id})")
                return workspace_id
        except sqlite3.Error as e:
            print(f"❌ Ошибка при создании рабочего пространства: {e}")
            return None

    def get_all_workspaces(self) -> List[Tuple]:
        """Возвращает список всех рабочих пространств."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM workspaces ORDER BY name")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении рабочих пространств: {e}")
            return []

    def get_workspace_by_id(self, workspace_id: int) -> Optional[Tuple]:
        """Возвращает рабочее пространство по ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM workspaces WHERE id = ?", (workspace_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении рабочего пространства: {e}")
            return None

    def get_default_workspace(self) -> Optional[Tuple]:
        """Возвращает рабочее пространство по умолчанию."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM workspaces WHERE is_default = TRUE")
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении рабочего пространства по умолчанию: {e}")
            return None

    def update_workspace(self, workspace_id: int, name: str, description: str = "") -> bool:
        """Обновляет рабочее пространство."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE workspaces SET name = ?, description = ? WHERE id = ?",
                    (name, description, workspace_id)
                )
                conn.commit()
                success = cursor.rowcount > 0
                if success:
                    print(f"✅ Рабочее пространство {workspace_id} обновлено")
                return success
        except sqlite3.Error as e:
            print(f"❌ Ошибка при обновлении рабочего пространства: {e}")
            return False

    def delete_workspace(self, workspace_id: int) -> bool:
        """Удаляет рабочее пространство."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Нельзя удалить рабочее пространство по умолчанию
                cursor.execute("SELECT is_default FROM workspaces WHERE id = ?", (workspace_id,))
                workspace = cursor.fetchone()
                if workspace and workspace[3]:  # is_default поле
                    print("❌ Нельзя удалить рабочее пространство по умолчанию")
                    return False

                cursor.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
                conn.commit()
                success = cursor.rowcount > 0
                if success:
                    print(f"✅ Рабочее пространство {workspace_id} удалено")
                return success
        except sqlite3.Error as e:
            print(f"❌ Ошибка при удалении рабочего пространства: {e}")
            return False

