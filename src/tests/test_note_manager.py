import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager


class TestNoteManager(unittest.TestCase):
    """Тесты для NoteManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db = DatabaseManager(":memory:")
        self.tag_manager = TagManager(self.db)
        self.note_manager = NoteManager(self.db, self.tag_manager)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.db.close()

    def test_create_note_without_tags(self):
        """Тест создания заметки без тегов"""
        note = self.note_manager.create("Тестовая заметка", "Содержимое заметки")

        self.assertIsNotNone(note)
        self.assertEqual(note.title, "Тестовая заметка")
        self.assertEqual(note.content, "Содержимое заметки")
        self.assertEqual(len(note.tags), 0)
        self.assertIsNotNone(note.id)

    def test_create_note_with_tags(self):
        """Тест создания заметки с тегами"""
        note = self.note_manager.create(
            "Заметка с тегами",
            "Содержимое",
            tags=["Python", "Работа", "Важное"]
        )

        self.assertIsNotNone(note)
        self.assertEqual(len(note.tags), 3)
        tag_names = [tag.name for tag in note.tags]
        self.assertIn("python", tag_names)
        self.assertIn("работа", tag_names)
        self.assertIn("важное", tag_names)

    def test_create_note_empty_title(self):
        """Тест создания заметки с пустым заголовком"""
        note = self.note_manager.create("", "Содержимое")
        self.assertIsNone(note)

        note = self.note_manager.create("   ", "Содержимое")
        self.assertIsNone(note)

    def test_get_note(self):
        """Тест получения заметки по ID"""
        created_note = self.note_manager.create("Тест", "Содержимое")
        retrieved_note = self.note_manager.get(created_note.id)

        self.assertIsNotNone(retrieved_note)
        self.assertEqual(created_note.id, retrieved_note.id)
        self.assertEqual(created_note.title, retrieved_note.title)

    def test_update_note(self):
        """Тест обновления заметки"""
        note = self.note_manager.create("Старый заголовок", "Старое содержимое")

        # Обновляем заголовок и содержимое
        success = self.note_manager.update(
            note.id,
            title="Новый заголовок",
            content="Новое содержимое"
        )
        self.assertTrue(success)

        updated_note = self.note_manager.get(note.id)
        self.assertEqual(updated_note.title, "Новый заголовок")
        self.assertEqual(updated_note.content, "Новое содержимое")

    def test_update_note_tags(self):
        """Тест обновления тегов заметки"""
        note = self.note_manager.create("Заметка", "Содержимое", tags=["Старый тег"])

        # Обновляем теги
        success = self.note_manager.update(
            note.id,
            tags=["Новый тег 1", "Новый тег 2"]
        )
        self.assertTrue(success)

        updated_note = self.note_manager.get(note.id)
        tag_names = [tag.name for tag in updated_note.tags]
        self.assertEqual(len(tag_names), 2)
        self.assertIn("новый тег 1", tag_names)
        self.assertIn("новый тег 2", tag_names)
        self.assertNotIn("старый тег", tag_names)

    def test_delete_note(self):
        """Тест удаления заметки"""
        note = self.note_manager.create("Удаляемая заметка", "Содержимое")
        note_id = note.id

        success = self.note_manager.delete(note_id)
        self.assertTrue(success)

        deleted_note = self.note_manager.get(note_id)
        self.assertIsNone(deleted_note)

    def test_search_by_text(self):
        """Тест поиска заметок по тексту"""
        # Создаем тестовые заметки
        self.note_manager.create("Python программирование", "Изучаем Python")
        self.note_manager.create("JavaScript основы", "Изучаем JavaScript")
        self.note_manager.create("Рабочие задачи", "Задачи по Python проекту")

        # Ищем по "Python"
        results = self.note_manager.search("Python")
        self.assertEqual(len(results), 2)

        titles = [note.title for note in results]
        self.assertIn("Python программирование", titles)
        self.assertIn("Рабочие задачи", titles)

    def test_search_by_tags(self):
        """Тест поиска заметок по тегам"""
        # Создаем заметки с разными тегами
        self.note_manager.create("Заметка 1", "Содержимое", tags=["Работа", "Важное"])
        self.note_manager.create("Заметка 2", "Содержимое", tags=["Личное"])
        self.note_manager.create("Заметка 3", "Содержимое", tags=["Работа", "Срочное"])

        # Ищем по тегу "Работа"
        results = self.note_manager.search(tag_names=["Работа"])
        self.assertEqual(len(results), 2)

        # Ищем по двум тегам
        results = self.note_manager.search(tag_names=["Работа", "Важное"])
        self.assertEqual(len(results), 1)

    def test_search_by_text_and_tags(self):
        """Тест комбинированного поиска"""
        self.note_manager.create("Python задачи", "Важные задачи", tags=["Работа"])
        self.note_manager.create("Python заметки", "Личные заметки", tags=["Личное"])
        self.note_manager.create("JavaScript задачи", "Задачи", tags=["Работа"])

        # Ищем "Python" с тегом "Работа"
        results = self.note_manager.search("Python", ["Работа"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python задачи")

    def test_get_all_notes(self):
        """Тест получения всех заметок"""
        self.note_manager.create("Заметка 1", "Содержимое 1")
        self.note_manager.create("Заметка 2", "Содержимое 2")
        self.note_manager.create("Заметка 3", "Содержимое 3")

        all_notes = self.note_manager.get_all()
        self.assertEqual(len(all_notes), 3)

    def test_add_tag_to_note(self):
        """Тест добавления тега к существующей заметке"""
        note = self.note_manager.create("Заметка", "Содержимое")

        success = self.note_manager.add_tag_to_note(note.id, "Новый тег")
        self.assertTrue(success)

        updated_note = self.note_manager.get(note.id)
        tag_names = [tag.name for tag in updated_note.tags]
        self.assertIn("новый тег", tag_names)


if __name__ == '__main__':
    unittest.main(verbosity=2)