from PyQt6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QCheckBox, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from src.gui.ui_task_widget import Ui_TaskWidget


class UpcomingTasksWidget(QWidget, Ui_TaskWidget):
    """Виджет для отображения предстоящих задач из ВСЕХ заметок"""

    navigate_to_note_requested = pyqtSignal(int)  # note_id
    task_toggled = pyqtSignal(int, bool)  # task_id, is_completed
    navigate_to_note = pyqtSignal(int)  # note_id

    def __init__(self, task_manager, note_manager):
        super().__init__()
        self.task_manager = task_manager
        self.note_manager = note_manager
        self.setupUi(self)

        # Настройка дополнительных параметров UI
        self.setup_additional_ui()
        self.connect_signals()
        self.load_tasks()

    def setup_additional_ui(self):
        """Дополнительная настройка UI"""
        # Настройка списка задач
        self.tasks_list.setAlternatingRowColors(True)

        # Настройка комбо-боксов
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)

    def connect_signals(self):
        """Подключение сигналов"""
        self.pushButton.clicked.connect(self.refresh)

    def load_tasks(self):
        """Загрузка и отображение задач"""
        self.tasks_list.clear()

        # Получаем задачи в зависимости от фильтра
        filter_type = self.filter_combo.currentText()

        if filter_type == "Все задачи":
            # Получаем и выполненные, и невыполненные задачи
            incomplete_tasks = self.task_manager.get_all_incomplete_tasks()

            # Получаем выполненные задачи через существующий метод или создаем временное решение
            completed_tasks = self.get_completed_tasks()
            tasks = incomplete_tasks + completed_tasks

        elif filter_type == "Только активные":
            tasks = self.task_manager.get_all_incomplete_tasks()
        elif filter_type == "Только выполненные":
            tasks = self.get_completed_tasks()
        elif filter_type == "Просроченные":
            # Временно используем пустой список
            tasks = []
        else:
            tasks = self.task_manager.get_all_incomplete_tasks()

        # Отображаем задачи
        for task in tasks:
            self.add_task_item(task)

        # Обновляем статистику
        self.update_stats(tasks)

    def get_completed_tasks(self):
        """Получает выполненные задачи через существующие методы"""
        try:
            # Получаем все задачи для всех заметок и фильтруем выполненные
            all_tasks = []

            # Получаем все заметки
            all_notes = self.note_manager.get_all()

            for note in all_notes:
                # Получаем задачи для каждой заметки
                note_tasks = self.task_manager.get_tasks_for_note(note.id)
                for task in note_tasks:
                    if task.is_completed:
                        # Добавляем информацию о заметке к задаче
                        task.note_title = note.title
                        all_tasks.append(task)

            return all_tasks

        except Exception as e:
            print(f"Ошибка при получении выполненных задач: {e}")
            return []

    def add_task_item(self, task):
        """Добавляет задачу в список"""
        # Создаем кастомный виджет для элемента списка
        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Чекбокс задачи
        checkbox = QCheckBox()
        checkbox.setChecked(task.is_completed)
        checkbox.stateChanged.connect(
            lambda state, task_id=task.id: self.on_task_toggled(task_id, state)
        )
        layout.addWidget(checkbox)

        # Описание задачи
        task_label = QLabel(task.description)
        task_label.setWordWrap(True)

        # Зачеркиваем текст если задача выполнена
        if task.is_completed:
            task_label.setStyleSheet("text-decoration: line-through; color: gray;")

        layout.addWidget(task_label)
        layout.addStretch()

        # Кнопка перехода к заметке
        if hasattr(task, 'note_id') and task.note_id:
            note_title = getattr(task, 'note_title', f"Заметка {task.note_id}")
            note_btn = QPushButton(f"📝 --> {note_title}")
            note_btn.setToolTip(f"Перейти к заметке: {note_title}")
            note_btn.setFixedSize(75, 25)
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

        # Создаем элемент списка
        list_item = QListWidgetItem(self.tasks_list)
        list_item.setSizeHint(item_widget.sizeHint())

        # Сохраняем данные задачи в элемент
        list_item.task_data = {
            'task_id': task.id,
            'is_completed': task.is_completed
        }

        self.tasks_list.addItem(list_item)
        self.tasks_list.setItemWidget(list_item, item_widget)

    def on_task_toggled(self, task_id, state):
        """Обработчик изменения чекбокса задачи"""
        is_completed = state == Qt.CheckState.Checked.value

        # Обновляем в БД
        success = self.task_manager.update_task(task_id, is_completed=is_completed)
        if success:
            self.task_toggled.emit(task_id, is_completed)
            print(f"✅ Задача {task_id} отмечена как {'выполнена' if is_completed else 'не выполнена'}")

            # Обновляем отображение
            self.refresh()

    def update_stats(self, tasks):
        """Обновление статистики"""
        total = len(tasks)
        completed = sum(1 for task in tasks if task.is_completed)
        active = total - completed

        self.total_label.setText(f"Всего: {total}")
        self.active_label.setText(f"Активные: {active}")
        self.completed_label.setText(f"Выполнено: {completed}")

    def on_filter_changed(self):
        """Обработчик изменения фильтра"""
        self.load_tasks()

    def on_sort_changed(self):
        """Обработчик изменения сортировки"""
        self.load_tasks()

    def refresh(self):
        """Обновляет список задач"""
        self.load_tasks()