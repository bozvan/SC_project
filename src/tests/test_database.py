import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.database_manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Тесты для DatabaseManager"""

    def setUp(self):
        """Настройка перед каждым тестом - используем БД в памяти"""
        self.db = DatabaseManager(":memory:")

    def tearDown(self):
        """Очистка после каждого теста"""
        if hasattr(self, 'db') and hasattr(self.db, 'close'):
            self.db.close()

    def test_database_creation(self):
        """Тест создания базы данных и таблиц"""

        note_id = self.db.create_note("Тест", "Тестовое содержимое")
        self.assertIsNotNone(note_id)

        note = self.db.get_note_by_id(note_id)
        self.assertIsNotNone(note)
        self.assertEqual(note[1], "Тест")

    def test_create_note(self):
        """Тест создания заметки"""
        note_id = self.db.create_note("Тестовая заметка", "Это содержимое тестовой заметки")

        # Проверяем, что ID возвращается (не None)
        self.assertIsNotNone(note_id)
        self.assertIsInstance(note_id, int)

        # Проверяем, что заметка действительно сохранена в БД
        notes = self.db.get_all_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0][1], "Тестовая заметка")
        self.assertEqual(notes[0][2], "Это содержимое тестовой заметки")

    def test_get_note_by_id(self):
        """Тест получения заметки по ID"""
        note_id = self.db.create_note("Заметка для поиска", "Содержимое для поиска")

        note = self.db.get_note_by_id(note_id)
        self.assertIsNotNone(note)
        self.assertEqual(note[1], "Заметка для поиска")

    def test_search_notes(self):
        """Тест поиска заметок"""
        self.db.create_note("Покупки", "Купить молоко и хлеб")
        self.db.create_note("Работа", "Завершить проект по Python")
        self.db.create_note("Личное", "Прочитать книгу о Python")

        results = self.db.search_notes("Python")
        self.assertEqual(len(results), 2)

        titles = [note[1] for note in results]
        self.assertIn("Работа", titles)
        self.assertIn("Личное", titles)
        self.assertNotIn("Покупки", titles)

    def test_empty_search(self):
        """Тест поиска с пустым запросом (должен вернуть все заметки)"""
        for i in range(3):
            self.db.create_note(f"Заметка {i}", f"Содержимое {i}")

        results = self.db.search_notes("")
        self.assertEqual(len(results), 3)

    def test_update_note(self):
        """Тест обновления заметки"""
        note_id = self.db.create_note("Старый заголовок", "Старое содержимое")

        success = self.db.update_note(note_id, "Новый заголовок", "Новое содержимое")
        self.assertTrue(success)

        updated_note = self.db.get_note_by_id(note_id)
        self.assertEqual(updated_note[1], "Новый заголовок")
        self.assertEqual(updated_note[2], "Новое содержимое")

    def test_delete_note(self):
        """Тест удаления заметки"""
        note_id = self.db.create_note("Заметка для удаления", "Содержимое")

        notes_before = self.db.get_all_notes()
        self.assertEqual(len(notes_before), 1)

        success = self.db.delete_note(note_id)
        self.assertTrue(success)

        notes_after = self.db.get_all_notes()
        self.assertEqual(len(notes_after), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)