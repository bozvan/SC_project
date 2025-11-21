import sys
import os
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database_manager import DatabaseManager
from src.core.workspace_manager import WorkspaceManager
from src.core.note_manager import NoteManager
from src.core.task_manager import TaskManager
from src.core.bookmark_manager import BookmarkManager
from src.core.tag_manager import TagManager


class TestWorkspaceFunctionality(unittest.TestCase):
    """Тесты функциональности рабочих пространств"""

    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами"""
        # Создаем временную директорию для БД
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.test_dir, 'test_workspace.db')

    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        # Удаляем временную директорию
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Инициализируем менеджеры для каждого теста
        self.db_manager = DatabaseManager(self.db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.workspace_manager = WorkspaceManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        self.task_manager = TaskManager(self.db_manager)
        self.bookmark_manager = BookmarkManager(self.db_manager)

    def tearDown(self):
        """Очистка после каждого теста"""
        # Закрываем соединение с БД
        self.db_manager.close()

    def test_01_get_default_workspace(self):
        """Тест получения workspace по умолчанию"""
        default_workspace = self.workspace_manager.get_default_workspace()

        self.assertIsNotNone(default_workspace, "Не удалось получить workspace по умолчанию")
        self.assertTrue(default_workspace.is_default, "Workspace не помечен как default")
        self.assertEqual(default_workspace.name, "DEFAULT", "Некорректное имя workspace по умолчанию")

    def test_02_create_new_workspace(self):
        """Тест создания нового workspace"""
        new_workspace = self.workspace_manager.create_workspace(
            "Проект X",
            "Рабочее пространство для проекта X"
        )

        self.assertIsNotNone(new_workspace, "Не удалось создать новый workspace")
        self.assertEqual(new_workspace.name, "Проект X", "Некорректное имя workspace")
        self.assertEqual(new_workspace.description, "Рабочее пространство для проекта X",
                         "Некорректное описание workspace")
        self.assertFalse(new_workspace.is_default, "Новый workspace не должен быть default")

    def test_03_get_all_workspaces(self):
        """Тест получения всех workspace"""
        # Создаем дополнительный workspace
        self.workspace_manager.create_workspace("Проект Y", "Тестовое пространство")

        all_workspaces = self.workspace_manager.get_all_workspaces()

        self.assertGreaterEqual(len(all_workspaces), 2, "Должно быть как минимум 2 workspace")

        # Проверяем, что есть workspace по умолчанию
        default_exists = any(ws.is_default for ws in all_workspaces)
        self.assertTrue(default_exists, "Должен существовать workspace по умолчанию")

    def test_04_create_note_in_workspace(self):
        """Тест создания заметки в конкретном workspace"""
        # Создаем workspace для теста
        workspace = self.workspace_manager.create_workspace("Тестовый проект", "Для тестирования заметок")

        note = self.note_manager.create(
            "Заметка в проекте",
            "Содержимое заметки",
            workspace_id=workspace.id
        )

        self.assertIsNotNone(note, "Не удалось создать заметку в workspace")
        self.assertEqual(note.workspace_id, workspace.id, "Заметка создана в неправильном workspace")
        self.assertEqual(note.title, "Заметка в проекте", "Некорректный заголовок заметки")

    def test_05_create_task_in_workspace(self):
        """Тест создания задачи в workspace"""
        # Создаем workspace и заметку для задачи
        workspace = self.workspace_manager.create_workspace("Проект с задачами", "Для тестирования задач")
        note = self.note_manager.create("Заметка для задачи", "Содержимое", workspace_id=workspace.id)

        task = self.task_manager.create_task(
            note_id=note.id,
            description="Задача в проекте",
            workspace_id=workspace.id
        )

        self.assertIsNotNone(task, "Не удалось создать задачу в workspace")
        self.assertEqual(task.workspace_id, workspace.id, "Задача создана в неправильном workspace")
        self.assertEqual(task.description, "Задача в проекте", "Некорректное описание задачи")

    def test_06_workspace_stats(self):
        """Тест статистики workspace"""
        workspace = self.workspace_manager.create_workspace("Статистика проект", "Для тестирования статистики")

        # Создаем заметки и задачи для статистики
        note1 = self.note_manager.create("Заметка 1", "Содержимое 1", workspace_id=workspace.id)
        note2 = self.note_manager.create("Заметка 2", "Содержимое 2", workspace_id=workspace.id)

        self.task_manager.create_task(note_id=note1.id, description="Задача 1", workspace_id=workspace.id)
        self.task_manager.create_task(note_id=note2.id, description="Задача 2", workspace_id=workspace.id,
                                      is_completed=True)

        stats = self.workspace_manager.get_workspace_stats(workspace.id)

        self.assertEqual(stats['notes_count'], 2, "Некорректное количество заметок")
        self.assertEqual(stats['tasks_count'], 2, "Некорректное количество задач")
        self.assertEqual(stats['active_tasks_count'], 1, "Некорректное количество активных задач")
        self.assertEqual(stats['total_items'], 4, "Некорректное общее количество элементов")

    def test_07_get_notes_by_workspace(self):
        """Тест получения заметок по workspace"""
        workspace1 = self.workspace_manager.create_workspace("Проект A", "Первый проект")
        workspace2 = self.workspace_manager.create_workspace("Проект B", "Второй проект")

        # Создаем заметки в разных workspace
        self.note_manager.create("Заметка A1", "Содержимое A1", workspace_id=workspace1.id)
        self.note_manager.create("Заметка A2", "Содержимое A2", workspace_id=workspace1.id)
        self.note_manager.create("Заметка B1", "Содержимое B1", workspace_id=workspace2.id)

        notes_workspace1 = self.note_manager.get_notes_by_workspace(workspace1.id)
        notes_workspace2 = self.note_manager.get_notes_by_workspace(workspace2.id)

        self.assertEqual(len(notes_workspace1), 2, "Некорректное количество заметок в workspace A")
        self.assertEqual(len(notes_workspace2), 1, "Некорректное количество заметок в workspace B")

        # Проверяем, что заметки принадлежат правильным workspace
        for note in notes_workspace1:
            self.assertEqual(note.workspace_id, workspace1.id, "Заметка в неправильном workspace")

        for note in notes_workspace2:
            self.assertEqual(note.workspace_id, workspace2.id, "Заметка в неправильном workspace")

    def test_08_update_workspace(self):
        """Тест обновления workspace"""
        workspace = self.workspace_manager.create_workspace("Исходное имя", "Исходное описание")

        success = self.workspace_manager.update_workspace(
            workspace.id,
            "Обновленное имя",
            "Обновленное описание"
        )

        self.assertTrue(success, "Не удалось обновить workspace")

        # Проверяем обновленные данные
        updated_workspace = self.workspace_manager.get_workspace(workspace.id)
        self.assertEqual(updated_workspace.name, "Обновленное имя", "Имя workspace не обновлено")
        self.assertEqual(updated_workspace.description, "Обновленное описание",
                         "Описание workspace не обновлено")

    def test_09_cannot_delete_default_workspace(self):
        """Тест запрета удаления workspace по умолчанию"""
        default_workspace = self.workspace_manager.get_default_workspace()

        delete_success = self.workspace_manager.delete_workspace(default_workspace.id)

        self.assertFalse(delete_success, "Workspace по умолчанию не должен удаляться")

        # Проверяем, что workspace по умолчанию все еще существует
        still_exists = self.workspace_manager.get_workspace(default_workspace.id)
        self.assertIsNotNone(still_exists, "Workspace по умолчанию был удален")

    def test_10_delete_workspace(self):
        """Тест удаления workspace"""
        workspace = self.workspace_manager.create_workspace("Для удаления", "Будет удален")

        # Создаем связанные данные
        note = self.note_manager.create("Заметка", "Содержимое", workspace_id=workspace.id)
        self.task_manager.create_task(note_id=note.id, description="Задача", workspace_id=workspace.id)

        delete_success = self.workspace_manager.delete_workspace(workspace.id)

        self.assertTrue(delete_success, "Не удалось удалить workspace")

        # Проверяем, что workspace действительно удален
        deleted_workspace = self.workspace_manager.get_workspace(workspace.id)
        self.assertIsNone(deleted_workspace, "Workspace все еще существует после удаления")

    def test_11_workspace_isolation(self):
        """Тест изоляции данных между workspace"""
        workspace1 = self.workspace_manager.create_workspace("Изоляция 1", "Первый")
        workspace2 = self.workspace_manager.create_workspace("Изоляция 2", "Второй")

        # Создаем одинаковые заметки в разных workspace
        note1 = self.note_manager.create("Одинаковая заметка", "Содержимое", workspace_id=workspace1.id)
        note2 = self.note_manager.create("Одинаковая заметка", "Содержимое", workspace_id=workspace2.id)

        # Получаем заметки для каждого workspace
        notes1 = self.note_manager.get_notes_by_workspace(workspace1.id)
        notes2 = self.note_manager.get_notes_by_workspace(workspace2.id)

        # Проверяем изоляцию
        self.assertEqual(len(notes1), 1, "В workspace1 должна быть одна заметка")
        self.assertEqual(len(notes2), 1, "В workspace2 должна быть одна заметка")

        # Заметки должны быть разными объектами
        self.assertNotEqual(note1.id, note2.id, "Заметки в разных workspace должны иметь разные ID")

    def test_12_bookmark_in_workspace(self):
        """Тест создания закладки в workspace"""
        workspace = self.workspace_manager.create_workspace("Закладки проект", "Для тестирования закладок")

        bookmark = self.bookmark_manager.create(
            url="https://example.com",
            title="Пример сайта",
            description="Тестовая закладка",
            workspace_id=workspace.id
        )

        self.assertIsNotNone(bookmark, "Не удалось создать закладку в workspace")
        self.assertEqual(bookmark.workspace_id, workspace.id, "Закладка создана в неправильном workspace")

        # Получаем закладки по workspace
        bookmarks = self.bookmark_manager.get_bookmarks_by_workspace(workspace.id)
        self.assertEqual(len(bookmarks), 1, "Должна быть одна закладка в workspace")
        self.assertEqual(bookmarks[0].id, bookmark.id, "Некорректная закладка получена")

    def test_13_invalid_workspace_operations(self):
        """Тест операций с несуществующим workspace"""
        # Попытка получить несуществующий workspace
        non_existent = self.workspace_manager.get_workspace(99999)
        self.assertIsNone(non_existent, "Несуществующий workspace не должен возвращаться")

        # Попытка обновить несуществующий workspace
        update_success = self.workspace_manager.update_workspace(99999, "Новое имя", "Новое описание")
        self.assertFalse(update_success, "Нельзя обновить несуществующий workspace")

        # Попытка удалить несуществующий workspace
        delete_success = self.workspace_manager.delete_workspace(99999)
        self.assertFalse(delete_success, "Нельзя удалить несуществующий workspace")

    def test_14_workspace_name_uniqueness(self):
        """Тест уникальности имен workspace - ИСПРАВЛЕННЫЙ ТЕСТ"""
        # В текущей реализации имена workspace должны быть уникальными
        workspace1 = self.workspace_manager.create_workspace("Уникальное имя", "Описание")

        # Попытка создать workspace с тем же именем должна завершиться ошибкой
        workspace2 = self.workspace_manager.create_workspace("Уникальное имя", "Другое описание")

        # Второй workspace не должен создаться из-за ограничения UNIQUE
        self.assertIsNone(workspace2, "Нельзя создать workspace с неуникальным именем")

    def test_15_workspace_with_different_names(self):
        """Тест создания workspace с разными именами"""
        # Создаем workspace с разными именами - должны успешно создаться
        workspace1 = self.workspace_manager.create_workspace("Проект Alpha", "Первый проект")
        workspace2 = self.workspace_manager.create_workspace("Проект Beta", "Второй проект")

        self.assertIsNotNone(workspace1, "Должен создать workspace с уникальным именем")
        self.assertIsNotNone(workspace2, "Должен создать workspace с другим уникальным именем")
        self.assertNotEqual(workspace1.name, workspace2.name, "Имена workspace должны быть разными")


class TestWorkspaceEdgeCases(unittest.TestCase):
    """Тесты граничных случаев для рабочих пространств"""

    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами"""
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.test_dir, 'test_workspace_edge.db')

    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db_manager = DatabaseManager(self.db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.workspace_manager = WorkspaceManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.db_manager.close()

    def test_empty_workspace_name(self):
        """Тест создания workspace с пустым именем"""
        workspace = self.workspace_manager.create_workspace("", "Описание")
        self.assertIsNone(workspace, "Нельзя создать workspace с пустым именем")

    def test_none_workspace_name(self):
        """Тест создания workspace с None именем"""
        workspace = self.workspace_manager.create_workspace(None, "Описание")
        self.assertIsNone(workspace, "Нельзя создать workspace с None именем")

    def test_very_long_workspace_name(self):
        """Тест создания workspace с очень длинным именем"""
        long_name = "A" * 100  # Разумная длина для теста
        workspace = self.workspace_manager.create_workspace(long_name, "Описание")
        self.assertIsNotNone(workspace, "Должна быть возможность создать workspace с длинным именем")

    def test_note_with_invalid_workspace(self):
        """Тест создания заметки с несуществующим workspace - ИСПРАВЛЕННЫЙ ТЕСТ"""
        # В текущей реализации есть FOREIGN KEY constraint, поэтому нельзя создать заметку
        # с несуществующим workspace_id
        note = self.note_manager.create("Заметка", "Содержимое", workspace_id=99999)

        # Заметка не должна создаться из-за ограничения внешнего ключа
        self.assertIsNone(note, "Нельзя создать заметку с несуществующим workspace")

    def test_note_with_default_workspace(self):
        """Тест создания заметки с workspace по умолчанию"""
        default_workspace = self.workspace_manager.get_default_workspace()

        note = self.note_manager.create("Заметка", "Содержимое", workspace_id=default_workspace.id)

        self.assertIsNotNone(note, "Должна быть возможность создать заметку с существующим workspace")
        self.assertEqual(note.workspace_id, default_workspace.id, "Заметка создана в неправильном workspace")

    def test_workspace_special_characters(self):
        """Тест создания workspace со специальными символами"""
        special_name = "Проект с 🚀 эмодзи & спецсимволами"
        workspace = self.workspace_manager.create_workspace(special_name, "Описание со спецсимволами")

        self.assertIsNotNone(workspace, "Должна быть возможность создать workspace со спецсимволами")
        self.assertEqual(workspace.name, special_name, "Имя workspace с спецсимволами не сохранено корректно")

    def test_workspace_whitespace_handling(self):
        """Тест обработки пробелов в именах workspace"""
        # Пробелы в начале и конце должны обрезаться
        workspace = self.workspace_manager.create_workspace("  Проект с пробелами  ", "Описание")

        self.assertIsNotNone(workspace, "Должна быть возможность создать workspace с пробелами")
        self.assertEqual(workspace.name, "Проект с пробелами", "Пробелы не обрезаны корректно")


class TestWorkspaceIntegration(unittest.TestCase):
    """Интеграционные тесты рабочих пространств"""

    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами"""
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.test_dir, 'test_workspace_integration.db')

    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db_manager = DatabaseManager(self.db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.workspace_manager = WorkspaceManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        self.task_manager = TaskManager(self.db_manager)
        self.bookmark_manager = BookmarkManager(self.db_manager)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.db_manager.close()

    def test_complete_workspace_lifecycle(self):
        """Тест полного жизненного цикла workspace"""
        # 1. Создание workspace
        workspace = self.workspace_manager.create_workspace("Полный цикл", "Тест жизненного цикла")
        self.assertIsNotNone(workspace, "Не удалось создать workspace")

        # 2. Создание данных в workspace
        note = self.note_manager.create("Тестовая заметка", "Содержимое", workspace_id=workspace.id)
        self.assertIsNotNone(note, "Не удалось создать заметку")

        task = self.task_manager.create_task(
            note_id=note.id,
            description="Тестовая задача",
            workspace_id=workspace.id
        )
        self.assertIsNotNone(task, "Не удалось создать задачу")

        bookmark = self.bookmark_manager.create(
            url="https://test.com",
            title="Тестовая закладка",
            workspace_id=workspace.id
        )
        self.assertIsNotNone(bookmark, "Не удалось создать закладку")

        # 3. Проверка статистики
        stats = self.workspace_manager.get_workspace_stats(workspace.id)
        self.assertEqual(stats['notes_count'], 1, "Некорректное количество заметок")
        self.assertEqual(stats['tasks_count'], 1, "Некорректное количество задач")
        self.assertEqual(stats['bookmarks_count'], 1, "Некорректное количество закладок")

        # 4. Обновление workspace
        update_success = self.workspace_manager.update_workspace(
            workspace.id,
            "Обновленный цикл",
            "Обновленное описание"
        )
        self.assertTrue(update_success, "Не удалось обновить workspace")

        # 5. Удаление workspace
        delete_success = self.workspace_manager.delete_workspace(workspace.id)
        self.assertTrue(delete_success, "Не удалось удалить workspace")

        # 6. Проверка что workspace удален
        deleted_workspace = self.workspace_manager.get_workspace(workspace.id)
        self.assertIsNone(deleted_workspace, "Workspace не удален")


if __name__ == "__main__":
    # Создаем test suite
    suite = unittest.TestSuite()

    # Добавляем тесты в определенном порядке
    test_classes = [
        TestWorkspaceFunctionality,
        TestWorkspaceEdgeCases,
        TestWorkspaceIntegration
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Возвращаем код выхода
    sys.exit(0 if result.wasSuccessful() else 1)
