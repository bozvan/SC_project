import os
import sys
import unittest
import tempfile
import shutil

# Добавляем корень проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager


class TestTagManager(unittest.TestCase):
    """Тесты для TagManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную директорию для тестовых БД
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_tag_manager.db")

        # Инициализируем DatabaseManager
        self.db = DatabaseManager(self.db_path)
        self.tag_manager = TagManager(self.db)

        # Создаем второе рабочее пространство для тестов изоляции
        self._create_workspace_2()

    def _create_workspace_2(self):
        """Создает второе рабочее пространство для тестов"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO workspaces (id, name, description, is_default) VALUES (?, ?, ?, ?)",
                    (2, "WORKSPACE2", "Второе рабочее пространство", False)
                )
                conn.commit()
        except Exception as e:
            print(f"⚠️ Не удалось создать workspace 2: {e}")

    def tearDown(self):
        """Очистка после каждого теста"""
        self.db.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_tag(self):
        """Тест создания тега"""
        tag = self.tag_manager.create("Python")
        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, "python")
        self.assertIsNotNone(tag.id)

    def test_create_duplicate_tag(self):
        """Тест создания дубликата тега"""
        tag1 = self.tag_manager.create("Python")
        self.assertIsNotNone(tag1, "Первый тег должен быть создан успешно")

        tag2 = self.tag_manager.create("python")  # Дубликат
        self.assertIsNotNone(tag2, "Второй тег должен быть создан успешно")

        tag3 = self.tag_manager.create("PYTHON")  # Дубликат в верхнем регистре
        self.assertIsNotNone(tag3, "Третий тег должен быть создан успешно")

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
        self.assertIsNotNone(created_tag, "Тег должен быть создан успешно")

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
            self.assertIsNotNone(tag, f"Тег '{tag_name}' должен быть создан успешно")
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
        created_tag = self.tag_manager.create("Python")
        self.assertIsNotNone(created_tag, "Тег должен быть создан успешно")

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
        self.assertIsNotNone(tag, "Тег должен быть создан успешно")
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
        self.assertIsNotNone(tag1)
        self.assertIsNotNone(tag1.id)

        # Второй вызов должен вернуть существующий тег
        tag2 = self.tag_manager.get_or_create("новый тег")  # Другой регистр
        self.assertIsNotNone(tag2)
        self.assertEqual(tag1.id, tag2.id)

    def test_update_tag(self):
        """Тест обновления тега"""
        tag = self.tag_manager.create("Старое имя")
        self.assertIsNotNone(tag, "Тег должен быть создан успешно")

        # Обновляем тег
        success = self.tag_manager.update(tag.id, "Новое имя")
        self.assertTrue(success)

        # Проверяем обновление
        updated_tag = self.tag_manager.get(tag.id)
        self.assertEqual(updated_tag.name, "новое имя")

    def test_get_tags_for_note(self):
        """Тест получения тегов для заметки"""
        # Создаем тег
        tag = self.tag_manager.create("Тестовый тег")
        self.assertIsNotNone(tag)

        # Пока просто проверяем, что метод не падает
        tags = self.tag_manager.get_tags_for_note(1)
        self.assertIsInstance(tags, list)

    def test_get_popular_tags(self):
        """Тест получения популярных тегов"""
        tags = self.tag_manager.get_popular_tags(limit=5)
        self.assertIsInstance(tags, list)

    def test_get_tags_by_workspace(self):
        """Тест получения тегов по рабочему пространству"""
        # Создаем теги в разных workspace
        tag1 = self.tag_manager.create("Тег в workspace 1", workspace_id=1)
        tag2 = self.tag_manager.create("Тег в workspace 2", workspace_id=2)

        self.assertIsNotNone(tag1)
        self.assertIsNotNone(tag2)

        # Получаем теги только для workspace 1
        tags_ws1 = self.tag_manager.get_tags_by_workspace(1)
        self.assertEqual(len(tags_ws1), 1)
        self.assertEqual(tags_ws1[0].name, "тег в workspace 1")

        # Получаем теги только для workspace 2
        tags_ws2 = self.tag_manager.get_tags_by_workspace(2)
        self.assertEqual(len(tags_ws2), 1)
        self.assertEqual(tags_ws2[0].name, "тег в workspace 2")

    def test_get_notes_by_tag(self):
        """Тест получения заметок по тегу"""
        # Создаем тег
        tag = self.tag_manager.create("Тестовый тег")
        self.assertIsNotNone(tag)

        # Пока просто проверяем, что метод не падает
        note_ids = self.tag_manager.get_notes_by_tag("Тестовый тег")
        self.assertIsInstance(note_ids, list)

    def test_create_tag_in_different_workspaces(self):
        """Тест создания одинаковых тегов в разных рабочих пространствах"""
        # Создаем тег с одинаковым именем в разных workspace
        tag1 = self.tag_manager.create("Общий тег", workspace_id=1)
        tag2 = self.tag_manager.create("Общий тег", workspace_id=2)

        self.assertIsNotNone(tag1)
        self.assertIsNotNone(tag2)

        # Теги должны иметь разные ID, так как они в разных workspace
        self.assertNotEqual(tag1.id, tag2.id)

        # Но одинаковые имена
        self.assertEqual(tag1.name, tag2.name)

    def test_get_all_with_workspace_filter(self):
        """Тест получения тегов с фильтром по workspace"""
        # Создаем теги в разных workspace
        self.tag_manager.create("Тег 1", workspace_id=1)
        self.tag_manager.create("Тег 2", workspace_id=1)
        self.tag_manager.create("Тег 3", workspace_id=2)

        # Получаем теги только для workspace 1
        tags_ws1 = self.tag_manager.get_all(workspace_id=1)
        self.assertEqual(len(tags_ws1), 2)

        # Получаем теги только для workspace 2
        tags_ws2 = self.tag_manager.get_all(workspace_id=2)
        self.assertEqual(len(tags_ws2), 1)

        # Получаем все теги без фильтра
        all_tags = self.tag_manager.get_all()
        self.assertEqual(len(all_tags), 3)

    def test_get_by_name_with_workspace(self):
        """Тест поиска тега по имени с указанием workspace"""
        # Создаем теги с одинаковым именем в разных workspace
        tag1 = self.tag_manager.create("Одинаковое имя", workspace_id=1)
        tag2 = self.tag_manager.create("Одинаковое имя", workspace_id=2)

        self.assertIsNotNone(tag1)
        self.assertIsNotNone(tag2)

        # Ищем в конкретном workspace
        found_tag1 = self.tag_manager.get_by_name("Одинаковое имя", workspace_id=1)
        found_tag2 = self.tag_manager.get_by_name("Одинаковое имя", workspace_id=2)

        self.assertIsNotNone(found_tag1)
        self.assertIsNotNone(found_tag2)
        self.assertEqual(found_tag1.id, tag1.id)
        self.assertEqual(found_tag2.id, tag2.id)

    def test_update_tag_duplicate_name_check(self):
        """Тест проверки дубликатов при обновлении тега"""
        # Создаем два разных тега
        tag1 = self.tag_manager.create("Тег 1")
        tag2 = self.tag_manager.create("Тег 2")

        self.assertIsNotNone(tag1)
        self.assertIsNotNone(tag2)

        # Пытаемся переименовать tag2 в имя tag1 - должно не получиться
        success = self.tag_manager.update(tag2.id, "Тег 1")
        self.assertFalse(success)

        # Проверяем, что тег2 не изменился
        updated_tag2 = self.tag_manager.get(tag2.id)
        self.assertEqual(updated_tag2.name, "тег 2")


if __name__ == '__main__':
    unittest.main(verbosity=2)