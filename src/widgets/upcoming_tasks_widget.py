from PyQt6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QCheckBox, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

from gui.ui_task_widget import Ui_TaskWidget


class UpcomingTasksWidget(QWidget, Ui_TaskWidget):
    """Виджет для отображения предстоящих задач из ВСЕХ заметок"""

    navigate_to_note_requested = pyqtSignal(int)  # note_id
    task_toggled = pyqtSignal(int, bool)  # task_id, is_completed
    navigate_to_note = pyqtSignal(int)  # note_id

    def __init__(self, task_manager, note_manager, workspace_id=1, parent=None):
        super().__init__()
        self.task_manager = task_manager
        self.note_manager = note_manager
        self.workspace_id = workspace_id
        self.setupUi(self)

        # Настройка дополнительных параметров UI
        self.setup_additional_ui()
        self.connect_signals()
        self.load_tasks()

    def setup_additional_ui(self):
        """Дополнительная настройка UI"""
        # Настройка списка задач
        self.tasks_list.setAlternatingRowColors(True)

        # Добавляем недостающие фильтры в комбо-боксы
        self.add_missing_filters()

        # Подключаем сигналы
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)

    def add_missing_filters(self):
        """Добавляет недостающие фильтры в комбо-боксы"""
        # Добавляем фильтры
        # self.filter_combo.addItem("Просроченные")
        self.filter_combo.addItem("С дедлайном")

        # Добавляем сортировки
        self.sort_combo.addItem("По приоритету и сроку")

    def connect_signals(self):
        """Подключение сигналов"""
        #self.pushButton.clicked.connect(self.refresh)

    def set_workspace(self, workspace_id):
        """Обновляет workspace и перезагружает задачи"""
        self.workspace_id = workspace_id
        self.load_tasks()

    def load_tasks(self):
        """Загрузка и отображение задач"""
        self.tasks_list.clear()

        # Получаем задачи в зависимости от фильтра
        filter_type = self.filter_combo.currentText()
        sort_type = self.sort_combo.currentText()

        if filter_type == "Все задачи":
            tasks = self.get_all_tasks_with_details()
        elif filter_type == "Только активные":
            tasks = self.get_all_incomplete_tasks_with_details()
        elif filter_type == "Только выполненные":
            tasks = self.get_completed_tasks_with_details()
        # elif filter_type == "Просроченные":
        #     tasks = self.get_overdue_tasks()
        elif filter_type == "С дедлайном":
            tasks = self.get_tasks_with_due_dates()
        else:
            tasks = self.get_all_incomplete_tasks_with_details()

        # Сортируем задачи в зависимости от выбранной сортировки
        if sort_type == "По приоритету и сроку":
            tasks = self.sort_tasks_by_priority_and_due_date(tasks)
        elif sort_type == "По сроку выполнения":
            tasks = self.sort_tasks_by_due_date(tasks)
        elif sort_type == "По приоритету":
            tasks = self.sort_tasks_by_priority(tasks)
        else:  # По дате создания (по умолчанию)
            tasks = self.sort_tasks_by_creation_date(tasks)

        # Отображаем задачи
        for task in tasks:
            self.add_task_item(task)

        # Обновляем статистику
        self.update_stats(tasks)

    def get_all_tasks_with_details(self):
        """Получает ВСЕ задачи с полной информацией о приоритетах и дедлайнах для текущего workspace"""
        try:
            all_tasks = []
            # Получаем только заметки текущего workspace
            all_notes = self.note_manager.get_notes_by_workspace(self.workspace_id)

            print(f"🔍 Загружаем задачи для {len(all_notes)} заметок workspace {self.workspace_id}")

            for note in all_notes:
                # Используем метод, который загружает задачи с приоритетами и дедлайнами
                note_tasks = self.task_manager.get_tasks_for_note(note.id)
                print(f"📝 Заметка '{note.title}': {len(note_tasks)} задач")

                for task in note_tasks:
                    # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
                    due_info = f" (до {task.due_date.strftime('%d.%m.%Y')})" if task.due_date else " (без срока)"
                    priority_info = f" [приоритет: {task.priority}]" if hasattr(task,
                                                                                'priority') else " [приоритет: нет]"
                    print(f"   ✅ Задача: '{task.description}'{due_info}{priority_info}")

                    task.note_title = note.title
                    task.note_id = note.id  # Убедимся, что note_id установлен
                    all_tasks.append(task)

            print(f"📊 Всего загружено задач в workspace {self.workspace_id}: {len(all_tasks)}")
            return all_tasks

        except Exception as e:
            print(f"❌ Ошибка при получении всех задач для workspace {self.workspace_id}: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_all_incomplete_tasks_with_details(self):
        """Получает невыполненные задачи с полной информацией для текущего workspace"""
        try:
            all_tasks = []
            # Получаем только заметки текущего workspace
            all_notes = self.note_manager.get_notes_by_workspace(self.workspace_id)

            for note in all_notes:
                note_tasks = self.task_manager.get_tasks_for_note(note.id)
                for task in note_tasks:
                    if not task.is_completed:
                        task.note_title = note.title
                        task.note_id = note.id
                        all_tasks.append(task)

            return all_tasks

        except Exception as e:
            print(f"Ошибка при получении невыполненных задач для workspace {self.workspace_id}: {e}")
            return []

    def get_completed_tasks_with_details(self):
        """Получает выполненные задачи с полной информацией для текущего workspace"""
        try:
            all_tasks = []
            # Получаем только заметки текущего workspace
            all_notes = self.note_manager.get_notes_by_workspace(self.workspace_id)

            for note in all_notes:
                note_tasks = self.task_manager.get_tasks_for_note(note.id)
                for task in note_tasks:
                    if task.is_completed:
                        task.note_title = note.title
                        task.note_id = note.id
                        all_tasks.append(task)

            return all_tasks

        except Exception as e:
            print(f"Ошибка при получении выполненных задач для workspace {self.workspace_id}: {e}")
            return []

    def get_tasks_with_due_dates(self):
        """Получает задачи с установленными дедлайнами (ВСЕ, включая выполненные) для текущего workspace"""
        try:
            all_tasks = []
            # Получаем только заметки текущего workspace
            all_notes = self.note_manager.get_notes_by_workspace(self.workspace_id)

            for note in all_notes:
                note_tasks = self.task_manager.get_tasks_for_note(note.id)
                for task in note_tasks:
                    if task.due_date:  # УБИРАЕМ проверку на is_completed
                        task.note_title = note.title
                        task.note_id = note.id
                        all_tasks.append(task)

            print(
                f"✅ Найдено задач с дедлайнами в workspace {self.workspace_id}: {len(all_tasks)} (включая выполненные)")
            return all_tasks

        except Exception as e:
            print(f"Ошибка при получении задач с дедлайнами для workspace {self.workspace_id}: {e}")
            return []

    def get_high_priority_tasks(self):
        """Получает задачи с высоким приоритетом для текущего workspace"""
        try:
            all_tasks = []
            # Получаем только заметки текущего workspace
            all_notes = self.note_manager.get_notes_by_workspace(self.workspace_id)

            for note in all_notes:
                note_tasks = self.task_manager.get_tasks_for_note(note.id)
                for task in note_tasks:
                    if task.priority == "high" and not task.is_completed:
                        task.note_title = note.title
                        task.note_id = note.id
                        all_tasks.append(task)

            return all_tasks

        except Exception as e:
            print(f"Ошибка при получении задач с высоким приоритетом для workspace {self.workspace_id}: {e}")
            return []

    def sort_tasks_by_priority_and_due_date(self, tasks):
        """Сортирует задачи по приоритету и сроку выполнения"""
        priority_order = {"high": 1, "medium": 2, "low": 3}

        sorted_tasks = sorted(tasks, key=lambda task: (
            priority_order.get(task.priority, 2),  # Сначала по приоритету
            task.due_date or self.get_max_date(),  # Затем по сроку (без срока - в конец)
            task.description.lower()  # Затем по описанию
        ))

        return sorted_tasks

    def sort_tasks_by_priority(self, tasks):
        """Сортирует задачи только по приоритету"""
        priority_order = {"high": 1, "medium": 2, "low": 3}

        sorted_tasks = sorted(tasks, key=lambda task: (
            priority_order.get(task.priority, 2),
            task.description.lower()
        ))

        return sorted_tasks

    def sort_tasks_by_due_date(self, tasks):
        """Сортирует задачи только по сроку выполнения"""
        sorted_tasks = sorted(tasks, key=lambda task: (
            task.due_date or self.get_max_date(),  # Сначала с дедлайном
            task.description.lower()
        ))

        return sorted_tasks

    def sort_tasks_by_creation_date(self, tasks):
        """Сортирует задачи по дате создания (по умолчанию)"""
        # Если у задач есть created_date, используем его, иначе сортируем по описанию
        if tasks and hasattr(tasks[0], 'created_date'):
            sorted_tasks = sorted(tasks, key=lambda task: (
                task.created_date,
                task.description.lower()
            ))
        else:
            sorted_tasks = sorted(tasks, key=lambda task: task.description.lower())

        return sorted_tasks

    def get_max_date(self):
        """Возвращает максимальную дату для сортировки"""
        from datetime import datetime
        return datetime(9999, 12, 31)

    def add_task_item(self, task):
        """Добавляет задачу в список (теперь использует create_task_widget)"""
        # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
        due_info = f" (до {task.due_date.strftime('%d.%m.%Y')})" if task.due_date else " (без срока)"
        priority_info = f" [приоритет: {task.priority}]" if hasattr(task, 'priority') else " [приоритет: нет]"
        status_info = " [ВЫПОЛНЕНА]" if task.is_completed else " [АКТИВНА]"
        print(f"🎯 Отображаем задачу: '{task.description}'{due_info}{priority_info}{status_info}")

        # Создаем элемент списка
        list_item = QListWidgetItem(self.tasks_list)
        list_item.setData(Qt.ItemDataRole.UserRole, task.id)

        # Создаем виджет задачи
        task_widget = self.create_task_widget(task)

        list_item.setSizeHint(task_widget.sizeHint())
        self.tasks_list.addItem(list_item)
        self.tasks_list.setItemWidget(list_item, task_widget)

    def get_priority_text(self, priority):
        """Возвращает текстовое описание приоритета"""
        priority_texts = {
            "high": "Высокий",
            "medium": "Средний",
            "low": "Низкий"
        }
        return priority_texts.get(priority, "Средний")

    def is_overdue(self, due_date):
        """Проверяет, просрочена ли задача"""
        from datetime import datetime
        return due_date < datetime.now()

    def on_task_toggled(self, task_id, state):
        """Обработчик изменения чекбокса задачи"""
        is_completed = state == Qt.CheckState.Checked.value

        print(f"🔄 Изменение статуса задачи {task_id}: {is_completed}")

        # Получаем текущую задачу чтобы сохранить дедлайн
        current_task = self.task_manager.get_task(task_id)
        if not current_task:
            print(f"❌ Не удалось найти задачу {task_id}")
            return

        # Обновляем в БД, ЯВНО передавая текущий дедлайн чтобы он не сбросился
        success = self.task_manager.update_task(
            task_id,
            is_completed=is_completed,
            due_date=current_task.due_date  # ЯВНО передаем текущий дедлайн
        )

        if success:
            self.task_toggled.emit(task_id, is_completed)
            print(f"✅ Задача {task_id} отмечена как {'выполнена' if is_completed else 'не выполнена'}")

            # ОБНОВЛЯЕМ ВЕСЬ СПИСОК ЗАДАЧ АВТОМАТИЧЕСКИ
            self.refresh_tasks_after_toggle()
        else:
            print(f"❌ Ошибка обновления задачи {task_id}")

    def refresh_tasks_after_toggle(self):
        """Обновляет список задач после изменения состояния чекбокса"""
        print("🔄 Автоматическое обновление списка задач после изменения статуса...")

        # Сохраняем текущие настройки фильтра и сортировки
        current_filter = self.filter_combo.currentText()
        current_sort = self.sort_combo.currentText()

        # Перезагружаем задачи
        self.load_tasks()

        # Восстанавливаем настройки фильтра и сортировки
        self.filter_combo.setCurrentText(current_filter)
        self.sort_combo.setCurrentText(current_sort)

        print("✅ Список задач обновлен после изменения статуса")

    def update_single_task_display(self, task_id, is_completed):
        """Обновляет отображение только одной задачи - ГАРАНТИРУЕМ что дедлайн всегда виден"""
        # Находим задачу в списке
        for i in range(self.tasks_list.count()):
            item = self.tasks_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task_id:
                # Получаем полную информацию о задаче из БД
                task = self.task_manager.get_task(task_id)
                if not task:
                    continue

                # УДАЛЯЕМ старый виджет и СОЗДАЕМ НОВЫЙ с гарантированным отображением дедлайна
                old_widget = self.tasks_list.itemWidget(item)
                if old_widget:
                    self.tasks_list.removeItemWidget(item)
                    old_widget.deleteLater()

                # СОЗДАЕМ НОВЫЙ виджет с актуальной информацией
                new_widget = self.create_task_widget(task)
                self.tasks_list.setItemWidget(item, new_widget)
                item.setSizeHint(new_widget.sizeHint())

                print(f"🔄 Обновлена задача: '{task.description}' - выполнена: {is_completed}, дедлайн: {task.due_date}")
                break

    def create_task_widget(self, task):
        """Создает виджет задачи с ГАРАНТИРОВАННЫМ отображением дедлайна"""
        # Создаем кастомный виджет для элемента списка
        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        # Чекбокс задачи
        checkbox = QCheckBox()
        checkbox.setChecked(task.is_completed)
        checkbox.stateChanged.connect(
            lambda state, task_id=task.id: self.on_task_toggled(task_id, state)
        )
        checkbox.setFixedSize(20, 20)
        layout.addWidget(checkbox)

        # ИКОНКА ПРИОРИТЕТА
        priority_icons = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        priority_icon = priority_icons.get(task.priority, "⚪")

        priority_label = QLabel(priority_icon)
        priority_label.setToolTip(f"Приоритет: {self.get_priority_text(task.priority)}")
        priority_label.setFixedWidth(25)
        layout.addWidget(priority_label)

        # ОПИСАНИЕ ЗАДАЧИ И ДЕДЛАЙН
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)

        # Описание задачи
        task_label = QLabel(task.description)
        task_label.setWordWrap(True)

        # Стили в зависимости от статуса и приоритета
        if task.is_completed:
            task_label.setStyleSheet("text-decoration: line-through; color: gray; font-size: 12px;")
        elif task.priority == "high":
            task_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        elif task.priority == "low":
            task_label.setStyleSheet("color: #666; font-size: 12px;")
        else:
            task_label.setStyleSheet("font-size: 12px;")

        content_layout.addWidget(task_label)

        # ДЕДЛАЙН - ВСЕГДА ОТОБРАЖАЕМ, ДАЖЕ ЕСЛИ ЕГО НЕТ!
        due_date_str = task.due_date.strftime('%d.%m.%Y') if task.due_date else "не установлен"
        due_label = QLabel(f"📅 {due_date_str}")

        # Стиль для дедлайна
        if task.is_completed:
            # Выполненная задача - серый, зачеркнутый, но ВИДИМЫЙ
            due_label.setStyleSheet("color: gray; font-size: 10px; text-decoration: line-through;")
            due_label.setToolTip(f"Срок выполнения: {due_date_str} (задача выполнена)")
        elif task.due_date and self.is_overdue(task.due_date):
            # Просроченная активная задача - красный
            due_label.setStyleSheet("color: red; font-weight: bold; font-size: 10px;")
            due_label.setToolTip("ПРОСРОЧЕНО!")
        elif task.due_date:
            # Обычный дедлайн - серый
            due_label.setStyleSheet("color: #666; font-size: 10px;")
            due_label.setToolTip(f"Срок выполнения: {due_date_str}")
        else:
            # Нет дедлайна - светло-серый
            due_label.setStyleSheet("color: #999; font-size: 10px;")
            due_label.setToolTip("Срок не установлен")

        content_layout.addWidget(due_label)

        layout.addWidget(content_widget)
        layout.addStretch()

        # Кнопка перехода к заметке
        if hasattr(task, 'note_id') and task.note_id:
            note_title = getattr(task, 'note_title', f"Заметка {task.note_id}")
            note_btn = QPushButton(f"📝")
            note_btn.setToolTip(f"Перейти к заметке: {note_title}")
            note_btn.setFixedSize(30, 30)
            note_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid gray;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            note_btn.clicked.connect(
                lambda checked, note_id=task.note_id: self.navigate_to_note_requested.emit(note_id)
            )
            layout.addWidget(note_btn)

        return item_widget

    def update_stats(self, tasks):
        """Обновление статистики"""
        total = len(tasks)
        completed = sum(1 for task in tasks if task.is_completed)
        active = total - completed

        # Подсчет дополнительной статистики
        high_priority = sum(1 for task in tasks if task.priority == "high" and not task.is_completed)
        overdue = sum(1 for task in tasks if task.due_date and self.is_overdue(task.due_date) and not task.is_completed)

        self.total_label.setText(f"Всего: {total}")
        self.active_label.setText(f"Активные: {active}")
        self.completed_label.setText(f"Выполнено: {completed}")

        # Вывод отладочной информации
        print(f"📊 Статистика workspace {self.workspace_id}: {total} всего, {active} активных, {completed} выполненных")
        print(f"📊 Детали: {high_priority} высокого приоритета, {overdue} просроченных")

    def on_filter_changed(self):
        """Обработчик изменения фильтра"""
        self.load_tasks()

    def on_sort_changed(self):
        """Обработчик изменения сортировки"""
        self.load_tasks()

    def refresh(self):
        """Обновляет список задач ТОЛЬКО при явном вызове"""
        self.load_tasks()
