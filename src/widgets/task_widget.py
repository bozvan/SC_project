from PyQt6.QtWidgets import QWidget, QCheckBox, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal


class TaskWidget(QWidget):
    """Виджет одной задачи с чекбоксом"""

    task_toggled = pyqtSignal(str, bool)  # description, is_checked
    task_changed = pyqtSignal()  # Сигнал об изменении задачи

    def __init__(self, description="", is_completed=False, parent=None):
        super().__init__(parent)
        self.description = description

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(5)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(is_completed)
        self.checkbox.stateChanged.connect(self.on_checkbox_toggled)

        self.text_input = QLineEdit()
        self.text_input.setText(description)
        self.text_input.setPlaceholderText("Введите описание задачи...")
        self.text_input.textChanged.connect(self.on_text_changed)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_input)

        self.update_style()

    def on_checkbox_toggled(self, state):
        """Обработчик изменения чекбокса"""
        is_checked = state == Qt.CheckState.Checked.value
        self.task_toggled.emit(self.description, is_checked)
        self.update_style()
        self.task_changed.emit()


    def on_text_changed(self):
        """Обработчик изменения текста"""
        self.description = self.text_input.text()
        self.task_changed.emit()

    def update_style(self):
        """Обновляет стиль в зависимости от статуса"""
        if self.checkbox.isChecked():
            self.text_input.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            self.text_input.setStyleSheet("")

    def get_task_data(self):
        """Возвращает данные задачи"""
        return {
            'description': self.description.strip(),
            'is_completed': self.checkbox.isChecked()
        }
