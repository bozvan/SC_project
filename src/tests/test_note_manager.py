import os
import sys
import unittest
import tempfile
import shutil
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager


class TestNoteManager(unittest.TestCase):
    """Тесты для NoteManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную директорию для тестовых БД
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_note_manager.db")

        # Инициализируем DatabaseManager
        self.db = DatabaseManager(self.db_path)
        self.tag_manager = TagManager(self.db)
        self.note_manager = NoteManager(self.db, self.tag_manager)

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
        # Теги нормализуются к нижнему регистру
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
        self.assertIsNotNone(created_note)

        retrieved_note = self.note_manager.get(created_note.id)

        self.assertIsNotNone(retrieved_note)
        self.assertEqual(created_note.id, retrieved_note.id)
        self.assertEqual(created_note.title, retrieved_note.title)

    def test_update_note(self):
        """Тест обновления заметки"""
        note = self.note_manager.create("Старый заголовок", "Старое содержимое")
        self.assertIsNotNone(note)

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
        self.assertIsNotNone(note)
        self.assertEqual(len(note.tags), 1)

        # Обновляем теги
        success = self.note_manager.update(
            note.id,
            tags=["Новый тег 1", "Новый тег 2"]
        )
        self.assertTrue(success)

        updated_note = self.note_manager.get(note.id)
        tag_names = [tag.name for tag in updated_note.tags]
        # Должно быть 2 новых тега
        self.assertEqual(len(tag_names), 2)
        self.assertIn("новый тег 1", tag_names)
        self.assertIn("новый тег 2", tag_names)
        self.assertNotIn("старый тег", tag_names)

    def test_delete_note(self):
        """Тест удаления заметки"""
        note = self.note_manager.create("Удаляемая заметка", "Содержимое")
        self.assertIsNotNone(note)

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

        # Ищем по тегу "Работа" - используем нижний регистр как в базе
        results = self.note_manager.search(tag_names=["работа"])
        self.assertEqual(len(results), 2)

        # Ищем по двум тегам
        results = self.note_manager.search(tag_names=["работа", "важное"])
        self.assertEqual(len(results), 1)

    def test_search_by_text_and_tags(self):
        """Тест комбинированного поиска"""
        self.note_manager.create("Python задачи", "Важные задачи", tags=["Работа"])
        self.note_manager.create("Python заметки", "Личные заметки", tags=["Личное"])
        self.note_manager.create("JavaScript задачи", "Задачи", tags=["Работа"])

        # Ищем "Python" с тегом "Работа" - используем нижний регистр для тега
        results = self.note_manager.search("Python", ["работа"])
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
        self.assertIsNotNone(note)

        success = self.note_manager.add_tag_to_note(note.id, "Новый тег")
        self.assertTrue(success)

        updated_note = self.note_manager.get(note.id)
        tag_names = [tag.name for tag in updated_note.tags]
        self.assertIn("новый тег", tag_names)

    def test_create_bookmark(self):
        """Тест создания закладки"""
        bookmark = self.note_manager.create_bookmark(
            "https://example.com",
            "Пример сайта",
            "Описание примера",
            tags=["веб", "пример"]
        )

        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.note_type, "bookmark")
        self.assertEqual(bookmark.url, "https://example.com")
        self.assertEqual(bookmark.title, "Пример сайта")
        self.assertEqual(len(bookmark.tags), 2)

    def test_create_bookmark_invalid_url(self):
        """Тест создания закладки с невалидным URL"""
        # Тестируем различные невалидные URL - они должны быть отклонены
        bookmark = self.note_manager.create_bookmark("invalid-url")
        self.assertIsNone(bookmark, "Невалидный URL должен быть отклонен")

        bookmark = self.note_manager.create_bookmark("http://")
        self.assertIsNone(bookmark, "URL без домена должен быть отклонен")

        bookmark = self.note_manager.create_bookmark("https://")
        self.assertIsNone(bookmark, "URL без домена должен быть отклонен")

        bookmark = self.note_manager.create_bookmark("")
        self.assertIsNone(bookmark, "Пустой URL должен быть отклонен")

        # URL без схемы, но с доменом должен нормализоваться и быть принят
        bookmark = self.note_manager.create_bookmark("example.com")
        self.assertIsNotNone(bookmark, "URL без схемы должен нормализоваться")

    def test_create_bookmark_without_title(self):
        """Тест создания закладки без заголовка"""
        bookmark = self.note_manager.create_bookmark("https://example.com")
        self.assertIsNotNone(bookmark)
        # Если заголовок не указан, должен использоваться URL
        self.assertEqual(bookmark.title, "https://example.com")

    def test_get_all_bookmarks(self):
        """Тест получения всех закладок"""
        self.note_manager.create_bookmark("https://example1.com", "Сайт 1")
        self.note_manager.create_bookmark("https://example2.com", "Сайт 2")
        self.note_manager.create("Обычная заметка", "Содержимое")  # Обычная заметка

        bookmarks = self.note_manager.get_all_bookmarks()
        self.assertEqual(len(bookmarks), 2)

        # Проверяем, что все возвращенные записи - закладки
        for bookmark in bookmarks:
            self.assertEqual(bookmark.note_type, "bookmark")

    def test_search_bookmarks(self):
        """Тест поиска закладок"""
        self.note_manager.create_bookmark("https://python.org", "Python Official", "Официальный сайт Python",
                                          tags=["программирование"])
        self.note_manager.create_bookmark("https://docs.python.org", "Python Documentation", "Документация Python",
                                          tags=["документация"])
        self.note_manager.create("Python заметка", "Заметка о Python")  # Обычная заметка

        # Ищем закладки по тексту
        results = self.note_manager.search_bookmarks("Python")
        self.assertEqual(len(results), 2)

        # Ищем закладки по тегу (нижний регистр)
        results = self.note_manager.search_bookmarks(tag_names=["документация"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Documentation")

    def test_workspace_isolation(self):
        """Тест изоляции рабочих пространств"""
        # Создаем заметки в разных workspace
        note1 = self.note_manager.create("Заметка 1", "Содержимое 1", workspace_id=1)
        note2 = self.note_manager.create("Заметка 2", "Содержимое 2", workspace_id=2)

        self.assertIsNotNone(note1)
        self.assertIsNotNone(note2)

        # Получаем заметки только для workspace 1
        notes_workspace1 = self.note_manager.get_notes_by_workspace(1)
        self.assertEqual(len(notes_workspace1), 1)
        self.assertEqual(notes_workspace1[0].title, "Заметка 1")

        # Получаем заметки только для workspace 2
        notes_workspace2 = self.note_manager.get_notes_by_workspace(2)
        self.assertEqual(len(notes_workspace2), 1)
        self.assertEqual(notes_workspace2[0].title, "Заметка 2")

    def test_note_with_special_characters(self):
        """Тест создания заметки со специальными символами"""
        title = "Заметка с спец. символами: !@#$%^&*()"
        content = "Содержимое с эмодзи 😊 и Unicode символами"

        note = self.note_manager.create(title, content)
        self.assertIsNotNone(note)
        self.assertEqual(note.title, title)
        self.assertEqual(note.content, content)

    def test_note_dates(self):
        """Тест корректности дат создания и изменения"""
        note = self.note_manager.create("Заметка с датами", "Содержимое")
        self.assertIsNotNone(note)

        # Проверяем, что даты установлены
        self.assertIsNotNone(note.created_date)
        self.assertIsNotNone(note.modified_date)

        # Проверяем, что даты являются объектами datetime
        self.assertIsInstance(note.created_date, datetime)
        self.assertIsInstance(note.modified_date, datetime)

    def test_note_content_types(self):
        """Тест создания заметок с разными типами контента"""
        # HTML контент
        html_note = self.note_manager.create(
            "HTML заметка",
            "<h1>Заголовок</h1><p>Параграф</p>",
            content_type="html"
        )
        self.assertIsNotNone(html_note)
        self.assertEqual(html_note.content_type, "html")

        # Plain text контент
        plain_note = self.note_manager.create(
            "Текстовая заметка",
            "Простой текст",
            content_type="plain"
        )
        self.assertIsNotNone(plain_note)
        self.assertEqual(plain_note.content_type, "plain")

    def test_note_without_content(self):
        """Тест создания заметки без содержимого"""
        note = self.note_manager.create("Заметка без содержимого", "")
        self.assertIsNotNone(note)
        self.assertEqual(note.content, "")

    def test_update_note_partial(self):
        """Тест частичного обновления заметки"""
        note = self.note_manager.create("Исходная заметка", "Исходное содержимое", tags=["исходный"])
        self.assertIsNotNone(note)
        self.assertEqual(len(note.tags), 1)

        # Обновляем только заголовок (не передаем теги)
        success = self.note_manager.update(note.id, title="Обновленный заголовок")
        self.assertTrue(success)

        updated_note = self.note_manager.get(note.id)
        self.assertEqual(updated_note.title, "Обновленный заголовок")
        self.assertEqual(updated_note.content, "Исходное содержимое")  # Не изменилось
        # Теги должны остаться прежними при частичном обновлении
        self.assertEqual(len(updated_note.tags), 1)

    def test_search_case_insensitive_tags(self):
        """Тест поиска по тегам без учета регистра"""
        self.note_manager.create("Заметка", "Содержимое", tags=["Python", "JavaScript"])

        # Поиск в разном регистре должен работать
        results1 = self.note_manager.search(tag_names=["python"])
        results2 = self.note_manager.search(tag_names=["PYTHON"])
        results3 = self.note_manager.search(tag_names=["Python"])

        self.assertEqual(len(results1), 1)
        self.assertEqual(len(results2), 1)
        self.assertEqual(len(results3), 1)

    def test_create_bookmark_normalization(self):
        """Тест нормализации URL при создании закладки"""
        # URL без схемы должен нормализоваться
        bookmark = self.note_manager.create_bookmark("example.com", "Пример")
        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.url, "https://example.com")

        # URL с www должен нормализоваться
        bookmark = self.note_manager.create_bookmark("www.example.com", "Пример")
        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.url, "https://www.example.com")

    def test_update_note_with_empty_tags(self):
        """Тест обновления заметки с пустым списком тегов"""
        note = self.note_manager.create("Заметка", "Содержимое", tags=["тег1", "тег2"])
        self.assertIsNotNone(note)
        self.assertEqual(len(note.tags), 2)

        # Обновляем с пустым списком тегов - теги должны быть удалены
        success = self.note_manager.update(note.id, tags=[])
        self.assertTrue(success)

        updated_note = self.note_manager.get(note.id)
        self.assertEqual(len(updated_note.tags), 0)

    def test_update_note_without_tags_param(self):
        """Тест обновления заметки без передачи параметра тегов"""
        note = self.note_manager.create("Заметка", "Содержимое", tags=["тег1", "тег2"])
        self.assertIsNotNone(note)
        self.assertEqual(len(note.tags), 2)

        # Обновляем без передачи тегов - теги должны остаться прежними
        success = self.note_manager.update(note.id, title="Новый заголовок")
        self.assertTrue(success)

        updated_note = self.note_manager.get(note.id)
        self.assertEqual(updated_note.title, "Новый заголовок")
        self.assertEqual(len(updated_note.tags), 2)  # Теги не изменились


if __name__ == '__main__':
    unittest.main(verbosity=2)