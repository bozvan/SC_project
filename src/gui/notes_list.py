from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidgetItem


class NotesListWidget:


    """Обертка для QListWidget с дополнительной функциональностью"""

    def __init__(self, list_widget):
        self.list_widget = list_widget

    def load_notes(self, notes):
        """Загружает заметки в список"""
        self.list_widget.clear()

        for note in notes:
            item = QListWidgetItem(note.title)
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            self.list_widget.addItem(item)