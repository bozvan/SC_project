import sqlite3
from typing import List, Optional
from datetime import datetime, timedelta
from .models import Task
from .database_manager import DatabaseManager


class TaskManager:
    """Менеджер для работы с задачами в базе данных"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация менеджера задач

        Args:
            db_manager: Экземпляр DatabaseManager для работы с БД
        """
        self.db = db_manager
        print("✅ Менеджер задач инициализирован")

    def create_task(self, note_id: int, description: str, due_date: Optional[datetime] = None) -> Optional[Task]:
        """
        Создает новую задачу для указанной заметки

        Args:
            note_id: ID заметки, к которой привязана задача
            description: Описание задачи
            due_date: Срок выполнения (опционально)

        Returns:
            Task: Созданная задача или None при ошибке
        """
        if not description or not description.strip():
            print("❌ Ошибка: описание задачи не может быть пустым")
            return None

        description = description.strip()

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем существование заметки
                cursor.execute("SELECT id, title FROM notes WHERE id = ?", (note_id,))
                note_result = cursor.fetchone()
                if not note_result:
                    print(f"❌ Заметка с ID {note_id} не существует")
                    return None

                # Вставляем задачу
                cursor.execute(
                    """INSERT INTO tasks (note_id, description, due_date, created_at, updated_at) 
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                    (note_id, description, due_date.isoformat() if due_date else None)
                )
                task_id = cursor.lastrowid
                conn.commit()

                if task_id:
                    task = Task(
                        description=description,
                        is_completed=False,
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id
                    )
                    task.note_title = note_result[1]  # Добавляем заголовок заметки
                    print(f"✅ Задача создана: {task}")
                    return task
                else:
                    print("❌ Ошибка: не удалось получить ID созданной задачи")
                    return None

        except Exception as e:
            print(f"❌ Ошибка при создании задачи: {e}")
            return None

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Возвращает задачу по ID

        Args:
            task_id: ID задачи

        Returns:
            Task: Найденная задача или None если не найдена
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.id, t.note_id, t.description, t.is_completed, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.id = ?""",
                    (task_id,)
                )
                result = cursor.fetchone()

                if result:
                    (task_id, note_id, description, is_completed, due_date_str,
                     created_at, updated_at, note_title) = result

                    # Преобразуем строки в datetime
                    due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    updated_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    task = Task(
                        description=description,
                        is_completed=bool(is_completed),
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id,
                        created_date=created_date,
                        updated_date=updated_date
                    )
                    task.note_title = note_title

                    return task
                else:
                    print(f"❌ Задача с ID {task_id} не найдена")
                    return None

        except Exception as e:
            print(f"❌ Ошибка при получении задачи с ID {task_id}: {e}")
            return None

    def get_tasks_for_note(self, note_id: int) -> List[Task]:
        """
        Возвращает все задачи для указанной заметки

        Args:
            note_id: ID заметки

        Returns:
            List[Task]: Список задач заметки
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.id, t.description, t.is_completed, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.note_id = ? 
                    ORDER BY t.is_completed, t.due_date, t.created_at""",
                    (note_id,)
                )
                results = cursor.fetchall()

                tasks = []
                for (task_id, description, is_completed, due_date_str,
                     created_at, updated_at, note_title) in results:
                    # Преобразуем строки в datetime
                    due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    updated_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    task = Task(
                        description=description,
                        is_completed=bool(is_completed),
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id,
                        created_date=created_date,
                        updated_date=updated_date
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Загружено задач для заметки {note_id}: {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении задач для заметки {note_id}: {e}")
            return []

    def update_task(self, task_id: int, description: Optional[str] = None,
                    is_completed: Optional[bool] = None, due_date: Optional[datetime] = None) -> bool:
        """
        Обновляет данные задачи

        Args:
            task_id: ID задачи
            description: Новое описание
            is_completed: Новый статус выполнения
            due_date: Новый срок выполнения

        Returns:
            bool: True если обновление успешно
        """
        # Проверяем существование задачи
        existing_task = self.get_task(task_id)
        if not existing_task:
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                update_fields = []
                update_values = []

                if description is not None and description.strip():
                    update_fields.append("description = ?")
                    update_values.append(description.strip())

                if is_completed is not None:
                    update_fields.append("is_completed = ?")
                    update_values.append(1 if is_completed else 0)

                if due_date is not None:
                    update_fields.append("due_date = ?")
                    update_values.append(due_date.isoformat() if due_date else None)
                elif due_date is None and existing_task.due_date is not None:
                    # Явное удаление due_date
                    update_fields.append("due_date = NULL")

                # Всегда обновляем updated_at
                update_fields.append("updated_at = CURRENT_TIMESTAMP")

                if update_fields:
                    update_values.append(task_id)
                    update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(update_query, update_values)
                    conn.commit()

                    print(f"✅ Задача с ID {task_id} обновлена")
                    return True
                else:
                    print("⚠️  Нет полей для обновления")
                    return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении задачи с ID {task_id}: {e}")
            return False

    def delete_task(self, task_id: int) -> bool:
        """
        Удаляет задачу

        Args:
            task_id: ID задачи для удаления

        Returns:
            bool: True если удаление успешно
        """
        # Проверяем существование задачи
        existing_task = self.get_task(task_id)
        if not existing_task:
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Задача '{existing_task.description}' (ID: {task_id}) удалена")
                    return True
                else:
                    print(f"❌ Не удалось удалить задачу с ID {task_id}")
                    return False

        except Exception as e:
            print(f"❌ Ошибка при удалении задачи с ID {task_id}: {e}")
            return False

    def toggle_task_completion(self, task_id: int) -> Optional[Task]:
        """
        Переключает статус выполнения задачи

        Args:
            task_id: ID задачи

        Returns:
            Task: Обновленная задача или None при ошибке
        """
        task = self.get_task(task_id)
        if not task:
            return None

        new_status = not task.is_completed
        success = self.update_task(task_id, is_completed=new_status)

        if success:
            task.is_completed = new_status
            task.updated_date = datetime.now()
            status_text = "выполнена" if new_status else "не выполнена"
            print(f"✅ Задача '{task.description}' помечена как {status_text}")
            return task
        else:
            return None

    def get_all_incomplete_tasks(self) -> List[Task]:
        """
        Возвращает все невыполненные задачи из всех заметок

        Returns:
            List[Task]: Список невыполненных задач
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.id, t.note_id, t.description, t.is_completed, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.is_completed = FALSE
                    ORDER BY t.due_date, t.created_at""",
                )
                results = cursor.fetchall()

                tasks = []
                for (task_id, note_id, description, is_completed, due_date_str,
                     created_at, updated_at, note_title) in results:
                    due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    updated_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    task = Task(
                        description=description,
                        is_completed=bool(is_completed),
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id,
                        created_date=created_date,
                        updated_date=updated_date
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Найдено невыполненных задач: {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении невыполненных задач: {e}")
            return []

    def get_upcoming_tasks(self, days_ahead: int = 7) -> List[Task]:
        """
        Возвращает предстоящие задачи с дедлайнами

        Args:
            days_ahead: Количество дней вперед для поиска

        Returns:
            List[Task]: Список предстоящих задач
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Задачи с дедлайном в ближайшие `days_ahead` дней, не выполненные
                cursor.execute(
                    """SELECT t.id, t.note_id, t.description, t.is_completed, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.due_date IS NOT NULL 
                    AND date(t.due_date) BETWEEN date('now') AND date('now', ? || ' days')
                    AND t.is_completed = FALSE
                    ORDER BY t.due_date ASC, t.created_at ASC""",
                    (f"+{days_ahead}",)
                )
                results = cursor.fetchall()

                tasks = []
                for (task_id, note_id, description, is_completed, due_date_str,
                     created_at, updated_at, note_title) in results:
                    due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    updated_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    task = Task(
                        description=description,
                        is_completed=bool(is_completed),
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id,
                        created_date=created_date,
                        updated_date=updated_date
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Найдено предстоящих задач (на {days_ahead} дней): {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении предстоящих задач: {e}")
            return []

    def get_completed_tasks(self, note_id: Optional[int] = None) -> List[Task]:
        """
        Возвращает выполненные задачи

        Args:
            note_id: Опционально - фильтр по заметке

        Returns:
            List[Task]: Список выполненных задач
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                if note_id:
                    cursor.execute(
                        """SELECT t.id, t.note_id, t.description, t.is_completed, t.due_date, 
                                  t.created_at, t.updated_at, n.title
                        FROM tasks t
                        JOIN notes n ON t.note_id = n.id
                        WHERE t.note_id = ? AND t.is_completed = TRUE 
                        ORDER BY t.updated_at DESC""",
                        (note_id,)
                    )
                else:
                    cursor.execute(
                        """SELECT t.id, t.note_id, t.description, t.is_completed, t.due_date, 
                                  t.created_at, t.updated_at, n.title
                        FROM tasks t
                        JOIN notes n ON t.note_id = n.id
                        WHERE t.is_completed = TRUE 
                        ORDER BY t.updated_at DESC"""
                    )

                results = cursor.fetchall()

                tasks = []
                for result in results:
                    # Безопасная распаковка с проверкой количества полей
                    if len(result) == 8:
                        (task_id, note_id, description, is_completed, due_date_str,
                         created_at, updated_at, note_title) = result
                    else:
                        # Альтернативная распаковка если полей меньше
                        task_id, note_id, description, is_completed, due_date_str, created_at, updated_at = result[:7]
                        note_title = "Unknown"  # Значение по умолчанию

                    due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    updated_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    task = Task(
                        description=description,
                        is_completed=bool(is_completed),
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id,
                        created_date=created_date,
                        updated_date=updated_date
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Найдено выполненных задач: {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении выполненных задач: {e}")
            return []