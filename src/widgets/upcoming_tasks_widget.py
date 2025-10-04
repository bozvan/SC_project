from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLabel, QCheckBox, QHBoxLayout, QPushButton, QMenu,
                             QMessageBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction


class UpcomingTasksWidget(QWidget):
    """Виджет для отображения предстоящих задач из ВСЕХ заметок в боковой панели"""

    task_toggled = pyqtSignal(int, bool)  # task_id, is_completed
    navigate_to_note = pyqtSignal(int)  # note_id

    def __init__(self, task_manager, note_manager):
        super().__init__()
        self.task_manager = task_manager
        self.note_manager = note_manager
        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        """Настройка интерфейса виджета"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Заголовок
        title_label = QLabel("Предстоящие задачи")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Область прокрутки для задач
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(400)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Контейнер для задач
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(2, 2, 2, 2)
        self.tasks_layout.setSpacing(3)

        self.scroll_area.setWidget(self.tasks_container)
        layout.addWidget(self.scroll_area)

        # Статистика
        self.stats_label = QLabel("Невыполненных задач: 0")
        self.stats_label.setStyleSheet("color: white; font-size: 11px; margin-top: 5px;")
        layout.addWidget(self.stats_label)

    def load_tasks(self):
        """Загрузка и отображение невыполненных задач из всех заметок"""
        # Очищаем старые задачи
        for i in reversed(range(self.tasks_layout.count())):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                self.tasks_layout.removeWidget(widget)
                widget.deleteLater()

        # Загружаем все невыполненные задачи
        tasks = self.task_manager.get_all_incomplete_tasks()

        if not tasks:
            # Показываем сообщение если задач нет
            no_tasks_label = QLabel("Нет предстоящих задач")
            no_tasks_label.setStyleSheet("color: palette(mid); font-style: italic; padding: 10px;")
            no_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tasks_layout.addWidget(no_tasks_label)
        else:
            # Отображаем задачи как чекбоксы
            for task in tasks:
                self.add_task_widget(task)

        # Обновляем статистику
        self.stats_label.setText(f"Невыполненных задач: {len(tasks)}")
        print(f"✅ Загружено предстоящих задач: {len(tasks)}")

    def add_task_widget(self, task):
        """Добавляет виджет задачи с чекбоксом"""
        task_widget = QFrame()
        task_widget.setFrameStyle(QFrame.Shape.Box)
        task_widget.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 3px;
                padding: 0px;
            }
            QFrame:hover {
                background-color: palette(alternate-base);
                border: 1px solid palette(highlight);
            }
        """)

        layout = QHBoxLayout(task_widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

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
        task_label.setStyleSheet("font-size: 11px;")

        # Зачеркиваем текст если задача выполнена
        if task.is_completed:
            task_label.setStyleSheet("font-size: 11px; text-decoration: line-through; color: gray;")

        layout.addWidget(task_label)
        layout.addStretch()

        # Информация о заметке (кликабельная)
        if task.note_title:
            note_btn = QPushButton("📝")
            note_btn.setToolTip(f"Перейти к заметке: {task.note_title}")
            note_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 12px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: palette(highlight);
                    border-radius: 2px;
                }
            """)
            note_btn.setFixedSize(20, 20)
            note_btn.clicked.connect(
                lambda checked, note_id=task.note_id: self.navigate_to_note.emit(note_id)
            )
            layout.addWidget(note_btn)

        # Сохраняем данные задачи
        task_widget.task_data = {
            'task_id': task.id,
            'note_id': task.note_id,
            'description': task.description,
            'is_completed': task.is_completed,
            'checkbox': checkbox,
            'label': task_label
        }

        self.tasks_layout.addWidget(task_widget)

    def on_task_toggled(self, task_id, state):
        """Обработчик изменения чекбокса задачи"""
        is_completed = state == Qt.CheckState.Checked.value

        # Обновляем в БД
        success = self.task_manager.update_task(task_id, is_completed=is_completed)
        if success:
            # Обновляем отображение этой задачи
            self.update_task_display(task_id, is_completed)
            self.task_toggled.emit(task_id, is_completed)
            print(f"✅ Задача {task_id} отмечена как {'выполнена' if is_completed else 'не выполнена'}")

            # Через 0.5 секунды обновляем весь список (чтобы выполненные задачи исчезли)
            if is_completed:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, self.load_tasks)

    def update_task_display(self, task_id, is_completed):
        """Обновляет отображение конкретной задачи"""
        # Ищем виджет с этой задачей
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if (hasattr(widget, 'task_data') and
                    widget.task_data['task_id'] == task_id):

                # Обновляем стиль текста
                if is_completed:
                    widget.task_data['label'].setStyleSheet(
                        "font-size: 11px; text-decoration: line-through; color: gray;"
                    )
                else:
                    widget.task_data['label'].setStyleSheet("font-size: 11px;")

                break

    def show_context_menu(self, position):
        """Показывает контекстное меню для задачи"""
        # Находим виджет под курсором
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if (widget and
                    hasattr(widget, 'task_data') and
                    widget.underMouse()):

                task_data = widget.task_data
                menu = QMenu(self)

                # Действие для перехода к заметке
                if task_data['note_id']:
                    goto_note_action = QAction("Перейти к заметке", self)
                    goto_note_action.triggered.connect(
                        lambda: self.navigate_to_note.emit(task_data['note_id'])
                    )
                    menu.addAction(goto_note_action)
                    menu.addSeparator()

                # Действия в зависимости от статуса задачи
                if task_data['is_completed']:
                    mark_incomplete_action = QAction("Отметить как невыполненную", self)
                    mark_incomplete_action.triggered.connect(
                        lambda: self.toggle_task(task_data['task_id'], False)
                    )
                    menu.addAction(mark_incomplete_action)
                else:
                    mark_complete_action = QAction("Отметить как выполненную", self)
                    mark_complete_action.triggered.connect(
                        lambda: self.toggle_task(task_data['task_id'], True)
                    )
                    menu.addAction(mark_complete_action)

                menu.exec(self.mapToGlobal(position))
                break

    def toggle_task(self, task_id, is_completed):
        """Переключает статус задачи"""
        success = self.task_manager.update_task(task_id, is_completed=is_completed)
        if success:
            # Находим и обновляем чекбокс
            for i in range(self.tasks_layout.count()):
                widget = self.tasks_layout.itemAt(i).widget()
                if (hasattr(widget, 'task_data') and
                        widget.task_data['task_id'] == task_id):

                    widget.task_data['checkbox'].setChecked(is_completed)
                    self.update_task_display(task_id, is_completed)
                    self.task_toggled.emit(task_id, is_completed)

                    # Обновляем список если задача выполнена
                    if is_completed:
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(500, self.load_tasks)
                    break

    def refresh(self):
        """Обновляет список задач"""
        self.load_tasks()

    def mousePressEvent(self, event):
        """Обработчик клика по виджету для контекстного меню"""
        if event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.pos())
        else:
            super().mousePressEvent(event)
