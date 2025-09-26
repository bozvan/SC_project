import unittest
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.core.models import Note, Tag, Task, WebBookmark


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

    def test_tag_creation(self):
        """Тест создания тега"""
        tag = Tag("Python")
        self.assertEqual(tag.name, "python")  # Имя должно быть нормализовано
        self.assertIsNone(tag.id)

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
        """Тест создания задачи"""
        task = Task("Изучить Python")
        self.assertEqual(task.description, "Изучить Python")
        self.assertFalse(task.is_completed)
        self.assertIsNone(task.due_date)

    def test_task_toggle(self):
        """Тест переключения статуса задачи"""
        task = Task("Тестовая задача")
        self.assertFalse(task.is_completed)

        task.toggle_completion()
        self.assertTrue(task.is_completed)

        task.toggle_completion()
        self.assertFalse(task.is_completed)

    def test_web_bookmark_creation(self):
        """Тест создания веб-закладки"""
        bookmark = WebBookmark("https://python.org", "Python Official Site")
        self.assertEqual(bookmark.url, "https://python.org")
        self.assertEqual(bookmark.title, "Python Official Site")
        self.assertEqual(bookmark.description, "")

    def test_emplty_web_bookmark(self):
        """Тест на проверку корректного создания веб-закладки"""
        bookmark = WebBookmark()
        self.assertEqual(bookmark.title, "")
        self.assertEqual(bookmark.description, "")
        self.assertEqual(bookmark.url, None)
        self.assertEqual(bookmark.id, None)


if __name__ == '__main__':
    unittest.main(verbosity=2)