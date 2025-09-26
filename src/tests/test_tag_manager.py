import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager


class TestTagManager(unittest.TestCase):
    """Тесты для TagManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db = DatabaseManager(":memory:")  # БД в памяти для тестов
        self.tag_manager = TagManager(self.db)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.db.close()

    def test_create_tag(self):
        """Тест создания тега"""
        tag = self.tag_manager.create("Python")
        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, "python")
        self.assertIsNotNone(tag.id)

    def test_create_duplicate_tag(self):
        """Тест создания дубликата тега"""
        tag1 = self.tag_manager.create("Python")
        tag2 = self.tag_manager.create("python")  # Дубликат
        tag3 = self.tag_manager.create("PYTHON")  # Дубликат в верхнем регистре

        self.assertEqual(tag1.id, tag2.id)  # Должны быть одинаковые ID
        self.assertEqual(tag1.id, tag3.id)

    def test_create_empty_tag(self):
        """Тест создания тега с пустым именем"""
        tag = self.tag_manager.create("")
        self.assertIsNone(tag)

        tag = self.tag_manager.create("   ")
        self.assertIsNone(tag)

    def test_get_tag(self):
        """Тест получения тега по ID"""
        created_tag = self.tag_manager.create("JavaScript")
        retrieved_tag = self.tag_manager.get(created_tag.id)

        self.assertIsNotNone(retrieved_tag)
        self.assertEqual(created_tag.id, retrieved_tag.id)
        self.assertEqual(created_tag.name, retrieved_tag.name)

    def test_get_nonexistent_tag(self):
        """Тест получения несуществующего тега"""
        tag = self.tag_manager.get(999)  # Несуществующий ID
        self.assertIsNone(tag)

    def test_get_all_tags(self):
        """Тест получения всех тегов"""
        # Создаем несколько тегов
        tags_to_create = ["Python", "JavaScript", "Работа", "Личное"]
        created_tags = []

        for tag_name in tags_to_create:
            tag = self.tag_manager.create(tag_name)
            created_tags.append(tag)

        # Получаем все теги
        all_tags = self.tag_manager.get_all()

        self.assertEqual(len(all_tags), len(tags_to_create))

        # Проверяем, что все созданные теги присутствуют
        tag_names = [tag.name for tag in all_tags]
        for tag in created_tags:
            self.assertIn(tag.name, tag_names)

    def test_get_by_name(self):
        """Тест поиска тега по имени"""
        self.tag_manager.create("Python")

        # Поиск в разных регистрах
        tag1 = self.tag_manager.get_by_name("python")
        tag2 = self.tag_manager.get_by_name("Python")
        tag3 = self.tag_manager.get_by_name("PYTHON")

        self.assertIsNotNone(tag1)
        self.assertEqual(tag1.name, "python")
        self.assertEqual(tag1.id, tag2.id)
        self.assertEqual(tag1.id, tag3.id)

    def test_delete_tag(self):
        """Тест удаления тега"""
        tag = self.tag_manager.create("Удаляемый тег")
        tag_id = tag.id

        # Удаляем тег
        success = self.tag_manager.delete(tag_id)
        self.assertTrue(success)

        # Проверяем, что тег удален
        deleted_tag = self.tag_manager.get(tag_id)
        self.assertIsNone(deleted_tag)

    def test_delete_nonexistent_tag(self):
        """Тест удаления несуществующего тега"""
        success = self.tag_manager.delete(999)
        self.assertFalse(success)

    def test_get_or_create(self):
        """Тест метода get_or_create"""
        # Первый вызов должен создать тег
        tag1 = self.tag_manager.get_or_create("Новый тег")
        self.assertIsNotNone(tag1.id)

        # Второй вызов должен вернуть существующий тег
        tag2 = self.tag_manager.get_or_create("новый тег")  # Другой регистр
        self.assertEqual(tag1.id, tag2.id)

    def test_update_tag(self):
        """Тест обновления тега"""
        tag = self.tag_manager.create("Старое имя")

        # Обновляем тег
        success = self.tag_manager.update(tag.id, "Новое имя")
        self.assertTrue(success)

        # Проверяем обновление
        updated_tag = self.tag_manager.get(tag.id)
        self.assertEqual(updated_tag.name, "новое имя")


if __name__ == '__main__':
    unittest.main(verbosity=2)
