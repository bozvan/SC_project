import unittest
import os
import sys
import tempfile
from datetime import datetime, timedelta

# Добавляем путь к корню проекта для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.database_manager import DatabaseManager
from core.task_manager import TaskManager
from core.note_manager import NoteManager
from core.tag_manager import TagManager


class TestTaskManagerWithPriority(unittest.TestCase):
    """Тесты для менеджера задач с приоритетами и сроками"""

    def setUp(self):
        """Создание временной БД для тестов"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.db_manager = DatabaseManager(self.db_path)

        # Создаем менеджеры
        self.tag_manager = TagManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        self.task_manager = TaskManager(self.db_manager)

        # Создаем тестовую заметку
        self.test_note = self.note_manager.create("Тестовая заметка", "Содержимое")
        self.note_id = self.test_note.id

    def tearDown(self):
        """Очистка после тестов"""
        # Закрываем все соединения с БД
        if hasattr(self, 'db_manager'):
            self.db_manager.close()

        # Закрываем временный файл
        if hasattr(self, 'temp_db'):
            self.temp_db.close()

        # Удаляем файл БД
        if hasattr(self, 'db_path') and os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except PermissionError:
                print(f"⚠️  Не удалось удалить файл {self.db_path}, возможно он все еще занят")

    def test_create_task_with_priority(self):
        """Тест создания задачи с приоритетом"""
        # Создаем задачи с разными приоритетами
        task_high = self.task_manager.create_task(
            self.note_id, "Важная задача", priority="high"
        )
        task_medium = self.task_manager.create_task(
            self.note_id, "Обычная задача", priority="medium"
        )
        task_low = self.task_manager.create_task(
            self.note_id, "Несрочная задача", priority="low"
        )

        self.assertIsNotNone(task_high)
        self.assertIsNotNone(task_medium)
        self.assertIsNotNone(task_low)

        self.assertEqual(task_high.priority, "high")
        self.assertEqual(task_medium.priority, "medium")
        self.assertEqual(task_low.priority, "low")

    def test_create_task_with_invalid_priority(self):
        """Тест создания задачи с неверным приоритетом"""
        task = self.task_manager.create_task(
            self.note_id, "Задача с неверным приоритетом", priority="invalid"
        )

        self.assertIsNotNone(task)
        # Должен установиться приоритет по умолчанию 'medium'
        self.assertEqual(task.priority, "medium")

    def test_create_task_with_due_date(self):
        """Тест создания задачи со сроком выполнения"""
        due_date = datetime.now() + timedelta(days=7)
        task = self.task_manager.create_task(
            self.note_id, "Задача со сроком", due_date=due_date
        )

        self.assertIsNotNone(task)
        self.assertIsNotNone(task.due_date)
        self.assertEqual(task.due_date.date(), due_date.date())

    def test_update_task_priority(self):
        """Тест обновления приоритета задачи"""
        task = self.task_manager.create_task(self.note_id, "Тестовая задача")

        # Обновляем приоритет
        success = self.task_manager.update_task(task.id, priority="high")
        self.assertTrue(success)

        # Проверяем обновление
        updated_task = self.task_manager.get_task(task.id)
        self.assertEqual(updated_task.priority, "high")

    def test_update_task_due_date(self):
        """Тест обновления срока выполнения"""
        task = self.task_manager.create_task(self.note_id, "Тестовая задача")
        new_due_date = datetime.now() + timedelta(days=5)

        # Обновляем срок
        success = self.task_manager.update_task(task.id, due_date=new_due_date)
        self.assertTrue(success)

        # Проверяем обновление
        updated_task = self.task_manager.get_task(task.id)
        self.assertIsNotNone(updated_task.due_date)
        self.assertEqual(updated_task.due_date.date(), new_due_date.date())

    def test_get_tasks_by_priority(self):
        """Тест получения задач по приоритету"""
        # Создаем задачи с разными приоритетами
        self.task_manager.create_task(self.note_id, "High 1", priority="high")
        self.task_manager.create_task(self.note_id, "High 2", priority="high")
        self.task_manager.create_task(self.note_id, "Medium 1", priority="medium")
        self.task_manager.create_task(self.note_id, "Low 1", priority="low")

        # Получаем задачи по приоритету
        high_tasks = self.task_manager.get_tasks_by_priority("high")
        medium_tasks = self.task_manager.get_tasks_by_priority("medium")
        low_tasks = self.task_manager.get_tasks_by_priority("low")

        self.assertEqual(len(high_tasks), 2)
        self.assertEqual(len(medium_tasks), 1)
        self.assertEqual(len(low_tasks), 1)

        # Проверяем приоритеты
        for task in high_tasks:
            self.assertEqual(task.priority, "high")
        for task in medium_tasks:
            self.assertEqual(task.priority, "medium")
        for task in low_tasks:
            self.assertEqual(task.priority, "low")

    def test_get_urgent_tasks(self):
        """Тест получения срочных задач"""
        # Создаем срочную задачу (высокий приоритет + срок в ближайшие 3 дня)
        urgent_due_date = datetime.now() + timedelta(days=2)
        self.task_manager.create_task(
            self.note_id, "Срочная задача",
            priority="high",
            due_date=urgent_due_date
        )

        # Создаем несрочную задачу (низкий приоритет)
        self.task_manager.create_task(
            self.note_id, "Несрочная задача",
            priority="low"
        )

        urgent_tasks = self.task_manager.get_urgent_tasks()

        self.assertEqual(len(urgent_tasks), 1)
        self.assertEqual(urgent_tasks[0].description, "Срочная задача")
        self.assertEqual(urgent_tasks[0].priority, "high")

    def test_get_tasks_with_due_dates(self):
        """Тест получения задач со сроками"""
        # Создаем задачи со сроками и без
        self.task_manager.create_task(
            self.note_id, "Задача со сроком",
            due_date=datetime.now() + timedelta(days=3)
        )
        self.task_manager.create_task(
            self.note_id, "Задача без срока"
        )
        self.task_manager.create_task(
            self.note_id, "Еще задача со сроком",
            due_date=datetime.now() + timedelta(days=1)
        )

        tasks_with_due_dates = self.task_manager.get_tasks_with_due_dates()

        self.assertEqual(len(tasks_with_due_dates), 2)

        # Проверяем сортировку по сроку
        self.assertEqual(tasks_with_due_dates[0].description, "Еще задача со сроком")
        self.assertEqual(tasks_with_due_dates[1].description, "Задача со сроком")

    def test_task_ordering_by_priority(self):
        """Тест сортировки задач по приоритету"""
        # Создаем задачи в разном порядке приоритетов
        self.task_manager.create_task(self.note_id, "Low", priority="low")
        self.task_manager.create_task(self.note_id, "High", priority="high")
        self.task_manager.create_task(self.note_id, "Medium", priority="medium")

        tasks = self.task_manager.get_tasks_for_note(self.note_id)

        # Проверяем порядок: high -> medium -> low
        self.assertEqual(tasks[0].priority, "high")
        self.assertEqual(tasks[1].priority, "medium")
        self.assertEqual(tasks[2].priority, "low")

    def test_complex_task_creation(self):
        """Тест создания задачи со всеми параметрами"""
        due_date = datetime.now() + timedelta(days=10)
        task = self.task_manager.create_task(
            note_id=self.note_id,
            description="Комплексная задача",
            due_date=due_date,
            priority="high",
            is_completed=False
        )

        self.assertIsNotNone(task)
        self.assertEqual(task.description, "Комплексная задача")
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.due_date.date(), due_date.date())
        self.assertFalse(task.is_completed)
        self.assertEqual(task.note_id, self.note_id)

    def test_invalid_priority_in_update(self):
        """Тест обновления с неверным приоритетом"""
        task = self.task_manager.create_task(self.note_id, "Тестовая задача")

        # Пытаемся установить неверный приоритет
        success = self.task_manager.update_task(task.id, priority="invalid_priority")

        # Должен вернуть True, но приоритет не изменится
        self.assertTrue(success)

        # Проверяем что приоритет не изменился
        updated_task = self.task_manager.get_task(task.id)
        self.assertEqual(updated_task.priority, "medium")  # остался по умолчанию


if __name__ == '__main__':
    unittest.main()
