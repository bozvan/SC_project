import re
from urllib.parse import urlparse
from typing import List, Optional
from datetime import datetime

from .bookmark_manager import BookmarkManager
from .models import Note, Tag
from .database_manager import DatabaseManager
from .tag_manager import TagManager
from .task_manager import TaskManager


class NoteManager:
    """Менеджер для работы с заметками в базе данных"""

    def __init__(self, db_manager: DatabaseManager, tag_manager: TagManager):
        self.db = db_manager
        self.tag_manager = tag_manager
        self.task_manager = TaskManager(db_manager)
        self.bookmark_manager = BookmarkManager(db_manager)

        # Выполняем миграцию при инициализации
        self.db.migrate_database()

    def create(self, title: str, content: str = "", tags: Optional[List[str]] = None,
               content_type: str = "html", note_type: str = "note",
               url: Optional[str] = None, page_title: Optional[str] = None,
               page_description: Optional[str] = None, workspace_id: int = 1) -> Optional[Note]:
        """
        Создает новую заметку или веб-закладку
        """
        if not title or not title.strip():
            print("❌ Ошибка: заголовок не может быть пустым")
            return None

        # ДОБАВЬТЕ ЭТУ ОТЛАДКУ
        print(f"🔧 CREATE CALLED: workspace_id = {workspace_id}, title = '{title}'")

        # Валидация типов
        if note_type not in ["note", "bookmark"]:
            print(f"⚠️  Неподдерживаемый note_type: {note_type}. Используется 'note'")
            note_type = "note"

        if content_type not in ["plain", "html"]:
            print(f"⚠️  Неподдерживаемый content_type: {content_type}. Используется 'html'")
            content_type = "html"

        # Для закладок проверяем URL
        if note_type == "bookmark" and (not url or not url.strip()):
            print("❌ Ошибка: для закладки URL не может быть пустым")
            return None

        title = title.strip()
        content = content.strip() if content else ""
        url = url.strip() if url else None
        page_title = page_title.strip() if page_title else None
        page_description = page_description.strip() if page_description else None

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # ДОБАВЬТЕ ОТЛАДКУ ПЕРЕД ВСТАВКОЙ
                print(f"🔧 INSERTING INTO DB: workspace_id = {workspace_id}")

                # Вставляем запись в таблицу notes
                cursor.execute(
                    """INSERT INTO notes (title, content, content_type, note_type, 
                              url, page_title, page_description, workspace_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (title, content, content_type, note_type, url, page_title, page_description, workspace_id)
                )
                note_id = cursor.lastrowid

                if not note_id:
                    print("❌ Ошибка: не удалось получить ID созданной записи")
                    return None

                # Обрабатываем теги в ТОМ ЖЕ соединении
                tag_objects = []
                if tags:
                    for tag_name in tags:
                        tag = self._get_or_create_tag_with_connection(cursor, tag_name)
                        if tag:
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
                    content_type=content_type,
                    note_type=note_type,
                    url=url,
                    page_title=page_title,
                    page_description=page_description,
                    workspace_id=workspace_id
                )
                note.tags = tag_objects

                record_type = "закладка" if note_type == "bookmark" else "заметка"
                print(f"✅ {record_type} '{title}' создана с ID: {note_id} в workspace {workspace_id}")
                if note_type == "bookmark":
                    print(f"   🔗 URL: {url}")
                if tag_objects:
                    print(f"   🏷️ Привязаны теги: {[tag.name for tag in tag_objects]}")

                return note

        except Exception as e:
            print(f"❌ Ошибка при создании записи '{title}': {e}")
            return None

    def get(self, note_id: int) -> Optional[Note]:
        """
        Возвращает объект Note по ID со списком связанных тегов
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Получаем данные записи
                cursor.execute(
                    """SELECT id, title, content, content_type, note_type, 
                              url, page_title, page_description, created_at, updated_at, workspace_id 
                    FROM notes WHERE id = ?""",
                    (note_id,)
                )
                result = cursor.fetchone()

                if not result:
                    print(f"❌ Запись с ID {note_id} не найдена")
                    return None

                (note_id, title, content, content_type, note_type, url,
                 page_title, page_description, created_at, updated_at, workspace_id) = result

                # Получаем теги для этой записи
                tag_objects = self.tag_manager.get_tags_for_note(note_id)

                # Преобразуем строки дат в объекты datetime
                created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                modified_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                # Если note_type не установлен, используем по умолчанию "note"
                if note_type is None:
                    note_type = "note"

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
                    content_type=content_type,
                    note_type=note_type,
                    url=url,
                    page_title=page_title,
                    page_description=page_description,
                    workspace_id=workspace_id
                )
                note.tags = tag_objects

                return note

        except Exception as e:
            print(f"❌ Ошибка при получении записи с ID {note_id}: {e}")
            return None

    def update(self, note_id: int, title: Optional[str] = None,
               content: Optional[str] = None, tags: Optional[List[str]] = None,
               content_type: Optional[str] = None, note_type: Optional[str] = None,
               url: Optional[str] = None, page_title: Optional[str] = None,
               page_description: Optional[str] = None, workspace_id: Optional[int] = None) -> bool:
        """
        Обновляет данные заметки или закладки с валидацией
        """
        existing_note = self.get(note_id)
        if not existing_note:
            print(f"❌ Запись с ID {note_id} не существует")
            return False

        # Если обновляем URL закладки - валидируем его
        if url is not None and existing_note.is_bookmark():
            normalized_url = self._normalize_url(url)
            if not self._validate_url(normalized_url):
                print(f"❌ Ошибка: некорректный URL '{url}'")
                return False
            url = normalized_url

        # Валидация типов
        if note_type is not None and note_type not in ["note", "bookmark"]:
            print(f"⚠️  Неподдерживаемый note_type: {note_type}. Изменение не применено.")
            note_type = None

        if content_type is not None and content_type not in ["plain", "html"]:
            print(f"⚠️  Неподдерживаемый content_type: {content_type}. Изменение не применено.")
            content_type = None

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

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

                if note_type is not None:
                    update_fields.append("note_type = ?")
                    update_values.append(note_type)

                if url is not None:
                    update_fields.append("url = ?")
                    update_values.append(url.strip() if url else None)

                if page_title is not None:
                    update_fields.append("page_title = ?")
                    update_values.append(page_title.strip() if page_title else None)

                if page_description is not None:
                    update_fields.append("page_description = ?")
                    update_values.append(page_description.strip() if page_description else None)

                if workspace_id is not None:
                    update_fields.append("workspace_id = ?")
                    update_values.append(workspace_id)

                # Если нет изменений, выходим раньше
                if not update_fields:
                    print("⚠️  Нет изменений для сохранения")
                    return True

                # Всегда обновляем updated_at
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(note_id)

                update_query = f"UPDATE notes SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(update_query, update_values)

                # Обновляем теги только если они переданы
                if tags is not None:
                    cursor.execute("DELETE FROM note_tag_relation WHERE note_id = ?", (note_id,))
                    for tag_name in tags:
                        tag = self._get_or_create_tag_with_connection(cursor, tag_name)
                        if tag and tag.id:
                            cursor.execute(
                                "INSERT INTO note_tag_relation (note_id, tag_id) VALUES (?, ?)",
                                (note_id, tag.id)
                            )

                conn.commit()

                record_type = "закладка" if (note_type or existing_note.note_type) == "bookmark" else "заметка"
                print(f"✅ {record_type} с ID {note_id} обновлена")
                if url is not None:
                    print(f"   🔗 URL обновлен: {url}")
                if workspace_id is not None:
                    print(f"   📁 Workspace обновлен: {workspace_id}")

                return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении записи с ID {note_id}: {e}")
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
        """
        existing_note = self.get(note_id)
        if not existing_note:
            print(f"Заметка с ID {note_id} не существует")
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Удаляем связи с тегами
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

    def get_notes_by_workspace(self, workspace_id: int) -> List[Note]:
        """
        Возвращает заметки для указанного рабочего пространства

        Args:
            workspace_id: ID рабочего пространства

        Returns:
            List[Note]: Список заметок в workspace
        """
        return self.search(workspace_id=workspace_id)

    def search(self, search_text: str = "", tag_names: Optional[List[str]] = None,
               note_type: Optional[str] = None, workspace_id: Optional[int] = None) -> List[Note]:
        """
        Ищет записи по тексту и/или тегам с фильтрацией по типу и workspace
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Базовый запрос
                query = """
                SELECT n.id, n.title, n.content, n.created_at, n.updated_at,
                       n.note_type, n.url, n.page_title, n.page_description, n.workspace_id
                FROM notes n
                WHERE 1=1
                """
                params = []

                # Фильтр по типу записи
                if note_type:
                    query += " AND n.note_type = ?"
                    params.append(note_type)

                # Фильтр по workspace
                if workspace_id is not None:
                    query += " AND n.workspace_id = ?"
                    params.append(workspace_id)

                # Добавляем условие для текстового поиска
                if search_text.strip():
                    search_pattern = f"%{search_text.strip()}%"
                    query += " AND (LOWER(n.title) LIKE LOWER(?) OR LOWER(n.content) LIKE LOWER(?) OR LOWER(n.page_title) LIKE LOWER(?) OR LOWER(n.page_description) LIKE LOWER(?))"
                    params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

                # Добавляем условие для тегов
                if tag_names:
                    normalized_tag_names = [name.strip().lower() for name in tag_names]
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
                for (note_id, title, content, created_at, updated_at,
                     note_type, url, page_title, page_description, workspace_id) in results:
                    # Получаем теги для каждой записи
                    tag_objects = self.tag_manager.get_tags_for_note(note_id)

                    # Преобразуем даты
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    modified_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    # Создаем объект Note
                    note = Note(
                        title=title,
                        content=content or "",
                        note_id=note_id,
                        created_date=created_date,
                        modified_date=modified_date,
                        note_type=note_type or "note",
                        url=url,
                        page_title=page_title,
                        page_description=page_description,
                        workspace_id=workspace_id
                    )
                    note.tags = tag_objects
                    notes.append(note)

                search_type = "закладок" if note_type == "bookmark" else "заметок" if note_type == "note" else "записей"
                workspace_info = f" в workspace {workspace_id}" if workspace_id is not None else ""
                print(f"Найдено {search_type}: {len(notes)}{workspace_info}")
                if search_text:
                    print(f"Поисковый запрос: '{search_text}'")
                if tag_names:
                    print(f"Теги для фильтрации: {tag_names}")

                return notes

        except Exception as e:
            print(f"Ошибка при поиске записей: {e}")
            return []

    def get_all(self, workspace_id: Optional[int] = None) -> List[Note]:
        """
        Возвращает все заметки
        """
        return self.search(workspace_id=workspace_id)

    def get_notes_by_tag(self, tag_name: str, workspace_id: Optional[int] = None) -> List[Note]:
        """
        Возвращает заметки по конкретному тегу
        """
        return self.search("", [tag_name], workspace_id=workspace_id)

    def add_tag_to_note(self, note_id: int, tag_name: str) -> bool:
        """
        Добавляет тег к существующей заметке
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

    def search_by_tags(self, tag_names: List[str], note_type: Optional[str] = None,
                       workspace_id: Optional[int] = None) -> List[Note]:
        """
        Ищет записи только по тегам с фильтрацией по типу
        """
        return self.search("", tag_names, note_type, workspace_id)

    def search_by_text_and_tags(self, search_text: str, tag_names: List[str],
                                note_type: Optional[str] = None, workspace_id: Optional[int] = None) -> List[Note]:
        """
        Ищет записи по тексту и тегам с фильтрацией по типу
        """
        return self.search(search_text, tag_names, note_type, workspace_id)

    def get_current_workspace_id(self) -> int:
        """Возвращает ID текущего рабочего пространства"""
        # Пробуем получить из настроек или используем по умолчанию
        try:
            from PyQt6.QtCore import QSettings
            settings = QSettings("SmartOrganizer", "SmartOrganizer")
            workspace_id = settings.value("current_workspace", 1, type=int)
            return workspace_id
        except:
            return 1

    def create_bookmark(self, url: str, title: str = "", description: str = "",
                        tags: Optional[List[str]] = None, workspace_id: int = 1) -> Optional[Note]:
        """
        Создает новую веб-закладку с валидацией URL
        """
        if not url or not url.strip():
            print("❌ Ошибка: URL не может быть пустым")
            return None

        # Нормализуем URL
        normalized_url = self._normalize_url(url)

        # Валидируем URL
        if not self._validate_url(normalized_url):
            print(f"❌ Ошибка: некорректный URL '{url}'")
            print("   URL должен быть в формате: https://example.com или example.com")
            return None

        # Если заголовок не указан, используем URL
        if not title.strip():
            title = normalized_url

        return self.create(
            title=title,
            content="",  # Закладки не имеют содержимого
            tags=tags,
            content_type="plain",
            note_type="bookmark",
            url=normalized_url,
            page_title=title,
            page_description=description,
            workspace_id=workspace_id
        )

    def get_all_bookmarks(self, workspace_id: Optional[int] = None) -> List[Note]:
        """
        Возвращает все веб-закладки
        """
        return self.search(note_type="bookmark", workspace_id=workspace_id)

    def search_bookmarks(self, search_text: str = "", tag_names: Optional[List[str]] = None,
                         workspace_id: Optional[int] = None) -> List[Note]:
        """
        Ищет закладки по тексту и/или тегам
        """
        return self.search(search_text, tag_names, "bookmark", workspace_id)

    def _validate_url(self, url: str) -> bool:
        """
        Проверяет валидность URL
        """
        if not url or not url.strip():
            return False

        url = url.strip()

        # Простая проверка формата URL
        try:
            result = urlparse(url)
            # URL должен иметь схему (http, https) и домен
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False

    def _normalize_url(self, url: str) -> str:
        """
        Нормализует URL (добавляет https:// если нужно)
        """
        if not url:
            return url

        url = url.strip()

        # Если URL начинается с www., добавляем https://
        if url.startswith('www.'):
            return f'https://{url}'

        # Если нет схемы, добавляем https://
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'

        return url
