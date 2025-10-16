from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QScrollArea,
                             QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from widgets.task_widget import TaskWidget


class TasksEditor(QWidget):
    """Виджет для редактирования списка задач"""

    tasks_changed = pyqtSignal()  # Сигнал об изменении задач

    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_widgets = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Заголовок
        title_label = QLabel("Задачи:")
        title_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Область прокрутки для задач
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(200)

        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(5, 5, 5, 5)
        self.tasks_layout.setSpacing(2)

        self.scroll_area.setWidget(self.tasks_container)
        layout.addWidget(self.scroll_area)

        # Кнопка добавления задачи
        self.add_task_btn = QPushButton("+ Добавить задачу")
        self.add_task_btn.clicked.connect(self.add_task)
        layout.addWidget(self.add_task_btn)

    def add_task(self, description="", is_completed=False):
        """Добавляет новую задачу"""
        task_widget = TaskWidget(description, is_completed)
        task_widget.task_changed.connect(self.on_task_changed)

        self.tasks_layout.addWidget(task_widget)
        self.task_widgets.append(task_widget)

        self.on_task_changed()
        return task_widget

    def on_task_changed(self):
        """Обработчик изменения любой задачи"""
        self.tasks_changed.emit()

    def load_tasks(self, tasks):
        """Загружает задачи в редактор"""
        # Очищаем существующие задачи
        self.clear_tasks()

        # Добавляем новые задачи
        for task in tasks:
            self.add_task(task.description, task.is_completed)

    def get_tasks(self):
        """Возвращает список задач"""
        tasks_data = []
        for widget in self.task_widgets:
            task_data = widget.get_task_data()
            if task_data['description']:  # Только непустые задачи
                tasks_data.append(task_data)
        return tasks_data

    def clear_tasks(self):
        """Очищает все задачи"""
        for widget in self.task_widgets:
            self.tasks_layout.removeWidget(widget)
            widget.deleteLater()
        self.task_widgets.clear()
