import unittest
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.core.models import Note, Tag, Task, WebBookmark, Workspace


class TestModels(unittest.TestCase):
    """Тесты для моделей данных"""

    def test_note_creation(self):
        """Тест создания заметки"""
        # Создаем заметку с минимальными параметрами
        note = Note("Тестовая заметка", "Это содержимое заметки")

        self.assertEqual(note.title, "Тестовая заметка")
        self.assertEqual(note.content, "Это содержимое заметки")
        self.assertIsNone(note.id)  # ID должен быть None для новой заметки
        self.assertIsInstance(note.created_date, datetime)
        self.assertIsInstance(note.modified_date, datetime)
        self.assertEqual(len(note.tags), 0)  # Пустой список тегов

    def test_note_with_id(self):
        """Тест создания заметки с ID"""
        note = Note("Заметка с ID", "Содержимое", note_id=1)
        self.assertEqual(note.id, 1)

    def test_note_string_representation(self):
        """Тест строкового представления заметки"""
        note = Note("Моя заметка", "Содержимое")
        str_repr = str(note)
        self.assertIn("Моя заметка", str_repr)
        self.assertIn("Note", str_repr)

    def test_note_tags_management(self):
        """Тест управления тегами заметки"""
        note = Note("Заметка с тегами", "Содержимое")
        tag1 = Tag("работа")
        tag2 = Tag("важное")

        # Добавляем теги
        note.add_tag(tag1)
        note.add_tag(tag2)
        self.assertEqual(len(note.tags), 2)

        # Удаляем тег
        note.remove_tag(tag1)
        self.assertEqual(len(note.tags), 1)
        self.assertEqual(note.tags[0].name, "важное")

    def test_note_with_workspace(self):
        """Тест создания заметки с workspace"""
        note = Note("Заметка в workspace", "Содержимое", workspace_id=2)
        self.assertEqual(note.workspace_id, 2)

    def test_note_bookmark_type(self):
        """Тест создания заметки типа bookmark"""
        note = Note(
            "Закладка",
            "Содержимое",
            note_type="bookmark",
            url="https://example.com"
        )
        self.assertTrue(note.is_bookmark())
        self.assertEqual(note.url, "https://example.com")

    def test_tag_creation(self):
        """Тест создания тега"""
        tag = Tag("Python")
        self.assertEqual(tag.name, "python")  # Имя должно быть нормализовано
        self.assertIsNone(tag.id)

    def test_tag_with_workspace(self):
        """Тест создания тега с workspace"""
        tag = Tag("Python", workspace_id=2)
        self.assertEqual(tag.workspace_id, 2)

    def test_tag_equality(self):
        """Тест сравнения тегов"""
        tag1 = Tag("Python")
        tag2 = Tag("python")
        tag3 = Tag("JavaScript")

        # Теги с одинаковыми именами должны быть равны
        self.assertEqual(tag1, tag2)
        self.assertEqual(tag1, "python")  # Сравнение со строкой
        self.assertNotEqual(tag1, tag3)

    def test_task_creation(self):
        """Тест создания задачи - ИСПРАВЛЕННЫЙ"""
        # Создаем задачу с правильными параметрами
        task = Task(description="Изучить Python")
        self.assertEqual(task.description, "Изучить Python")
        self.assertFalse(task.is_completed)
        self.assertIsNone(task.due_date)

    def test_task_with_title(self):
        """Тест создания задачи с заголовком"""
        task = Task(title="Задача", description="Изучить Python")
        self.assertEqual(task.title, "Задача")
        self.assertEqual(task.description, "Изучить Python")

    def test_task_with_workspace(self):
        """Тест создания задачи с workspace"""
        task = Task(description="Задача", workspace_id=2)
        self.assertEqual(task.workspace_id, 2)

    def test_task_toggle(self):
        """Тест переключения статуса задачи"""
        task = Task(description="Тестовая задача")
        self.assertFalse(task.is_completed)

        task.toggle_completion()
        self.assertTrue(task.is_completed)

        task.toggle_completion()
        self.assertFalse(task.is_completed)

    def test_task_with_due_date(self):
        """Тест создания задачи с датой выполнения"""
        due_date = datetime(2025, 12, 31)
        task = Task(description="Задача с датой", due_date=due_date)
        self.assertEqual(task.due_date, due_date)

    def test_web_bookmark_creation(self):
        """Тест создания веб-закладки"""
        bookmark = WebBookmark("https://python.org", "Python Official Site")
        self.assertEqual(bookmark.url, "https://python.org")
        self.assertEqual(bookmark.title, "Python Official Site")
        self.assertEqual(bookmark.description, "")

    def test_web_bookmark_with_description(self):
        """Тест создания веб-закладки с описанием"""
        bookmark = WebBookmark(
            "https://python.org",
            "Python Official Site",
            description="Официальный сайт Python"
        )
        self.assertEqual(bookmark.description, "Официальный сайт Python")

    def test_web_bookmark_with_workspace(self):
        """Тест создания веб-закладки с workspace"""
        bookmark = WebBookmark(
            "https://example.com",
            "Example",
            workspace_id=2
        )
        self.assertEqual(bookmark.workspace_id, 2)

    def test_web_bookmark_get_domain(self):
        """Тест получения домена из URL закладки"""
        bookmark = WebBookmark("https://docs.python.org/3/", "Python Docs")
        domain = bookmark.get_domain()
        self.assertEqual(domain, "docs.python.org")

    def test_workspace_creation(self):
        """Тест создания рабочего пространства"""
        workspace = Workspace("Мой проект", "Описание проекта")
        self.assertEqual(workspace.name, "Мой проект")
        self.assertEqual(workspace.description, "Описание проекта")
        self.assertFalse(workspace.is_default)

    def test_workspace_default(self):
        """Тест создания workspace по умолчанию"""
        workspace = Workspace("Default", is_default=True)
        self.assertTrue(workspace.is_default)

    def test_workspace_add_note(self):
        """Тест добавления заметки в workspace"""
        workspace = Workspace("Проект")
        note = Note("Заметка", "Содержимое")

        workspace.add_note(note)
        self.assertEqual(len(workspace.notes), 1)
        self.assertEqual(workspace.notes[0].title, "Заметка")

    def test_workspace_add_task(self):
        """Тест добавления задачи в workspace"""
        workspace = Workspace("Проект")
        task = Task(description="Задача")

        workspace.add_task(task)
        self.assertEqual(len(workspace.tasks), 1)
        self.assertEqual(workspace.tasks[0].description, "Задача")

    def test_workspace_add_bookmark(self):
        """Тест добавления закладки в workspace"""
        workspace = Workspace("Проект")
        bookmark = WebBookmark("https://example.com", "Example")

        workspace.add_bookmark(bookmark)
        self.assertEqual(len(workspace.bookmarks), 1)
        self.assertEqual(workspace.bookmarks[0].title, "Example")

    def test_note_update_modified_date(self):
        """Тест обновления даты изменения заметки"""
        note = Note("Заметка", "Содержимое")
        original_date = note.modified_date

        # Ждем немного чтобы гарантировать разницу во времени
        import time
        time.sleep(0.1)

        note.update_modified_date()
        self.assertNotEqual(original_date, note.modified_date)

    def test_note_content_types(self):
        """Тест типов контента заметки"""
        html_note = Note("HTML", "<h1>Заголовок</h1>", content_type="html")
        plain_note = Note("Plain", "Текст", content_type="plain")

        self.assertTrue(html_note.is_html())
        self.assertFalse(plain_note.is_html())

    def test_tag_hash(self):
        """Тест хэширования тегов"""
        tag1 = Tag("python")
        tag2 = Tag("python")
        tag3 = Tag("javascript")

        # Теги с одинаковыми именами должны иметь одинаковый хэш
        self.assertEqual(hash(tag1), hash(tag2))
        self.assertNotEqual(hash(tag1), hash(tag3))

    def test_task_priority(self):
        """Тест приоритета задачи"""
        high_priority = Task(description="Важная", priority="high")
        medium_priority = Task(description="Обычная", priority="medium")
        low_priority = Task(description="Несрочная", priority="low")

        self.assertEqual(high_priority.priority, "high")
        self.assertEqual(medium_priority.priority, "medium")
        self.assertEqual(low_priority.priority, "low")

    def test_web_bookmark_favicon(self):
        """Тест favicon закладки"""
        bookmark = WebBookmark(
            "https://example.com",
            "Example",
            favicon_url="https://example.com/favicon.ico"
        )
        self.assertEqual(bookmark.favicon_url, "https://example.com/favicon.ico")

    def test_note_repr_representation(self):
        """Тест repr представления заметки"""
        note = Note("Тест", "Содержимое", note_id=1)
        repr_str = repr(note)
        self.assertIn("Note(id=1, title='Тест'", repr_str)

    def test_tag_repr_representation(self):
        """Тест repr представления тега"""
        tag = Tag("python", tag_id=1)
        repr_str = repr(tag)
        self.assertIn("Tag(id=1, name='python')", repr_str)

    def test_task_repr_representation(self):
        """Тест repr представления задачи"""
        task = Task(description="Описание", task_id=1)
        repr_str = repr(task)
        self.assertIn("Task(id=1, description='Описание'", repr_str)

    def test_web_bookmark_repr_representation(self):
        """Тест repr представления веб-закладки"""
        bookmark = WebBookmark("https://test.com", "Test", bookmark_id=1)
        repr_str = repr(bookmark)
        self.assertIn("WebBookmark(id=1, title='Test'", repr_str)

    def test_workspace_repr_representation(self):
        """Тест repr представления рабочего пространства"""
        workspace = Workspace("Проект", workspace_id=1)
        repr_str = repr(workspace)
        self.assertIn("Workspace(id=1, name='Проект'", repr_str)

    def test_note_remove_nonexistent_tag(self):
        """Тест удаления несуществующего тега"""
        note = Note("Заметка", "Содержимое")
        tag = Tag("test")
        note.remove_tag(tag)  # Не должно вызывать ошибку
        self.assertEqual(len(note.tags), 0)

    def test_web_bookmark_get_domain_error_handling(self):
        """Тест обработки ошибок в get_domain"""
        bookmark = WebBookmark("invalid_url", "Test")
        domain = bookmark.get_domain()
        # При ошибке парсинга возвращается пустая строка
        self.assertEqual(domain, "")

    def test_tag_equality_with_non_tag(self):
        """Тест сравнения тега с не-тегом"""
        tag = Tag("python")
        self.assertNotEqual(tag, 123)


if __name__ == '__main__':
    unittest.main(verbosity=2)
