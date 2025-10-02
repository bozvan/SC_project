from typing import List, Optional
from datetime import datetime
from .models import Note, Tag
from .database_manager import DatabaseManager
from .tag_manager import TagManager


class NoteManager:
    """Менеджер для работы с заметками в базе данных"""

    def __init__(self, db_manager: DatabaseManager, tag_manager: TagManager):
        self.db = db_manager
        self.tag_manager = tag_manager

        # Выполняем миграцию при инициализации
        self.db.migrate_database()

    def create(self, title: str, content: str = "", tags: Optional[List[str]] = None, content_type: str = "html") -> \
    Optional[Note]:
        """
        Создает новую заметку с ОДНИМ соединением к БД
        """
        if not title or not title.strip():
            print("❌ Ошибка: заголовок заметки не может быть пустым")
            return None

        # Валидация content_type
        if content_type not in ["plain", "html"]:
            print(f"⚠️  Неподдерживаемый content_type: {content_type}. Используется 'html'")
            content_type = "html"

        title = title.strip()
        content = content.strip() if content else ""

        try:
            # Используем ОДНО соединение для всех операций
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Вставляем заметку в таблицу notes
                cursor.execute(
                    "INSERT INTO notes (title, content, content_type) VALUES (?, ?, ?)",
                    (title, content, content_type)
                )
                note_id = cursor.lastrowid

                if not note_id:
                    print("❌ Ошибка: не удалось получить ID созданной заметки")
                    return None

                # Обрабатываем теги в ТОМ ЖЕ соединении
                tag_objects = []
                if tags:
                    for tag_name in tags:
                        tag = self._get_or_create_tag_with_connection(cursor, tag_name)
                        if tag:
                            # Связываем заметку с тегом
                            cursor.execute(
                                "INSERT INTO note_tag_relation (note_id, tag_id) VALUES (?, ?)",
                                (note_id, tag.id)
                            )
                            tag_objects.append(tag)

                conn.commit()

                # Создаем объект Note
                note = Note(
                    title=title,
                    content=content,
                    note_id=note_id,
                    created_date=datetime.now(),
                    modified_date=datetime.now(),
                    content_type=content_type
                )
                note.tags = tag_objects

                print(f"✅ Заметка '{title}' создана с ID: {note_id} (тип: {content_type})")
                if tag_objects:
                    print(f"   Привязаны теги: {[tag.name for tag in tag_objects]}")

                return note

        except Exception as e:
            print(f"❌ Ошибка при создании заметки '{title}': {e}")
            return None

    def get(self, note_id: int) -> Optional[Note]:
        """
        Возвращает объект Note по ID со списком связанных тегов

        Args:
            note_id: ID заметки

        Returns:
            Note: Найденная заметка или None если не найдена
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Получаем данные заметки
                cursor.execute(
                    "SELECT id, title, content, content_type, created_at, updated_at FROM notes WHERE id = ?",
                    (note_id,)
                )
                result = cursor.fetchone()

                if not result:
                    print(f"❌ Заметка с ID {note_id} не найдена")
                    return None

                note_id, title, content, content_type, created_at, updated_at = result

                # Получаем теги для этой заметки
                tag_objects = self.tag_manager.get_tags_for_note(note_id)

                # Преобразуем строки дат в объекты datetime
                created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                modified_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                # Если content_type не установлен, используем по умолчанию "plain"
                if content_type is None:
                    content_type = "plain"

                # Создаем объект Note
                note = Note(
                    title=title,
                    content=content or "",
                    note_id=note_id,
                    created_date=created_date,
                    modified_date=modified_date,
                    content_type=content_type
                )
                note.tags = tag_objects

                return note

        except Exception as e:
            print(f"❌ Ошибка при получении заметки с ID {note_id}: {e}")
            return None

    def update(self, note_id: int, title: Optional[str] = None,
               content: Optional[str] = None, tags: Optional[List[str]] = None,
               content_type: Optional[str] = None) -> bool:
        """
        Обновляет данные заметки с ОДНИМ соединением к БД
        """
        # Проверяем, существует ли заметка
        existing_note = self.get(note_id)
        if not existing_note:
            print(f"❌ Заметка с ID {note_id} не существует")
            return False

        # Валидация content_type
        if content_type is not None and content_type not in ["plain", "html"]:
            print(f"⚠️  Неподдерживаемый content_type: {content_type}. Изменение не применено.")
            content_type = None

        try:
            # Используем ОДНО соединение для всех операций
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Подготавливаем данные для обновления
                update_fields = []
                update_values = []

                if title is not None and title.strip():
                    update_fields.append("title = ?")
                    update_values.append(title.strip())

                if content is not None:
                    update_fields.append("content = ?")
                    update_values.append(content.strip() if content else "")

                if content_type is not None:
                    update_fields.append("content_type = ?")
                    update_values.append(content_type)

                # Всегда обновляем updated_at
                update_fields.append("updated_at = CURRENT_TIMESTAMP")

                if update_fields:
                    update_values.append(note_id)
                    update_query = f"UPDATE notes SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(update_query, update_values)

                # Обновляем теги в ТОМ ЖЕ соединении
                if tags is not None:
                    # Удаляем старые связи
                    cursor.execute("DELETE FROM note_tag_relation WHERE note_id = ?", (note_id,))

                    # Добавляем новые связи
                    for tag_name in tags:
                        # Используем существующий TagManager но с текущим соединением
                        tag = self._get_or_create_tag_with_connection(cursor, tag_name)
                        if tag and tag.id:
                            cursor.execute(
                                "INSERT INTO note_tag_relation (note_id, tag_id) VALUES (?, ?)",
                                (note_id, tag.id)
                            )

                conn.commit()

                print(f"✅ Заметка с ID {note_id} успешно обновлена")
                if content_type is not None:
                    print(f"   Тип содержимого изменен на: {content_type}")
                if tags is not None:
                    print(f"   Обновлены теги: {tags}")

                return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении заметки с ID {note_id}: {e}")
            return False

    def _get_or_create_tag_with_connection(self, cursor, tag_name: str) -> Optional[Tag]:
        """
        Вспомогательный метод для получения или создания тега с использованием существующего курсора
        """
        if not tag_name or not tag_name.strip():
            return None

        normalized_name = tag_name.strip().lower()

        try:
            # Сначала ищем существующий тег
            cursor.execute("SELECT id, name FROM tags WHERE name = ?", (normalized_name,))
            result = cursor.fetchone()

            if result:
                tag_id, name = result
                return Tag(name=name, tag_id=tag_id)
            else:
                # Создаем новый тег
                cursor.execute("INSERT INTO tags (name) VALUES (?)", (normalized_name,))
                tag_id = cursor.lastrowid
                if tag_id:
                    print(f"✅ Тег '{normalized_name}' создан с ID: {tag_id}")
                    return Tag(name=normalized_name, tag_id=tag_id)
                else:
                    print(f"❌ Ошибка при создании тега '{normalized_name}'")
                    return None

        except Exception as e:
            print(f"❌ Ошибка при работе с тегом '{tag_name}': {e}")
            return None

    def delete(self, note_id: int) -> bool:
        """
        Удаляет заметку и все ее связи с тегами

        Args:
            note_id: ID заметки для удаления

        Returns:
            bool: True если удаление успешно
        """
        # Проверяем, существует ли заметка
        existing_note = self.get(note_id)
        if not existing_note:
            print(f"Заметка с ID {note_id} не существует")
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Удаляем связи с тегами (благодаря ON DELETE CASCADE это может быть не нужно,
                # но делаем для надежности)
                cursor.execute("DELETE FROM note_tag_relation WHERE note_id = ?", (note_id,))

                # Удаляем саму заметку
                cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"Заметка '{existing_note.title}' (ID: {note_id}) успешно удалена")
                    return True
                else:
                    print(f"Не удалось удалить заметку с ID {note_id}")
                    return False

        except Exception as e:
            print(f"Ошибка при удалении заметки с ID {note_id}: {e}")
            return False

    def search(self, search_text: str = "", tag_names: Optional[List[str]] = None) -> List[Note]:
        """
        Ищет заметки по тексту и/или тегам

        Args:
            search_text: Текст для поиска в заголовке и содержимом (без учета регистра)
            tag_names: Список тегов для фильтрации (ВСЕ теги должны присутствовать)

        Returns:
            List[Note]: Список найденных заметок
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Базовый запрос
                query = """
                SELECT n.id, n.title, n.content, n.created_at, n.updated_at
                FROM notes n
                WHERE 1=1
                """
                params = []

                # Добавляем условие для текстового поиска (без учета регистра)
                if search_text.strip():
                    search_pattern = f"%{search_text.strip()}%"
                    query += " AND (LOWER(n.title) LIKE LOWER(?) OR LOWER(n.content) LIKE LOWER(?))"
                    params.extend([search_pattern, search_pattern])

                # Добавляем условие для тегов (ВСЕ указанные теги должны присутствовать)
                if tag_names:
                    normalized_tag_names = [name.strip().lower() for name in tag_names]

                    # Для каждого тега добавляем JOIN и условие
                    for i, tag_name in enumerate(normalized_tag_names):
                        query += f"""
                        AND EXISTS (
                            SELECT 1 FROM note_tag_relation ntr{i}
                            JOIN tags t{i} ON ntr{i}.tag_id = t{i}.id
                            WHERE ntr{i}.note_id = n.id AND t{i}.name = ?
                        )
                        """
                        params.append(tag_name)

                # Сортируем по дате обновления (новые сначала)
                query += " ORDER BY n.updated_at DESC"

                cursor.execute(query, params)
                results = cursor.fetchall()

                notes = []
                for note_id, title, content, created_at, updated_at in results:
                    # Получаем теги для каждой заметки
                    tag_objects = self.tag_manager.get_tags_for_note(note_id)

                    # Преобразуем даты
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    modified_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    # Создаем объект Note
                    note = Note(
                        title=title,  # Сохраняем оригинальный регистр
                        content=content or "",
                        note_id=note_id,
                        created_date=created_date,
                        modified_date=modified_date
                    )
                    note.tags = tag_objects
                    notes.append(note)

                print(f"Найдено заметок: {len(notes)}")
                if search_text:
                    print(f"Поисковый запрос (без учета регистра): '{search_text}'")
                if tag_names:
                    print(f"Теги для фильтрации (ВСЕ должны быть): {tag_names}")

                return notes

        except Exception as e:
            print(f"Ошибка при поиске заметок: {e}")
            return []

    def get_all(self) -> List[Note]:
        """
        Возвращает все заметки

        Returns:
            List[Note]: Список всех заметок
        """
        return self.search("", None)

    def get_notes_by_tag(self, tag_name: str) -> List[Note]:
        """
        Возвращает заметки по конкретному тегу

        Args:
            tag_name: Имя тега

        Returns:
            List[Note]: Список заметок с указанным тегом
        """
        return self.search("", [tag_name])

    def add_tag_to_note(self, note_id: int, tag_name: str) -> bool:
        """
        Добавляет тег к существующей заметке

        Args:
            note_id: ID заметки
            tag_name: Имя тега для добавления

        Returns:
            bool: True если успешно
        """
        note = self.get(note_id)
        if not note:
            return False

        tag = self.tag_manager.get_or_create(tag_name)
        if not tag or not tag.id:
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем, нет ли уже такой связи
                cursor.execute(
                    "SELECT 1 FROM note_tag_relation WHERE note_id = ? AND tag_id = ?",
                    (note_id, tag.id)
                )
                existing = cursor.fetchone()

                if not existing:
                    cursor.execute(
                        "INSERT INTO note_tag_relation (note_id, tag_id) VALUES (?, ?)",
                        (note_id, tag.id)
                    )
                    conn.commit()
                    print(f"Тег '{tag_name}' добавлен к заметке {note_id}")
                    return True
                else:
                    print(f"Тег '{tag_name}' уже привязан к заметке {note_id}")
                    return True

        except Exception as e:
            print(f"Ошибка при добавлении тега к заметке: {e}")
            return False

    def search_by_tags(self, tag_names: List[str]) -> List[Note]:
        """
        Ищет заметки только по тегам

        Args:
            tag_names: Список тегов для фильтрации

        Returns:
            List[Note]: Список найденных заметок
        """
        return self.search("", tag_names)

    def search_by_text_and_tags(self, search_text: str, tag_names: List[str]) -> List[Note]:
        """
        Ищет заметки по тексту и тегам одновременно

        Args:
            search_text: Текст для поиска
            tag_names: Список тегов для фильтрации

        Returns:
            List[Note]: Список найденных заметок
        """
        return self.search(search_text, tag_names)