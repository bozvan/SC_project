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

    def create(self, name: str) -> Optional[Tag]:
        """
        Создает новый тег в БД (с проверкой на дубликаты)
        Использует отдельное соединение для случаев, когда вызывается отдельно
        """
        if not name or not name.strip():
            print("❌ Ошибка: имя тега не может быть пустым")
            return None

        normalized_name = name.strip().lower()

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем, существует ли тег с таким именем
                cursor.execute("SELECT id, name FROM tags WHERE name = ?", (normalized_name,))
                existing_tag = cursor.fetchone()

                if existing_tag:
                    tag_id, tag_name = existing_tag
                    print(f"✅ Тег '{tag_name}' уже существует (ID: {tag_id})")
                    return Tag(name=tag_name, tag_id=tag_id)

                # Создаем новый тег
                cursor.execute("INSERT INTO tags (name) VALUES (?)", (normalized_name,))
                conn.commit()
                tag_id = cursor.lastrowid

                if tag_id:
                    print(f"✅ Тег '{normalized_name}' создан с ID: {tag_id}")
                    return Tag(name=normalized_name, tag_id=tag_id)
                else:
                    print("❌ Ошибка: не удалось получить ID созданного тега")
                    return None

        except Exception as e:
            print(f"❌ Ошибка при создании тега '{name}': {e}")
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

    def get_all(self) -> List[Tag]:
        """
        Возвращает список всех тегов

        Returns:
            List[Tag]: Список всех тегов в базе данных
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM tags ORDER BY name")
                results = cursor.fetchall()

                tags = []
                for tag_id, name in results:
                    tags.append(Tag(name=name, tag_id=tag_id))

                print(f"Загружено тегов: {len(tags)}")
                return tags

        except Exception as e:
            print(f"Ошибка при получении списка тегов: {e}")
            return []

    def get_by_name(self, name: str) -> Optional[Tag]:
        """
        Поиск тега по имени (регистронезависимый)

        Args:
            name: Название тега для поиска

        Returns:
            Tag: Найденный тег или None если не найден
        """
        if not name:
            return None

        normalized_name = name.strip().lower()

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
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

    def get_or_create(self, name: str) -> Tag:
        """
        Получает существующий тег или создает новый

        Args:
            name: Название тега

        Returns:
            Tag: Существующий или созданный тег
        """
        existing_tag = self.get_by_name(name)
        if existing_tag:
            return existing_tag
        else:
            new_tag = self.create(name)
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

    def get_notes_by_tag(self, tag_name: str) -> List:
        """Возвращает заметки с указанным тегом"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT n.id 
                    FROM notes n
                    JOIN note_tag_relation ntr ON n.id = ntr.note_id
                    JOIN tags t ON ntr.tag_id = t.id
                    WHERE t.name = ?
                """, (tag_name,))
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(f"❌ Ошибка получения заметок по тегу {tag_name}: {e}")
            return []