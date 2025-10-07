from datetime import datetime
from typing import List, Optional


class Note:
    """Класс, представляющий заметку"""

    def __init__(self,
                 title: str,
                 content: str = "",
                 note_id: Optional[int] = None,
                 created_date: Optional[datetime] = None,
                 modified_date: Optional[datetime] = None,
                 content_type: str = "plain",
                 note_type: str = "note",  # "note" или "bookmark"
                 url: Optional[str] = None,
                 page_title: Optional[str] = None,
                 page_description: Optional[str] = None):
        """
        Инициализация заметки или закладки

        Args:
            title: Заголовок заметки/закладки
            content: Содержимое заметки
            note_id: Уникальный идентификатор
            created_date: Дата создания
            modified_date: Дата последнего изменения
            content_type: Тип содержимого - "plain" или "html"
            note_type: Тип записи - "note" (заметка) или "bookmark" (закладка)
            url: URL веб-страницы (только для закладок)
            page_title: Заголовок веб-страницы (только для закладок)
            page_description: Описание веб-страницы (только для закладок)
        """
        self.id = note_id
        self.title = title
        self.content = content
        self.created_date = created_date if created_date else datetime.now()
        self.modified_date = modified_date if modified_date else datetime.now()
        self.content_type = content_type
        self.note_type = note_type  # "note" или "bookmark"
        self.url = url
        self.page_title = page_title
        self.page_description = page_description
        self.tags: List[Tag] = []  # Список связанных тегов

    def __str__(self) -> str:
        """Строковое представление заметки/закладки"""
        type_str = "🔖" if self.note_type == "bookmark" else "📝"
        content_type_str = f" ({self.content_type})" if self.content_type != "plain" else ""
        url_str = f" [URL: {self.url}]" if self.url else ""
        return f"{type_str} Note(id={self.id}, title='{self.title}'{content_type_str}{url_str}, type={self.note_type})"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Note(id={self.id}, title='{self.title}', type='{self.note_type}', url='{self.url}')"

    def add_tag(self, tag: 'Tag') -> None:
        """Добавляет тег к заметке"""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: 'Tag') -> None:
        """Удаляет тег из заметки"""
        if tag in self.tags:
            self.tags.remove(tag)

    def update_modified_date(self) -> None:
        """Обновляет дату изменения"""
        self.modified_date = datetime.now()

    def is_html(self) -> bool:
        """Проверяет, является ли содержимое HTML"""
        return self.content_type == "html"

    def is_bookmark(self) -> bool:
        """Проверяет, является ли запись закладкой"""
        return self.note_type == "bookmark"

    def is_note(self) -> bool:
        """Проверяет, является ли запись заметкой"""
        return self.note_type == "note"


class Tag:
    """Класс, представляющий тег"""

    def __init__(self, name: str, tag_id: Optional[int] = None):
        """
        Инициализация тега

        Args:
            name: Название тега
            tag_id: Уникальный идентификатор
        """
        self.id = tag_id
        self.name = name.strip().lower()  # Нормализуем имя тега

    def __str__(self) -> str:
        """Строковое представление тега"""
        return f"Tag(id={self.id}, name='{self.name}')"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Tag(id={self.id}, name='{self.name}')"

    def __eq__(self, other) -> bool:
        """Сравнение тегов по имени"""
        if isinstance(other, Tag):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other.lower().strip()
        return False

    def __hash__(self) -> int:
        """Хэш для использования в множествах и словарях"""
        return hash(self.name)


class Task:
    """Класс, представляющий задачу внутри заметки"""

    def __init__(self,
                 description: str,
                 is_completed: bool = False,
                 task_id: Optional[int] = None,
                 due_date: Optional[datetime] = None,
                 note_id: Optional[int] = None,
                 created_date: Optional[datetime] = None,
                 updated_date: Optional[datetime] = None):
        """
        Инициализация задачи

        Args:
            description: Описание задачи
            is_completed: Статус выполнения
            task_id: Уникальный идентификатор
            due_date: Срок выполнения
            note_id: ID родительской заметки
            created_date: Дата создания
            updated_date: Дата обновления
        """
        self.id = task_id
        self.description = description
        self.is_completed = is_completed
        self.due_date = due_date
        self.note_id = note_id
        self.created_date = created_date if created_date else datetime.now()
        self.updated_date = updated_date if updated_date else datetime.now()
        self.note_title = None  # Для отображения контекста в виджетах

    def __str__(self) -> str:
        """Строковое представление задачи"""
        status = "✅" if self.is_completed else "⭕"
        due_info = f" (до {self.due_date.strftime('%d.%m.%Y')})" if self.due_date else ""
        return f"Task({status} '{self.description}'{due_info})"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Task(id={self.id}, note_id={self.note_id}, desc='{self.description[:20]}...', completed={self.is_completed})"

    def toggle_completion(self) -> None:
        """Переключает статус выполнения задачи"""
        self.is_completed = not self.is_completed
        self.updated_date = datetime.now()


class WebBookmark:
    """Класс, представляющий веб-закладку"""

    def __init__(self,
                 url: str,
                 title: str = "",
                 description: str = "",
                 bookmark_id: Optional[int] = None,
                 favicon_url: Optional[str] = None,
                 created_date: Optional[datetime] = None,
                 updated_date: Optional[datetime] = None):
        """
        Инициализация закладки

        Args:
            url: URL веб-страницы
            title: Заголовок страницы
            description: Описание страницы
            bookmark_id: Уникальный идентификатор
            favicon_url: URL иконки сайта
            created_date: Дата создания
            updated_date: Дата обновления
        """
        self.id = bookmark_id
        self.url = url
        self.title = title
        self.description = description
        self.favicon_url = favicon_url
        self.created_date = created_date if created_date else datetime.now()
        self.updated_date = updated_date if updated_date else datetime.now()
        self.tags: List[Tag] = []  # Список связанных тегов

    def __str__(self) -> str:
        """Строковое представление закладки"""
        return f"🔖 WebBookmark(id={self.id}, title='{self.title}', url='{self.url}')"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"WebBookmark(id={self.id}, title='{self.title}', url='{self.url}')"

    def get_domain(self) -> str:
        """Возвращает домен из URL"""
        from urllib.parse import urlparse
        try:
            return urlparse(self.url).netloc
        except:
            return self.url
