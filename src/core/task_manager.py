from typing import List, Optional
from datetime import datetime
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
        self._create_tasks_table()
        print("✅ Менеджер задач инициализирован")

    def _create_tasks_table(self):
        """Создает таблицу задач с поддержкой приоритетов если не существует"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Сначала проверяем существование таблицы
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='tasks'
                """)
                table_exists = cursor.fetchone()

                if table_exists:
                    # Проверяем существование колонки priority
                    cursor.execute("PRAGMA table_info(tasks)")
                    columns = [column[1] for column in cursor.fetchall()]

                    if 'priority' not in columns:
                        print("🔧 Добавляем колонку priority в таблицу tasks")
                        cursor.execute("""
                            ALTER TABLE tasks 
                            ADD COLUMN priority TEXT DEFAULT 'medium' 
                            CHECK(priority IN ('high', 'medium', 'low'))
                        """)

                    # Также проверяем другие необходимые колонки
                    if 'due_date' not in columns:
                        print("🔧 Добавляем колонку due_date в таблицу tasks")
                        cursor.execute("""
                            ALTER TABLE tasks 
                            ADD COLUMN due_date DATETIME
                        """)
                else:
                    # Создаем таблицу с нуля
                    cursor.execute("""
                        CREATE TABLE tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            note_id INTEGER NOT NULL,
                            description TEXT NOT NULL,
                            is_completed BOOLEAN DEFAULT FALSE,
                            priority TEXT DEFAULT 'medium' CHECK(priority IN ('high', 'medium', 'low')),
                            due_date DATETIME,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
                        )
                    """)
                    print("✅ Таблица задач создана с поддержкой приоритетов и сроков")

                conn.commit()

        except Exception as e:
            print(f"❌ Ошибка при создании/обновлении таблицы задач: {e}")

    def create_task(self, note_id: int, description: str, due_date: Optional[datetime] = None,
                    priority: str = "medium", is_completed: bool = False) -> Optional[Task]:
        """
        Создает новую задачу для указанной заметки

        Args:
            note_id: ID заметки, к которой привязана задача
            description: Описание задачи
            due_date: Срок выполнения (опционально)
            priority: Приоритет задачи ('high', 'medium', 'low')
            is_completed: Статус выполнения (по умолчанию False)

        Returns:
            Task: Созданная задача или None при ошибке
        """
        if not description or not description.strip():
            print("❌ Ошибка: описание задачи не может быть пустым")
            return None

        # Валидация приоритета
        if priority not in ['high', 'medium', 'low']:
            print(f"⚠️  Неверный приоритет '{priority}', установлен 'medium'")
            priority = 'medium'

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
                    """INSERT INTO tasks (note_id, description, due_date, priority, is_completed, created_at, updated_at) 
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                    (note_id, description, due_date.isoformat() if due_date else None, priority,
                     1 if is_completed else 0)
                )
                task_id = cursor.lastrowid
                conn.commit()

                if task_id:
                    task = Task(
                        description=description,
                        is_completed=is_completed,
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id,
                        priority=priority
                    )
                    task.note_title = note_result[1]
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
                    """SELECT t.id, t.note_id, t.description, t.is_completed, t.priority, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.id = ?""",
                    (task_id,)
                )
                result = cursor.fetchone()

                if result:
                    (task_id, note_id, description, is_completed, priority, due_date_str,
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
                        modified_date=updated_date,
                        priority=priority or 'medium'  # Защита от None
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
                    """SELECT t.id, t.description, t.is_completed, t.priority, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.note_id = ? 
                    ORDER BY 
                        CASE priority 
                            WHEN 'high' THEN 1 
                            WHEN 'medium' THEN 2 
                            WHEN 'low' THEN 3 
                        END,
                        t.due_date ASC,
                        t.created_at ASC""",
                    (note_id,)
                )
                results = cursor.fetchall()

                tasks = []
                for (task_id, description, is_completed, priority, due_date_str,
                     created_at, updated_at, note_title) in results:

                    # ПРЕОБРАЗОВАНИЕ ДАТЫ
                    due_date = None
                    if due_date_str:
                        try:
                            due_date = datetime.fromisoformat(due_date_str)
                        except ValueError as e:
                            print(f"⚠️ Ошибка преобразования даты '{due_date_str}': {e}")

                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    updated_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    task = Task(
                        description=description,
                        is_completed=bool(is_completed),
                        task_id=task_id,
                        due_date=due_date,  # УБЕДИТЕСЬ ЧТО ЭТО ПЕРЕДАЕТСЯ
                        note_id=note_id,
                        created_date=created_date,
                        modified_date=updated_date,
                        priority=priority  # УБЕДИТЕСЬ ЧТО ЭТО ПЕРЕДАЕТСЯ
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Загружено задач для заметки {note_id}: {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении задач для заметки {note_id}: {e}")
            return []

    def update_task(self, task_id: int, description: Optional[str] = None,
                    is_completed: Optional[bool] = None, due_date: Optional[datetime] = None,
                    priority: Optional[str] = None) -> bool:
        """
        Обновляет данные задачи

        Args:
            task_id: ID задачи
            description: Новое описание
            is_completed: Новый статус выполнения
            due_date: Новый срок выполнения
            priority: Новый приоритет

        Returns:
            bool: True если обновление успешно
        """
        # Проверяем существование задачи
        existing_task = self.get_task(task_id)
        if not existing_task:
            return False

        # Валидация приоритета
        if priority is not None and priority not in ['high', 'medium', 'low']:
            print(f"⚠️  Неверный приоритет '{priority}', приоритет не изменен")
            priority = None

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

                # ИСПРАВЛЕНИЕ: Не сбрасываем due_date если он не указан явно
                if due_date is not None:
                    update_fields.append("due_date = ?")
                    update_values.append(due_date.isoformat() if due_date else None)
                # УБИРАЕМ эту часть - она сбрасывает дедлайн!
                # elif due_date is None and existing_task.due_date is not None:
                #     # Явное удаление due_date
                #     update_fields.append("due_date = NULL")

                if priority is not None:
                    update_fields.append("priority = ?")
                    update_values.append(priority)

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

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """
        Возвращает задачи по приоритету

        Args:
            priority: Приоритет ('high', 'medium', 'low')

        Returns:
            List[Task]: Список задач с указанным приоритетом
        """
        if priority not in ['high', 'medium', 'low']:
            print(f"❌ Неверный приоритет: {priority}")
            return []

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.id, t.note_id, t.description, t.is_completed, t.priority, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.priority = ? 
                    ORDER BY t.due_date, t.created_at""",
                    (priority,)
                )
                results = cursor.fetchall()

                tasks = []
                for (task_id, note_id, description, is_completed, task_priority, due_date_str,
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
                        modified_date=updated_date,
                        priority=task_priority
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Найдено задач с приоритетом '{priority}': {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении задач по приоритету: {e}")
            return []

    def get_urgent_tasks(self) -> List[Task]:
        """
        Возвращает срочные задачи (высокий приоритет + срок в ближайшие 3 дня)

        Returns:
            List[Task]: Список срочных задач
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.id, t.note_id, t.description, t.is_completed, t.priority, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.priority = 'high' 
                    AND t.due_date IS NOT NULL 
                    AND date(t.due_date) BETWEEN date('now') AND date('now', '+3 days')
                    AND t.is_completed = FALSE
                    ORDER BY t.due_date ASC""",
                )
                results = cursor.fetchall()

                tasks = []
                for (task_id, note_id, description, is_completed, priority, due_date_str,
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
                        modified_date=updated_date,
                        priority=priority
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Найдено срочных задач: {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении срочных задач: {e}")
            return []

    def get_tasks_with_due_dates(self) -> List[Task]:
        """
        Возвращает все задачи с установленными сроками

        Returns:
            List[Task]: Список задач со сроками
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.id, t.note_id, t.description, t.is_completed, t.priority, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.due_date IS NOT NULL 
                    ORDER BY t.due_date ASC, 
                        CASE priority 
                            WHEN 'high' THEN 1 
                            WHEN 'medium' THEN 2 
                            WHEN 'low' THEN 3 
                        END""",
                )
                results = cursor.fetchall()

                tasks = []
                for (task_id, note_id, description, is_completed, priority, due_date_str,
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
                        modified_date=updated_date,
                        priority=priority
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Найдено задач со сроками: {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении задач со сроками: {e}")
            return []

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
        """Возвращает все невыполненные задачи из всех заметок"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.id, t.note_id, t.description, t.is_completed, t.priority, t.due_date, 
                              t.created_at, t.updated_at, n.title
                    FROM tasks t
                    JOIN notes n ON t.note_id = n.id
                    WHERE t.is_completed = FALSE
                    ORDER BY 
                        CASE priority 
                            WHEN 'high' THEN 1 
                            WHEN 'medium' THEN 2 
                            WHEN 'low' THEN 3 
                        END,
                        t.due_date,
                        t.created_at""",
                )
                results = cursor.fetchall()

                tasks = []
                for (task_id, note_id, description, is_completed, priority, due_date_str,
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
                        modified_date=updated_date,
                        priority=priority
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
                for (task_id, note_id, description, is_completed, priority, due_date_str,
                     created_at, updated_at, note_title) in results:
                    due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    modified_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()


                    task = Task(
                        description=description,
                        is_completed=bool(is_completed),
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id,
                        created_date=created_date,
                        modified_date=modified_date,
                        priority=priority
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
                        (task_id, note_id, description, is_completed, priority, due_date_str,
                         created_at, updated_at, note_title) = result
                    else:
                        # Альтернативная распаковка если полей меньше
                        task_id, note_id, description, is_completed, due_date_str, created_at, updated_at = result[:7]
                        note_title = "Unknown"  # Значение по умолчанию

                    due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    modified_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    task = Task(
                        description=description,
                        is_completed=bool(is_completed),
                        task_id=task_id,
                        due_date=due_date,
                        note_id=note_id,
                        created_date=created_date,
                        modified_date=modified_date,
                        priority=priority
                    )
                    task.note_title = note_title
                    tasks.append(task)

                print(f"✅ Найдено выполненных задач: {len(tasks)}")
                return tasks

        except Exception as e:
            print(f"❌ Ошибка при получении выполненных задач: {e}")
            return []

    def parse_tasks_from_html(self, html_content: str) -> List[Task]:
        """
        Парсит задачи из HTML-контента заметки

        Ищет специальные маркеры задач в HTML:
        - Элементы с data-type="task"
        - Чекбоксы с определенными классами
        - Специальные списки задач

        Args:
            html_content: HTML-код заметки

        Returns:
            List[Task]: Список найденных задач
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("❌ BeautifulSoup не установлен. Установите: pip install beautifulsoup4")
            return []

        tasks = []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Ищем задачи в специальных task-блоках
            task_elements = soup.find_all(attrs={"data-type": "task"})

            for task_elem in task_elements:
                # Извлекаем данные задачи
                task_id = task_elem.get('data-task-id')
                description = task_elem.get('data-description', '').strip()
                is_completed = task_elem.get('data-completed', 'false').lower() == 'true'

                # Получаем due_date если есть
                due_date_str = task_elem.get('data-due-date')
                due_date = None
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str)
                    except ValueError:
                        pass

                if description:  # Только задачи с описанием
                    task = Task(
                        description=description,
                        is_completed=is_completed,
                        task_id=int(task_id) if task_id else None,
                        due_date=due_date
                    )
                    tasks.append(task)

            print(f"✅ Извлечено задач из HTML: {len(tasks)}")
            return tasks

        except Exception as e:
            print(f"❌ Ошибка при парсинге задач из HTML: {e}")
            return []

    def generate_html_from_tasks(self, tasks: List[Task]) -> str:
        """
        Генерирует HTML-код для списка задач

        Args:
            tasks: Список задач

        Returns:
            str: HTML-код с чекбоксами
        """
        if not tasks:
            return ""

        html_parts = ['<div class="task-list">']

        for task in tasks:
            checked = "checked" if task.is_completed else ""
            due_date_attr = f' data-due-date="{task.due_date.isoformat()}"' if task.due_date else ""

            task_html = f'''
            <div class="task-item" data-type="task" data-task-id="{task.id or ''}" 
                 data-description="{task.description}" data-completed="{str(task.is_completed).lower()}"{due_date_attr}>
                <input type="checkbox" class="task-checkbox" {checked} onchange="toggleTask(this)">
                <span class="task-text">{task.description}</span>
            </div>
            '''
            html_parts.append(task_html)

        html_parts.append('</div>')
        return '\n'.join(html_parts)

    def extract_and_save_tasks(self, note_id: int, html_content: str) -> bool:
        """
        Извлекает задачи из HTML и сохраняет их в БД

        Args:
            note_id: ID заметки
            html_content: HTML-контент заметки

        Returns:
            bool: True если успешно
        """
        try:
            # Парсим задачи из HTML
            tasks_from_html = self.parse_tasks_from_html(html_content)

            # Получаем существующие задачи для этой заметки
            existing_tasks = self.get_tasks_for_note(note_id)
            existing_task_map = {task.description: task for task in existing_tasks}

            # Обновляем или создаем задачи
            for html_task in tasks_from_html:
                if html_task.description in existing_task_map:
                    # Обновляем существующую задачу
                    existing_task = existing_task_map[html_task.description]
                    self.update_task(
                        existing_task.id,
                        is_completed=html_task.is_completed,
                        due_date=html_task.due_date
                    )
                else:
                    # Создаем новую задачу
                    self.create_task(
                        note_id,
                        html_task.description,
                        html_task.due_date
                    )

            print(f"✅ Задачи синхронизированы для заметки {note_id}")
            return True

        except Exception as e:
            print(f"❌ Ошибка при синхронизации задач: {e}")
            return False

    def debug_tasks_for_note(self, note_id: int):
        """Отладочный метод: показывает сырые данные из БД"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, description, is_completed FROM tasks WHERE note_id = ? ORDER BY created_at",
                    (note_id,)
                )
                results = cursor.fetchall()

                print(f"🔍 ОТЛАДКА БД для заметки {note_id}:")
                for task_id, description, is_completed in results:
                    print(
                        f"   📊 ID: {task_id}, Описание: '{description}', is_completed: {is_completed} (тип: {type(is_completed)})")

        except Exception as e:
            print(f"❌ Ошибка отладки: {e}")
