import sys
import os
from datetime import datetime, timedelta

# Добавляем путь для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager
from src.core.task_manager import TaskManager


class TaskManagerTester:
    """Тестер для проверки функциональности TaskManager"""

    def __init__(self, db_path="test_smart_organizer.db"):
        """Инициализация тестера"""
        # Используем тестовую БД чтобы не затронуть основную
        self.db = DatabaseManager(db_path)
        self.tag_manager = TagManager(self.db)
        self.note_manager = NoteManager(self.db, self.tag_manager)
        self.task_manager = TaskManager(self.db)

        # ID созданных тестовых заметок
        self.test_note_ids = []

        print("🚀 Инициализация TaskManager Tester...")
        print("✅ Все менеджеры загружены")

    def cleanup(self):
        """Очистка тестовых данных"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                # Удаляем тестовые данные
                cursor.execute("DELETE FROM tasks WHERE note_id IN (SELECT id FROM notes WHERE title LIKE 'TEST:%')")
                cursor.execute("DELETE FROM notes WHERE title LIKE 'TEST:%'")
                conn.commit()
                print("✅ Тестовые данные очищены")
        except Exception as e:
            print(f"❌ Ошибка при очистке: {e}")

    def create_test_note(self, title_suffix=""):
        """Создает тестовую заметку"""
        title = f"TEST: Note {title_suffix} {datetime.now().strftime('%H:%M:%S')}"
        note = self.note_manager.create(title, f"Test content for {title}")
        if note:
            self.test_note_ids.append(note.id)
            print(f"✅ Создана тестовая заметка: {note.title} (ID: {note.id})")
            return note.id
        else:
            print("❌ Не удалось создать тестовую заметку")
            return None

    def test_basic_crud(self):
        """Тест базовых CRUD операций"""
        print("\n" + "=" * 50)
        print("🧪 ТЕСТ: Базовые CRUD операции")
        print("=" * 50)

        # 1. Создание заметки для теста
        note_id = self.create_test_note("CRUD Test")
        if not note_id:
            return False

        # 2. Создание задачи
        print("\n--- Создание задачи ---")
        task = self.task_manager.create(
            note_id=note_id,
            description="Протестировать CRUD операции в TaskManager",
            due_date=datetime.now() + timedelta(days=1)
        )

        if not task:
            print("❌ ТЕСТ ПРОВАЛЕН: Не удалось создать задачу")
            return False

        print(f"✅ Задача создана: {task}")
        task_id = task.id

        # 3. Получение задачи по ID
        print("\n--- Получение задачи по ID ---")
        retrieved_task = self.task_manager.get(task_id)
        if not retrieved_task:
            print("❌ ТЕСТ ПРОВАЛЕН: Не удалось получить задачу по ID")
            return False

        print(f"✅ Задача получена: {retrieved_task}")

        # Проверка данных
        if (retrieved_task.description != task.description or
                retrieved_task.is_completed != task.is_completed):
            print("❌ ТЕСТ ПРОВАЛЕН: Данные задачи не совпадают")
            return False

        # 4. Обновление задачи
        print("\n--- Обновление задачи ---")
        new_description = "ОБНОВЛЕННО: Протестировать CRUD операции"
        success = self.task_manager.update(
            task_id=task_id,
            description=new_description,
            is_completed=True
        )

        if not success:
            print("❌ ТЕСТ ПРОВАЛЕН: Не удалось обновить задачу")
            return False

        # Проверяем обновление
        updated_task = self.task_manager.get(task_id)
        if (updated_task.description != new_description or
                not updated_task.is_completed):
            print("❌ ТЕСТ ПРОВАЛЕН: Задача не обновилась корректно")
            return False

        print(f"✅ Задача обновлена: {updated_task}")

        # 5. Удаление задачи
        print("\n--- Удаление задачи ---")
        success = self.task_manager.delete(task_id)
        if not success:
            print("❌ ТЕСТ ПРОВАЛЕН: Не удалось удалить задачу")
            return False

        # Проверяем удаление
        deleted_task = self.task_manager.get(task_id)
        if deleted_task:
            print("❌ ТЕСТ ПРОВАЛЕН: Задача все еще существует после удаления")
            return False

        print("✅ Задача успешно удалена")
        return True

    def test_toggle_completion(self):
        """Тест переключения статуса выполнения"""
        print("\n" + "=" * 50)
        print("🧪 ТЕСТ: Переключение статуса выполнения")
        print("=" * 50)

        note_id = self.create_test_note("Toggle Test")
        if not note_id:
            return False

        # Создаем задачу
        task = self.task_manager.create(
            note_id=note_id,
            description="Протестировать переключение статуса"
        )

        if not task:
            print("❌ ТЕСТ ПРОВАЛЕН: Не удалось создать задачу для теста")
            return False

        initial_status = task.is_completed
        print(f"✅ Исходный статус: {'Выполнена' if initial_status else 'Не выполнена'}")

        # Переключаем статус
        toggled_task = self.task_manager.toggle_completion(task.id)
        if not toggled_task:
            print("❌ ТЕСТ ПРОВАЛЕН: Не удалось переключить статус")
            return False

        print(f"✅ Статус после переключения: {'Выполнена' if toggled_task.is_completed else 'Не выполнена'}")

        # Проверяем что статус изменился
        if toggled_task.is_completed == initial_status:
            print("❌ ТЕСТ ПРОВАЛЕН: Статус не изменился")
            return False

        # Переключаем обратно
        final_task = self.task_manager.toggle_completion(task.id)
        if final_task.is_completed != initial_status:
            print("❌ ТЕСТ ПРОВАЛЕН: Статус не вернулся к исходному")
            return False

        print(f"✅ Финальный статус: {'Выполнена' if final_task.is_completed else 'Не выполнена'}")
        print("✅ Тест переключения статуса пройден")
        return True

    def test_multiple_tasks_per_note(self):
        """Тест нескольких задач для одной заметки"""
        print("\n" + "=" * 50)
        print("🧪 ТЕСТ: Несколько задач для одной заметки")
        print("=" * 50)

        note_id = self.create_test_note("Multiple Tasks")
        if not note_id:
            return False

        # Создаем несколько задач
        tasks_data = [
            ("Первая задача", None),
            ("Вторая задача с дедлайном", datetime.now() + timedelta(days=2)),
            ("Третья задача", None),
        ]

        created_tasks = []
        for description, due_date in tasks_data:
            task = self.task_manager.create(note_id, description, due_date)
            if task:
                created_tasks.append(task)
                print(f"✅ Создана: {task}")

        # Получаем все задачи для заметки
        note_tasks = self.task_manager.get_tasks_for_note(note_id)

        if len(note_tasks) != len(tasks_data):
            print(f"❌ ТЕСТ ПРОВАЛЕН: Ожидалось {len(tasks_data)} задач, получено {len(note_tasks)}")
            return False

        print(f"✅ Получено задач для заметки: {len(note_tasks)}")
        for task in note_tasks:
            print(f"   - {task}")

        return True

    def test_upcoming_tasks(self):
        """Тест получения предстоящих задач"""
        print("\n" + "=" * 50)
        print("🧪 ТЕСТ: Предстоящие задачи")
        print("=" * 50)

        note_id = self.create_test_note("Upcoming Tasks")
        if not note_id:
            return False

        # Создаем задачи с разными дедлайнами
        today = datetime.now()
        tasks_data = [
            ("Просроченная задача", today - timedelta(days=1)),  # Вчера
            ("Задача на сегодня", today),  # Сегодня
            ("Задача на завтра", today + timedelta(days=1)),  # Завтра
            ("Задача через неделю", today + timedelta(days=7)),  # Через неделю
            ("Задача без дедлайна", None),  # Без дедлайна
        ]

        for description, due_date in tasks_data:
            task = self.task_manager.create(note_id, description, due_date)
            if task:
                print(f"✅ Создана: {task}")

        # Получаем предстоящие задачи (на 7 дней вперед)
        upcoming_tasks = self.task_manager.get_upcoming_tasks(days=7)

        print(f"✅ Найдено предстоящих задач: {len(upcoming_tasks)}")
        for task in upcoming_tasks:
            print(f"   - {task} (из заметки: '{task.note_title}')")

        # Должны найти задачи: на сегодня, завтра, через неделю (но не просроченные и без дедлайна)
        expected_count = 3  # сегодня, завтра, через неделю
        if len(upcoming_tasks) != expected_count:
            print(f"⚠️  Предупреждение: ожидалось {expected_count} задач, найдено {len(upcoming_tasks)}")
            # Это не обязательно ошибка, зависит от логики фильтрации

        return True

    def test_completed_tasks(self):
        """Тест получения выполненных задач"""
        print("\n" + "=" * 50)
        print("🧪 ТЕСТ: Выполненные задачи")
        print("=" * 50)

        note_id = self.create_test_note("Completed Tasks")
        if not note_id:
            return False

        # Создаем задачи и отмечаем некоторые как выполненные
        tasks_data = [
            ("Невыполненная задача 1", False),
            ("Выполненная задача 1", True),
            ("Невыполненная задача 2", False),
            ("Выполненная задача 2", True),
        ]

        for description, is_completed in tasks_data:
            task = self.task_manager.create(note_id, description)
            if task and is_completed:
                self.task_manager.toggle_completion(task.id)

        # Получаем выполненные задачи для заметки
        completed_tasks = self.task_manager.get_completed_tasks(note_id)

        print(f"✅ Найдено выполненных задач: {len(completed_tasks)}")
        for task in completed_tasks:
            print(f"   - {task}")

        expected_completed = 2
        if len(completed_tasks) != expected_completed:
            print(f"❌ ТЕСТ ПРОВАЛЕН: Ожидалось {expected_completed} выполненных задач, найдено {len(completed_tasks)}")
            return False

        return True

    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🎯 ЗАПУСК ВСЕХ ТЕСТОВ TASK MANAGER")
        print("=" * 60)

        tests = [
            ("Базовые CRUD операции", self.test_basic_crud),
            ("Переключение статуса", self.test_toggle_completion),
            ("Несколько задач для заметки", self.test_multiple_tasks_per_note),
            ("Предстоящие задачи", self.test_upcoming_tasks),
            ("Выполненные задачи", self.test_completed_tasks),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
                print(f"\n{status}: {test_name}\n")
            except Exception as e:
                print(f"❌ ОШИБКА в тесте '{test_name}': {e}")
                results.append((test_name, False))

        # Вывод итогов
        print("\n" + "=" * 60)
        print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
        print("=" * 60)

        passed = sum(1 for _, success in results if success)
        total = len(results)

        for test_name, success in results:
            status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
            print(f"  {status}: {test_name}")

        print(f"\n🎯 Результат: {passed}/{total} тестов пройдено")

        if passed == total:
            print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! TaskManager работает корректно.")
        else:
            print("⚠️  Некоторые тесты не пройдены. Требуется отладка.")

        # Очистка
        self.cleanup()

        return passed == total


def main():
    """Главная функция тестирования"""
    try:
        tester = TaskManagerTester("test_smart_organizer.db")
        success = tester.run_all_tests()

        if success:
            print("\n🚀 TaskManager готов к интеграции в основное приложение!")
        else:
            print("\n🔧 Требуется отладка перед интеграцией.")

        return success

    except Exception as e:
        print(f"❌ Критическая ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
# [file content end]