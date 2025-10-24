from typing import List, Optional
from .models import Tag
from .database_manager import DatabaseManager


class TagManager:
    """Менеджер для работы с тегами в базе данных"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация менеджера тегов

        Args:
            db_manager: Экземпляр DatabaseManager для работы с БД
        """
        self.db = db_manager

    def create(self, name: str, workspace_id: int = 1) -> Optional[Tag]:
        """
        Создает новый тег в БД для указанного workspace
        """
        if not name or not name.strip():
            print("❌ Ошибка: имя тега не может быть пустым")
            return None

        normalized_name = name.strip().lower()

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем, существует ли тег с таким именем В ДАННОМ WORKSPACE
                cursor.execute(
                    "SELECT id, name FROM tags WHERE name = ? AND workspace_id = ?",
                    (normalized_name, workspace_id)
                )
                existing_tag = cursor.fetchone()

                if existing_tag:
                    tag_id, tag_name = existing_tag
                    print(f"✅ Тег '{tag_name}' уже существует в workspace {workspace_id} (ID: {tag_id})")
                    return Tag(name=tag_name, tag_id=tag_id)

                # Создаем новый тег ПРИВЯЗАННЫЙ К WORKSPACE
                cursor.execute(
                    "INSERT INTO tags (name, workspace_id) VALUES (?, ?)",
                    (normalized_name, workspace_id)
                )
                conn.commit()
                tag_id = cursor.lastrowid

                if tag_id:
                    print(f"✅ Тег '{normalized_name}' создан в workspace {workspace_id} с ID: {tag_id}")
                    return Tag(name=normalized_name, tag_id=tag_id)
                else:
                    print("❌ Ошибка: не удалось получить ID созданного тега")
                    return None

        except Exception as e:
            print(f"❌ Ошибка при создании тега '{name}' в workspace {workspace_id}: {e}")
            return None

    def get(self, tag_id: int) -> Optional[Tag]:
        """
        Возвращает объект Tag по ID

        Args:
            tag_id: ID тега

        Returns:
            Tag: Найденный тег или None если не найден
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM tags WHERE id = ?", (tag_id,))
                result = cursor.fetchone()

                if result:
                    tag_id, name = result
                    return Tag(name=name, tag_id=tag_id)
                else:
                    print(f"Тег с ID {tag_id} не найден")
                    return None

        except Exception as e:
            print(f"Ошибка при получении тега с ID {tag_id}: {e}")
            return None

    def get_all(self, workspace_id: Optional[int] = None) -> List[Tag]:
        """
        Возвращает список всех тегов для определенного workspace
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                if workspace_id is not None:
                    # Получаем ВСЕ теги для данного workspace (включая неиспользуемые)
                    cursor.execute("""
                        SELECT id, name 
                        FROM tags 
                        WHERE workspace_id = ?
                        ORDER BY name
                    """, (workspace_id,))
                    print(f"🔍 Загружаем ВСЕ теги для workspace {workspace_id}")
                else:
                    # Получаем все теги (для обратной совместимости)
                    cursor.execute("SELECT id, name FROM tags ORDER BY name")
                    print("🔍 Загружаем все теги")

                results = cursor.fetchall()

                tags = []
                for tag_id, name in results:
                    tags.append(Tag(name=name, tag_id=tag_id))

                print(f"✅ Загружено тегов: {len(tags)}")
                return tags

        except Exception as e:
            print(f"❌ Ошибка при получении списка тегов: {e}")
            return []

    def get_by_name(self, name: str, workspace_id: Optional[int] = None) -> Optional[Tag]:
        """
        Поиск тега по имени в рамках workspace
        """
        if not name:
            return None

        normalized_name = name.strip().lower()

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                if workspace_id is not None:
                    cursor.execute(
                        "SELECT id, name FROM tags WHERE name = ? AND workspace_id = ?",
                        (normalized_name, workspace_id)
                    )
                else:
                    cursor.execute("SELECT id, name FROM tags WHERE name = ?", (normalized_name,))

                result = cursor.fetchone()

                if result:
                    tag_id, name = result
                    return Tag(name=name, tag_id=tag_id)
                else:
                    return None

        except Exception as e:
            print(f"Ошибка при поиске тега по имени '{name}': {e}")
            return None

    def delete(self, tag_id: int) -> bool:
        """
        Удаляет тег по ID

        Args:
            tag_id: ID тега для удаления

        Returns:
            bool: True если удаление успешно, False если ошибка
        """
        # Сначала проверяем, существует ли тег
        tag = self.get(tag_id)
        if not tag:
            print(f"Тег с ID {tag_id} не существует")
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"Тег '{tag.name}' (ID: {tag_id}) успешно удален")
                    return True
                else:
                    print(f"Не удалось удалить тег с ID {tag_id}")
                    return False

        except Exception as e:
            print(f"Ошибка при удалении тега с ID {tag_id}: {e}")
            return False

    def get_or_create(self, name: str, workspace_id: int = 1) -> Tag:
        """
        Получает существующий тег или создает новый для указанного workspace
        """
        existing_tag = self.get_by_name(name, workspace_id)
        if existing_tag:
            return existing_tag
        else:
            new_tag = self.create(name, workspace_id)
            return new_tag if new_tag else Tag(name=name)

    def get_tags_for_note(self, note_id: int) -> List[Tag]:
        """
        Возвращает список тегов для указанной заметки

        Args:
            note_id: ID заметки

        Returns:
            List[Tag]: Список тегов заметки
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.id, t.name 
                    FROM tags t 
                    JOIN note_tag_relation ntr ON t.id = ntr.tag_id 
                    WHERE ntr.note_id = ?
                """, (note_id,))
                results = cursor.fetchall()

                tags = []
                for tag_id, name in results:
                    tags.append(Tag(name=name, tag_id=tag_id))

                return tags

        except Exception as e:
            print(f"Ошибка при получении тегов для заметки {note_id}: {e}")
            return []

    def update(self, tag_id: int, new_name: str) -> bool:
        """
        Обновляет название тега

        Args:
            tag_id: ID тега
            new_name: Новое название

        Returns:
            bool: True если обновление успешно
        """
        if not new_name or not new_name.strip():
            print("Ошибка: новое имя тега не может быть пустым")
            return False

        normalized_name = new_name.strip().lower()

        # Проверяем, не существует ли уже тег с таким именем
        existing_tag = self.get_by_name(normalized_name)
        if existing_tag and existing_tag.id != tag_id:
            print(f"Тег с именем '{normalized_name}' уже существует")
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE tags SET name = ? WHERE id = ?",
                    (normalized_name, tag_id)
                )
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"Тег с ID {tag_id} обновлен на '{normalized_name}'")
                    return True
                else:
                    print(f"Тег с ID {tag_id} не найден для обновления")
                    return False

        except Exception as e:
            print(f"Ошибка при обновлении тега с ID {tag_id}: {e}")
            return False

    def get_notes_by_tag(self, tag_name: str, workspace_id: Optional[int] = None) -> List:
        """
        Возвращает заметки с указанным тегом, опционально фильтруя по workspace

        Args:
            tag_name: Название тега
            workspace_id: ID рабочего пространства (опционально)

        Returns:
            List: Список ID заметок
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                if workspace_id is not None:
                    cursor.execute("""
                        SELECT DISTINCT n.id 
                        FROM notes n
                        JOIN note_tag_relation ntr ON n.id = ntr.note_id
                        JOIN tags t ON ntr.tag_id = t.id
                        WHERE t.name = ? AND n.workspace_id = ?
                    """, (tag_name.lower(), workspace_id))  # ← ДОБАВЛЕН lower()
                    print(f"🔍 Поиск заметок по тегу '{tag_name}' в workspace {workspace_id}")
                else:
                    cursor.execute("""
                        SELECT n.id 
                        FROM notes n
                        JOIN note_tag_relation ntr ON n.id = ntr.note_id
                        JOIN tags t ON ntr.tag_id = t.id
                        WHERE t.name = ?
                    """, (tag_name.lower(),))  # ← ДОБАВЛЕН lower()
                    print(f"🔍 Поиск заметок по тегу '{tag_name}' во всех workspace")

                results = cursor.fetchall()
                note_ids = [row[0] for row in results]
                print(f"✅ Найдено {len(note_ids)} заметок с тегом '{tag_name}' в workspace {workspace_id}")
                return note_ids

        except Exception as e:
            print(f"❌ Ошибка получения заметок по тегу {tag_name}: {e}")
            return []

    def get_popular_tags(self, workspace_id: Optional[int] = None, limit: int = 10) -> List[Tag]:
        """
        Возвращает самые популярные теги (по количеству использования)

        Args:
            workspace_id: ID рабочего пространства (опционально)
            limit: Максимальное количество тегов

        Returns:
            List[Tag]: Список популярных тегов
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                if workspace_id is not None:
                    cursor.execute("""
                        SELECT t.id, t.name, COUNT(ntr.note_id) as usage_count
                        FROM tags t
                        JOIN note_tag_relation ntr ON t.id = ntr.tag_id
                        JOIN notes n ON ntr.note_id = n.id
                        WHERE n.workspace_id = ?
                        GROUP BY t.id, t.name
                        ORDER BY usage_count DESC, t.name
                        LIMIT ?
                    """, (workspace_id, limit))
                    print(f"🔍 Получаем популярные теги для workspace {workspace_id}")
                else:
                    cursor.execute("""
                        SELECT t.id, t.name, COUNT(ntr.note_id) as usage_count
                        FROM tags t
                        JOIN note_tag_relation ntr ON t.id = ntr.tag_id
                        GROUP BY t.id, t.name
                        ORDER BY usage_count DESC, t.name
                        LIMIT ?
                    """, (limit,))
                    print("🔍 Получаем популярные теги для всех workspace")

                results = cursor.fetchall()

                tags = []
                for tag_id, name, usage_count in results:
                    tag = Tag(name=name, tag_id=tag_id)
                    tag.usage_count = usage_count  # Добавляем счетчик использования
                    tags.append(tag)

                print(f"✅ Загружено {len(tags)} популярных тегов")
                return tags

        except Exception as e:
            print(f"❌ Ошибка при получении популярных тегов: {e}")
            return []

    def get_tags_by_workspace(self, workspace_id: int) -> List[Tag]:
        """
        Возвращает все теги для указанного workspace

        Args:
            workspace_id: ID рабочего пространства

        Returns:
            List[Tag]: Список тегов workspace
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name 
                    FROM tags 
                    WHERE workspace_id = ?
                    ORDER BY name
                """, (workspace_id,))

                results = cursor.fetchall()
                tags = []
                for tag_id, name in results:
                    tags.append(Tag(name=name, tag_id=tag_id))

                print(f"✅ Загружено {len(tags)} тегов для workspace {workspace_id}")
                return tags

        except Exception as e:
            print(f"❌ Ошибка при получении тегов для workspace {workspace_id}: {e}")
            return []
