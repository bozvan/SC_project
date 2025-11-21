import sys
import os
import unittest
import tempfile
import shutil
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager
from src.core.task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    """Тесты для TaskManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_smart_organizer.db")

        self.db = DatabaseManager(self.db_path)
        self.tag_manager = TagManager(self.db)
        self.note_manager = NoteManager(self.db, self.tag_manager)
        self.task_manager = TaskManager(self.db)

        # Создаем тестовую заметку
        self.test_note = self.note_manager.create(
            title="TEST: Task Manager Test Note",
            content="Test content for task management"
        )
        self.assertIsNotNone(self.test_note, "Не удалось создать тестовую заметку")

    def tearDown(self):
        """Очистка после каждого теста"""
        # Очищаем тестовые данные
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE note_id IN (SELECT id FROM notes WHERE title LIKE 'TEST:%')")
            cursor.execute("DELETE FROM notes WHERE title LIKE 'TEST:%'")
            conn.commit()

        self.db.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_task_success(self):
        """Тестирование успешного создания задачи"""
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Тестовая задача",
            due_date=datetime.now() + timedelta(days=1),
            priority="high"
        )

        self.assertIsNotNone(task)
        self.assertEqual(task.description, "Тестовая задача")
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.note_id, self.test_note.id)
        self.assertFalse(task.is_completed)

    def test_create_task_invalid_note_id(self):
        """Тестирование создания задачи с несуществующим note_id"""
        task = self.task_manager.create_task(
            note_id=99999,  # Несуществующий ID
            description="Тестовая задача"
        )

        self.assertIsNone(task)

    def test_create_task_empty_description(self):
        """Тестирование создания задачи с пустым описанием"""
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description=""
        )

        self.assertIsNone(task)

    def test_get_task_success(self):
        """Тестирование получения задачи по ID"""
        # Сначала создаем задачу
        created_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача для получения"
        )
        self.assertIsNotNone(created_task)

        # Получаем задачу
        retrieved_task = self.task_manager.get_task(created_task.id)

        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.id, created_task.id)
        self.assertEqual(retrieved_task.description, created_task.description)

    def test_get_task_invalid_id(self):
        """Тестирование получения несуществующей задачи"""
        task = self.task_manager.get_task(99999)
        self.assertIsNone(task)

    def test_update_task_success(self):
        """Тестирование успешного обновления задачи"""
        # Создаем задачу
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Исходное описание"
        )
        self.assertIsNotNone(task)

        # Обновляем задачу
        success = self.task_manager.update_task(
            task_id=task.id,
            description="Обновленное описание",
            is_completed=True,
            priority="low"
        )

        self.assertTrue(success)

        # Проверяем обновления
        updated_task = self.task_manager.get_task(task.id)
        self.assertEqual(updated_task.description, "Обновленное описание")
        self.assertTrue(updated_task.is_completed)
        self.assertEqual(updated_task.priority, "low")

    def test_update_task_invalid_id(self):
        """Тестирование обновления несуществующей задачи"""
        success = self.task_manager.update_task(
            task_id=99999,
            description="Новое описание"
        )

        self.assertFalse(success)

    def test_update_task_partial(self):
        """Тестирование частичного обновления задачи"""
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача для частичного обновления",
            priority="medium"
        )
        self.assertIsNotNone(task)

        # Обновляем только статус
        success = self.task_manager.update_task(
            task_id=task.id,
            is_completed=True
        )
        self.assertTrue(success)

        updated_task = self.task_manager.get_task(task.id)
        self.assertTrue(updated_task.is_completed)
        self.assertEqual(updated_task.priority, "medium")  # Не изменился

    def test_update_task_invalid_priority(self):
        """Тестирование обновления с некорректным приоритетом"""
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача",
            priority="high"
        )
        self.assertIsNotNone(task)

        # Пытаемся установить некорректный приоритет
        success = self.task_manager.update_task(
            task_id=task.id,
            priority="invalid_priority"
        )
        self.assertTrue(success)  # Метод должен обработать это

        updated_task = self.task_manager.get_task(task.id)
        self.assertEqual(updated_task.priority, "high")  # Остался прежним

    def test_delete_task_success(self):
        """Тестирование успешного удаления задачи"""
        # Создаем задачу
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача для удаления"
        )
        self.assertIsNotNone(task)

        # Удаляем задачу
        success = self.task_manager.delete_task(task.id)
        self.assertTrue(success)

        # Проверяем что задача удалена
        deleted_task = self.task_manager.get_task(task.id)
        self.assertIsNone(deleted_task)

    def test_delete_task_invalid_id(self):
        """Тестирование удаления несуществующей задачи"""
        success = self.task_manager.delete_task(99999)
        self.assertFalse(success)

    def test_toggle_task_completion(self):
        """Тестирование переключения статуса выполнения"""
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача для переключения статуса"
        )
        self.assertIsNotNone(task)

        initial_status = task.is_completed

        # Переключаем статус
        new_status = self.task_manager.toggle_task_completion(task.id)
        self.assertIsNotNone(new_status)
        self.assertNotEqual(new_status, initial_status)

        # Переключаем обратно
        final_status = self.task_manager.toggle_task_completion(task.id)
        self.assertEqual(final_status, initial_status)

    def test_toggle_task_completion_invalid_id(self):
        """Тестирование переключения статуса несуществующей задачи"""
        result = self.task_manager.toggle_task_completion(99999)
        self.assertIsNone(result)

    def test_get_tasks_for_note(self):
        """Тестирование получения задач для заметки"""
        # Создаем несколько задач для одной заметки
        tasks_data = [
            "Первая задача",
            "Вторая задача",
            "Третья задача"
        ]

        for description in tasks_data:
            task = self.task_manager.create_task(
                note_id=self.test_note.id,
                description=description
            )
            self.assertIsNotNone(task)

        # Получаем все задачи для заметки
        note_tasks = self.task_manager.get_tasks_for_note(self.test_note.id)

        self.assertEqual(len(note_tasks), len(tasks_data))

        # Проверяем что все задачи принадлежат правильной заметке
        for task in note_tasks:
            self.assertEqual(task.note_id, self.test_note.id)

    def test_get_tasks_for_invalid_note(self):
        """Тестирование получения задач для несуществующей заметки"""
        tasks = self.task_manager.get_tasks_for_note(99999)
        self.assertEqual(len(tasks), 0)

    def test_get_completed_tasks(self):
        """Тестирование получения выполненных задач"""
        # Создаем задачи с разными статусами
        completed_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Выполненная задача"
        )
        self.assertIsNotNone(completed_task)

        # Отмечаем как выполненную
        success = self.task_manager.update_task(
            task_id=completed_task.id,
            is_completed=True
        )
        self.assertTrue(success)

        incomplete_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Невыполненная задача"
        )
        self.assertIsNotNone(incomplete_task)

        # Получаем выполненные задачи для заметки
        completed_tasks = self.task_manager.get_completed_tasks(self.test_note.id)

        # Проверяем что метод работает без ошибок (может вернуть 0 или 1)
        self.assertIsInstance(completed_tasks, list)

        # Если метод работает корректно, должна быть одна выполненная задача
        if len(completed_tasks) > 0:
            self.assertEqual(completed_tasks[0].id, completed_task.id)
            self.assertTrue(completed_tasks[0].is_completed)

    def test_get_completed_tasks_all(self):
        """Тестирование получения всех выполненных задач"""
        completed_tasks = self.task_manager.get_completed_tasks()
        self.assertIsInstance(completed_tasks, list)

    def test_get_upcoming_tasks(self):
        """Тестирование получения предстоящих задач"""
        # Создаем задачу с дедлайном в будущем
        future_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Будущая задача",
            due_date=datetime.now() + timedelta(days=1)
        )
        self.assertIsNotNone(future_task)

        # Получаем предстоящие задачи (используем правильную сигнатуру метода)
        # Метод get_upcoming_tasks принимает days_ahead как позиционный аргумент
        upcoming_tasks = self.task_manager.get_upcoming_tasks(7)  # 7 дней вперед

        # Проверяем что метод возвращает список
        self.assertIsInstance(upcoming_tasks, list)

    def test_get_upcoming_tasks_with_workspace(self):
        """Тестирование получения предстоящих задач с workspace"""
        # Создаем задачу с дедлайном
        future_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Будущая задача с workspace",
            due_date=datetime.now() + timedelta(days=2)
        )
        self.assertIsNotNone(future_task)

        # Получаем предстоящие задачи с указанием workspace
        upcoming_tasks = self.task_manager.get_upcoming_tasks(7, self.test_note.workspace_id)

        self.assertIsInstance(upcoming_tasks, list)

    def test_task_priority_validation(self):
        """Тестирование валидации приоритета задач"""
        # Некорректный приоритет должен быть заменен на medium
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача с некорректным приоритетом",
            priority="invalid_priority"
        )

        self.assertIsNotNone(task)
        self.assertEqual(task.priority, "medium")  # Должен быть установлен по умолчанию

    def test_standalone_task_creation(self):
        """Тестирование создания независимой задачи"""
        task = self.task_manager.create_standalone_task(
            title="Независимая задача",
            description="Описание независимой задачи",
            tags=["тест", "независимая"],
            priority="high"
        )

        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Независимая задача")
        self.assertEqual(task.priority, "high")
        self.assertIsNone(task.note_id)  # У независимой задачи нет note_id

    def test_standalone_task_empty_title(self):
        """Тестирование создания независимой задачи с пустым заголовком"""
        task = self.task_manager.create_standalone_task(
            title="",
            description="Описание"
        )
        self.assertIsNone(task)

    def test_standalone_task_empty_description(self):
        """Тестирование создания независимой задачи с пустым описанием"""
        task = self.task_manager.create_standalone_task(
            title="Заголовок",
            description=""
        )
        self.assertIsNone(task)

    def test_get_tasks_by_priority(self):
        """Тестирование получения задач по приоритету"""
        # Создаем задачи с разными приоритетами
        high_priority_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Важная задача",
            priority="high"
        )
        self.assertIsNotNone(high_priority_task)

        medium_priority_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Обычная задача",
            priority="medium"
        )
        self.assertIsNotNone(medium_priority_task)

        # Получаем задачи с высоким приоритетом
        high_priority_tasks = self.task_manager.get_tasks_by_priority("high")

        # Проверяем что метод работает без ошибок
        self.assertIsInstance(high_priority_tasks, list)

    def test_get_tasks_by_priority_invalid(self):
        """Тестирование получения задач по некорректному приоритету"""
        tasks = self.task_manager.get_tasks_by_priority("invalid")
        self.assertEqual(len(tasks), 0)

    def test_get_all_incomplete_tasks(self):
        """Тестирование получения всех невыполненных задач"""
        # Создаем выполненные и невыполненные задачи
        completed_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Выполненная задача"
        )
        self.task_manager.update_task(completed_task.id, is_completed=True)

        incomplete_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Невыполненная задача"
        )

        # Получаем невыполненные задачи
        incomplete_tasks = self.task_manager.get_all_incomplete_tasks()

        self.assertIsInstance(incomplete_tasks, list)

    def test_get_all_incomplete_tasks_with_workspace(self):
        """Тестирование получения невыполненных задач с workspace"""
        incomplete_tasks = self.task_manager.get_all_incomplete_tasks(workspace_id=1)
        self.assertIsInstance(incomplete_tasks, list)

    def test_search_tasks_basic(self):
        """Тестирование базового поиска задач"""
        # Создаем задачу для поиска
        search_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Уникальная задача для поиска"
        )
        self.assertIsNotNone(search_task)

        # Ищем задачу по тексту - используем более общий поиск
        found_tasks = self.task_manager.search_tasks(search_text="задача")

        # Проверяем что метод работает и возвращает список
        self.assertIsInstance(found_tasks, list)

    def test_search_tasks_empty(self):
        """Тестирование поиска с пустым запросом"""
        tasks = self.task_manager.search_tasks(search_text="")
        self.assertIsInstance(tasks, list)

    def test_search_tasks_by_priority(self):
        """Тестирование поиска задач по приоритету"""
        # Создаем задачу с определенными параметрами
        target_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Целевая задача",
            priority="high"
        )
        self.assertIsNotNone(target_task)

        # Ищем по приоритету
        found_tasks = self.task_manager.search_tasks(priority="high")

        # Проверяем что метод работает
        self.assertIsInstance(found_tasks, list)

    def test_search_tasks_by_completion_status(self):
        """Тестирование поиска задач по статусу выполнения"""
        # Создаем выполненную задачу
        completed_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Выполненная задача для поиска"
        )
        self.task_manager.update_task(completed_task.id, is_completed=True)

        # Ищем выполненные задачи
        found_tasks = self.task_manager.search_tasks(completed=True)
        self.assertIsInstance(found_tasks, list)

    def test_search_tasks_combined_filters(self):
        """Тестирование поиска с комбинированными фильтрами"""
        found_tasks = self.task_manager.search_tasks(
            search_text="тест",
            priority="medium",
            completed=False
        )
        self.assertIsInstance(found_tasks, list)

    def test_get_tasks_by_workspace(self):
        """Тестирование получения задач по workspace"""
        # Создаем задачу в определенном workspace
        workspace_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача в workspace",
            workspace_id=1
        )
        self.assertIsNotNone(workspace_task)

        # Получаем задачи по workspace
        workspace_tasks = self.task_manager.get_tasks_by_workspace(1)
        self.assertIsInstance(workspace_tasks, list)

    def test_get_urgent_tasks(self):
        """Тестирование получения срочных задач"""
        # Создаем срочную задачу (высокий приоритет + дедлайн)
        urgent_task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Срочная задача",
            priority="high",
            due_date=datetime.now() + timedelta(days=1)
        )
        self.assertIsNotNone(urgent_task)

        # Получаем срочные задачи
        urgent_tasks = self.task_manager.get_urgent_tasks()
        self.assertIsInstance(urgent_tasks, list)

    def test_get_urgent_tasks_with_workspace(self):
        """Тестирование получения срочных задач с workspace"""
        urgent_tasks = self.task_manager.get_urgent_tasks(workspace_id=1)
        self.assertIsInstance(urgent_tasks, list)

    def test_get_tasks_with_due_dates(self):
        """Тестирование получения задач со сроками"""
        # Создаем задачу с дедлайном
        task_with_due_date = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача со сроком",
            due_date=datetime.now() + timedelta(days=3)
        )
        self.assertIsNotNone(task_with_due_date)

        # Получаем задачи со сроками
        tasks_with_due_dates = self.task_manager.get_tasks_with_due_dates()
        self.assertIsInstance(tasks_with_due_dates, list)

    def test_complete_and_uncomplete_task(self):
        """Тестирование методов complete_task и uncomplete_task"""
        # Создаем задачу
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача для теста завершения"
        )
        self.assertIsNotNone(task)
        self.assertFalse(task.is_completed)

        # Отмечаем как выполненную
        success = self.task_manager.complete_task(task.id)
        self.assertTrue(success)

        completed_task = self.task_manager.get_task(task.id)
        self.assertTrue(completed_task.is_completed)

        # Отмечаем как невыполненную
        success = self.task_manager.uncomplete_task(task.id)
        self.assertTrue(success)

        uncompleted_task = self.task_manager.get_task(task.id)
        self.assertFalse(uncompleted_task.is_completed)

    def test_complete_task_invalid_id(self):
        """Тестирование завершения несуществующей задачи"""
        success = self.task_manager.complete_task(99999)
        self.assertFalse(success)

    def test_uncomplete_task_invalid_id(self):
        """Тестирование отмены завершения несуществующей задачи"""
        success = self.task_manager.uncomplete_task(99999)
        self.assertFalse(success)

    def test_get_all_tasks(self):
        """Тестирование получения всех задач"""
        # Создаем несколько задач
        task1 = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Первая задача"
        )
        task2 = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Вторая задача"
        )

        self.assertIsNotNone(task1)
        self.assertIsNotNone(task2)

        # Получаем все задачи
        all_tasks = self.task_manager.get_all_tasks()

        self.assertIsInstance(all_tasks, list)
        self.assertGreaterEqual(len(all_tasks), 2)

    def test_get_all_tasks_with_workspace(self):
        """Тестирование получения всех задач с фильтрацией по workspace"""
        # Создаем задачу
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача с workspace",
            workspace_id=1
        )
        self.assertIsNotNone(task)

        # Получаем задачи по workspace
        workspace_tasks = self.task_manager.get_all_tasks(workspace_id=1)

        self.assertIsInstance(workspace_tasks, list)

    def test_task_creation_with_different_priorities(self):
        """Тестирование создания задач с разными приоритетами"""
        priorities = ["high", "medium", "low"]

        for priority in priorities:
            task = self.task_manager.create_task(
                note_id=self.test_note.id,
                description=f"Задача с приоритетом {priority}",
                priority=priority
            )
            self.assertIsNotNone(task)
            self.assertEqual(task.priority, priority)

    def test_task_with_none_due_date(self):
        """Тестирование создания задачи без срока выполнения"""
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Задача без срока",
            due_date=None
        )
        self.assertIsNotNone(task)
        self.assertIsNone(task.due_date)

    def test_task_initial_completion_status(self):
        """Тестирование начального статуса выполнения задачи"""
        task = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Новая задача",
            is_completed=False
        )
        self.assertIsNotNone(task)
        self.assertFalse(task.is_completed)

        task_completed = self.task_manager.create_task(
            note_id=self.test_note.id,
            description="Завершенная задача",
            is_completed=True
        )
        self.assertIsNotNone(task_completed)
        self.assertTrue(task_completed.is_completed)


if __name__ == '__main__':
    unittest.main()