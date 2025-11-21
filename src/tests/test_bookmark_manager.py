import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.database_manager import DatabaseManager
from src.core.bookmark_manager import BookmarkManager
from src.core.models import WebBookmark, Tag


class TestBookmarkManager(unittest.TestCase):
    """Тесты для BookmarkManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_bookmark_manager.db")
        self.db = DatabaseManager(self.db_path)
        self.bookmark_manager = BookmarkManager(self.db)

        # Создаем тестовый workspace
        self._create_test_workspace()

    def _create_test_workspace(self):
        """Создает тестовый workspace в БД"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            # Создаем workspace с id=1 (по умолчанию)
            cursor.execute("INSERT OR IGNORE INTO workspaces (id, name) VALUES (1, 'Default Workspace')")
            conn.commit()

    def tearDown(self):
        """Очистка после каждого теста"""
        self.db.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Тестирование инициализации BookmarkManager"""
        self.assertIsNotNone(self.bookmark_manager.db)
        self.assertIsNotNone(self.bookmark_manager.session)

    def test_validate_url_valid_urls(self):
        """Тестирование валидации корректных URL"""
        valid_urls = [
            "https://python.org",
            "python.org",
            "www.python.org",
            "github.com",
            "http://example.com",
            "localhost",
            "https://sub.domain.co.uk/path?query=value#fragment"
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(
                    self.bookmark_manager.validate_url(url),
                    f"URL '{url}' должен быть валидным"
                )

    def test_validate_url_invalid_urls(self):
        """Тестирование валидации некорректных URL"""
        invalid_urls = [
            "not-a-url",
            "",
            "   ",
            "http://",
            "path/to/file"
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    self.bookmark_manager.validate_url(url),
                    f"URL '{url}' должен быть невалидным"
                )

    def test_normalize_url(self):
        """Тестирование нормализации URL"""
        test_cases = [
            ("python.org", "https://python.org"),
            ("www.python.org", "https://www.python.org"),
            ("https://example.com", "https://example.com"),
            ("http://example.com", "http://example.com"),
            ("", ""),
            ("   ", "")
        ]

        for input_url, expected_output in test_cases:
            with self.subTest(url=input_url):
                result = self.bookmark_manager.normalize_url(input_url)
                self.assertEqual(result, expected_output)

    def test_extract_domain(self):
        """Тестирование извлечения домена из URL"""
        test_cases = [
            ("https://example.com/path", "example.com"),
            ("http://sub.domain.co.uk", "sub.domain.co.uk"),
            ("invalid-url", "")
        ]

        for url, expected_domain in test_cases:
            with self.subTest(url=url):
                result = self.bookmark_manager._extract_domain(url)
                self.assertEqual(result, expected_domain)

    @patch('src.core.bookmark_manager.requests.Session')
    def test_parse_url_metadata_success(self, mock_session_class):
        """Тестирование успешного получения метаданных"""
        mock_session = Mock()
        mock_response = Mock()

        mock_response.content = """
        <html>
            <head>
                <title>Test Page Title</title>
                <meta name="description" content="Test description">
                <link rel="icon" href="/favicon.ico">
            </head>
        </html>
        """
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.raise_for_status = Mock()

        mock_session.get.return_value = mock_response
        mock_session.head.return_value.status_code = 200
        mock_session_class.return_value = mock_session

        self.bookmark_manager.session = mock_session

        metadata = self.bookmark_manager.parse_url_metadata("https://example.com")

        self.assertEqual(metadata['title'], "Test Page Title")
        self.assertEqual(metadata['description'], "Test description")
        self.assertEqual(metadata['status_code'], 200)

    @patch('src.core.bookmark_manager.requests.Session')
    def test_parse_url_metadata_failure(self, mock_session_class):
        """Тестирование получения метаданных при ошибке"""
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Connection error")
        mock_session_class.return_value = mock_session

        self.bookmark_manager.session = mock_session

        metadata = self.bookmark_manager.parse_url_metadata("https://invalid-url.com")

        self.assertIn("недоступен", metadata['title'])
        self.assertIn("Не удалось загрузить страницу", metadata['description'])
        self.assertEqual(metadata['status_code'], 0)

    def test_create_bookmark_success(self):
        """Тестирование успешного создания закладки"""
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Test Bookmark",
            description="Test Description",
            tags=["тест", "пример"],
            favicon_url="https://example.com/favicon.ico"
        )

        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.url, "https://example.com")
        self.assertEqual(bookmark.title, "Test Bookmark")
        self.assertEqual(bookmark.description, "Test Description")
        self.assertEqual(len(bookmark.tags), 2)
        self.assertIn("тест", [tag.name for tag in bookmark.tags])

    def test_create_bookmark_auto_title(self):
        """Тестирование автоматического создания заголовка из домена"""
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="",  # Пустой заголовок
            description="Test"
        )

        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.title, "example.com")

    def test_create_bookmark_invalid_url(self):
        """Тестирование создания закладки с невалидным URL"""
        bookmark = self.bookmark_manager.create(
            url="invalid-url",
            title="Test Bookmark"
        )
        self.assertIsNone(bookmark)

    def test_create_bookmark_empty_url(self):
        """Тестирование создания закладки с пустым URL"""
        bookmark = self.bookmark_manager.create(url="", title="Test")
        self.assertIsNone(bookmark)

    def test_create_bookmark_favicon_handling(self):
        """Тестирование обработки favicon_url"""
        # Тест с корректным favicon_url
        bookmark1 = self.bookmark_manager.create(
            url="https://example.com",
            title="Test",
            favicon_url="https://example.com/favicon.ico"
        )
        self.assertEqual(bookmark1.favicon_url, "https://example.com/favicon.ico")

        # Тест с пустым favicon_url
        bookmark2 = self.bookmark_manager.create(
            url="https://example.com",
            title="Test",
            favicon_url=""
        )
        self.assertIsNone(bookmark2.favicon_url)

    def test_safe_create_bookmark(self):
        """Тестирование безопасного создания закладки"""
        bookmark = self.bookmark_manager.safe_create_bookmark(
            url="https://example.com",
            title="Test Bookmark",
            description="Test Description",
            tags=["safe-test"]
        )

        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.url, "https://example.com")
        self.assertEqual(bookmark.title, "Test Bookmark")
        self.assertIsNone(bookmark.favicon_url)

    @patch.object(BookmarkManager, 'parse_url_metadata')
    def test_add_bookmark_with_metadata_success(self, mock_parse_metadata):
        """Тестирование создания закладки с метаданными"""
        mock_parse_metadata.return_value = {
            'title': 'Mocked Title',
            'description': 'Mocked Description',
            'url': 'https://example.com',
            'status_code': 200,
            'favicon_url': None
        }

        bookmark = self.bookmark_manager.add_bookmark_with_metadata(
            url="https://example.com",
            tags=["mock-test"]
        )

        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.title, "Mocked Title")
        self.assertEqual(bookmark.description, "Mocked Description")

    def test_get_or_create_tag_with_connection(self):
        """Тестирование создания и получения тегов"""
        with self.bookmark_manager.db._get_connection() as conn:
            cursor = conn.cursor()

            # Создание нового тега
            new_tag = self.bookmark_manager._get_or_create_tag_with_connection(cursor, "new-tag")
            self.assertIsNotNone(new_tag)
            self.assertEqual(new_tag.name, "new-tag")

            # Получение существующего тега
            existing_tag = self.bookmark_manager._get_or_create_tag_with_connection(cursor, "new-tag")
            self.assertIsNotNone(existing_tag)
            self.assertEqual(existing_tag.name, "new-tag")

    def test_get_bookmark(self):
        """Тестирование получения закладки по ID"""
        # Сначала создаем закладку
        created_bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Test Bookmark",
            tags=["test"]
        )

        self.assertIsNotNone(created_bookmark)

        # Затем получаем ее по ID
        retrieved_bookmark = self.bookmark_manager.get(created_bookmark.id)

        self.assertIsNotNone(retrieved_bookmark)
        self.assertEqual(retrieved_bookmark.id, created_bookmark.id)
        self.assertEqual(retrieved_bookmark.title, "Test Bookmark")
        self.assertIsInstance(retrieved_bookmark.created_date, datetime)
        self.assertIsInstance(retrieved_bookmark.updated_date, datetime)

    def test_get_nonexistent_bookmark(self):
        """Тестирование получения несуществующей закладки"""
        bookmark = self.bookmark_manager.get(9999)
        self.assertIsNone(bookmark)

    def test_get_tags_for_bookmark(self):
        """Тестирование получения тегов для закладки"""
        # Создаем закладку с тегами
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Test",
            tags=["tag1", "tag2"]
        )

        tags = self.bookmark_manager.get_tags_for_bookmark(bookmark.id)
        self.assertEqual(len(tags), 2)
        tag_names = [tag.name for tag in tags]
        self.assertIn("tag1", tag_names)
        self.assertIn("tag2", tag_names)

    def test_get_all_bookmarks(self):
        """Тестирование получения всех закладок"""
        # Создаем несколько закладок
        bookmark1 = self.bookmark_manager.create(url="https://example1.com", title="First")
        bookmark2 = self.bookmark_manager.create(url="https://example2.com", title="Second")

        self.assertIsNotNone(bookmark1)
        self.assertIsNotNone(bookmark2)

        all_bookmarks = self.bookmark_manager.get_all()
        self.assertGreaterEqual(len(all_bookmarks), 2)

    def test_get_all_bookmarks_with_workspace(self):
        """Тестирование получения закладок с фильтром workspace"""
        # Создаем закладки в workspace 1
        bookmark1 = self.bookmark_manager.create(
            url="https://example1.com",
            title="First"
        )
        bookmark2 = self.bookmark_manager.create(
            url="https://example2.com",
            title="Second"
        )

        workspace_1_bookmarks = self.bookmark_manager.get_all(workspace_id=1)
        self.assertEqual(len(workspace_1_bookmarks), 2)

    def test_get_bookmarks_by_workspace(self):
        """Тестирование получения закладок по workspace"""
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Test"
        )

        bookmarks = self.bookmark_manager.get_bookmarks_by_workspace(1)
        self.assertEqual(len(bookmarks), 1)

    def test_search_bookmarks(self):
        """Тестирование поиска закладок по тексту"""
        # Создаем тестовые закладки
        bookmark1 = self.bookmark_manager.create(
            url="https://python.org",
            title="Python Programming",
            description="Official Python website"
        )
        bookmark2 = self.bookmark_manager.create(
            url="https://docs.python.org",
            title="Python Documentation",
            description="Python official documentation"
        )

        # Ищем по заголовку
        results_title = self.bookmark_manager.search("Python")
        self.assertEqual(len(results_title), 2)

        # Ищем по URL
        results_url = self.bookmark_manager.search("docs")
        self.assertEqual(len(results_url), 1)

        # Ищем по описанию
        results_desc = self.bookmark_manager.search("official")
        self.assertEqual(len(results_desc), 2)

        # Пустой поиск
        results_empty = self.bookmark_manager.search("")
        self.assertGreaterEqual(len(results_empty), 2)

    def test_search_by_tags(self):
        """Тестирование поиска закладок по тегам"""
        # Создаем закладки с тегами
        bookmark1 = self.bookmark_manager.create(
            url="https://example1.com",
            title="First",
            tags=["programming", "python"]
        )
        bookmark2 = self.bookmark_manager.create(
            url="https://example2.com",
            title="Second",
            tags=["docs", "python"]
        )

        # Поиск по одному тегу
        results_single = self.bookmark_manager.search_by_tags(["python"])
        self.assertEqual(len(results_single), 2)

        # Поиск по нескольким тегам
        results_multi = self.bookmark_manager.search_by_tags(["programming", "python"])
        self.assertEqual(len(results_multi), 1)

    def test_search_by_text_and_tags(self):
        """Тестирование комбинированного поиска по тексту и тегам"""
        bookmark1 = self.bookmark_manager.create(
            url="https://example1.com",
            title="Python Guide",
            tags=["programming", "python"]
        )
        bookmark2 = self.bookmark_manager.create(
            url="https://example2.com",
            title="Java Guide",
            tags=["programming", "java"]
        )

        results = self.bookmark_manager.search_by_text_and_tags("Guide", ["python"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Guide")

    def test_update_bookmark_description(self):
        """Тестирование обновления описания закладки"""
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Test",
            description="Old description"
        )

        success = self.bookmark_manager.update_bookmark_description(bookmark.id, "New description")
        self.assertTrue(success)

        updated_bookmark = self.bookmark_manager.get(bookmark.id)
        self.assertEqual(updated_bookmark.description, "New description")

    def test_update_bookmark_description_nonexistent(self):
        """Тестирование обновления описания несуществующей закладки"""
        success = self.bookmark_manager.update_bookmark_description(9999, "New description")
        self.assertFalse(success)

    def test_update_bookmark_method(self):
        """Тестирование метода update_bookmark"""
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Original Title",
            tags=["original"]
        )

        success = self.bookmark_manager.update_bookmark(
            bookmark_id=bookmark.id,
            title="Updated Title",
            url="https://updated.com",
            description="Updated Description",
            tags=["updated", "test"]
        )

        self.assertTrue(success)

        updated_bookmark = self.bookmark_manager.get(bookmark.id)
        self.assertEqual(updated_bookmark.title, "Updated Title")
        self.assertEqual(updated_bookmark.url, "https://updated.com")
        self.assertEqual(updated_bookmark.description, "Updated Description")
        self.assertEqual(len(updated_bookmark.tags), 2)

    def test_update_method_comprehensive(self):
        """Комплексное тестирование метода update"""
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Original"
        )

        success = self.bookmark_manager.update(
            bookmark_id=bookmark.id,
            title="Updated Title",
            description="New description",
            tags=["new-tag"],
            url="https://new-url.com",
            favicon_url="https://new-url.com/favicon.ico"
        )

        self.assertTrue(success)

        updated_bookmark = self.bookmark_manager.get(bookmark.id)
        self.assertEqual(updated_bookmark.title, "Updated Title")
        self.assertEqual(updated_bookmark.description, "New description")
        self.assertEqual(updated_bookmark.url, "https://new-url.com")
        self.assertEqual(updated_bookmark.favicon_url, "https://new-url.com/favicon.ico")

    def test_update_method_no_changes(self):
        """Тестирование update без изменений"""
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Test"
        )

        success = self.bookmark_manager.update(bookmark_id=bookmark.id)
        self.assertTrue(success)

    def test_update_method_invalid_url(self):
        """Тестирование update с невалидным URL"""
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Test"
        )

        success = self.bookmark_manager.update(
            bookmark_id=bookmark.id,
            url="invalid-url"
        )
        self.assertFalse(success)

    def test_delete_bookmark(self):
        """Тестирование удаления закладки"""
        bookmark = self.bookmark_manager.create(
            url="https://todelete.com",
            title="To Delete"
        )

        success = self.bookmark_manager.delete(bookmark.id)
        self.assertTrue(success)

        deleted_bookmark = self.bookmark_manager.get(bookmark.id)
        self.assertIsNone(deleted_bookmark)

    def test_delete_nonexistent_bookmark(self):
        """Тестирование удаления несуществующей закладки"""
        success = self.bookmark_manager.delete(9999)
        self.assertFalse(success)

    @patch.object(BookmarkManager, 'add_bookmark_with_metadata')
    def test_bulk_add_bookmarks(self, mock_add_bookmark):
        """Тестирование массового добавления закладок"""
        mock_bookmark = Mock(spec=WebBookmark)
        mock_add_bookmark.return_value = mock_bookmark

        urls = [
            "https://example1.com",
            "https://example2.com"
        ]

        created_bookmarks = self.bookmark_manager.bulk_add_bookmarks(
            urls=urls,
            common_tags=["bulk", "test"]
        )

        self.assertEqual(len(created_bookmarks), 2)
        self.assertEqual(mock_add_bookmark.call_count, 2)

    def test_get_bookmark_stats(self):
        """Тестирование получения статистики"""
        # Создаем несколько закладок
        self.bookmark_manager.create(url="https://example1.com", title="First")
        self.bookmark_manager.create(url="https://example2.com", title="Second", tags=["test"])

        stats = self.bookmark_manager.get_bookmark_stats()

        self.assertGreaterEqual(stats['total'], 2)
        self.assertGreaterEqual(stats['with_tags'], 1)
        self.assertGreaterEqual(stats['added_today'], 0)

    def test_get_bookmark_stats_with_workspace(self):
        """Тестирование получения статистики с фильтром workspace"""
        self.bookmark_manager.create(
            url="https://example.com",
            title="Test"
        )

        stats = self.bookmark_manager.get_bookmark_stats(workspace_id=1)
        self.assertEqual(stats['total'], 1)

    def test_edge_cases(self):
        """Тестирование граничных случаев"""
        # Очень длинные значения
        long_title = "A" * 1000
        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title=long_title
        )
        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.title, long_title)

        # Специальные символы
        special_bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Тест с русскими символами",
            tags=["tag with spaces"]
        )
        self.assertIsNotNone(special_bookmark)


if __name__ == '__main__':
    unittest.main(verbosity=2)