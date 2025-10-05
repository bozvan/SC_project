from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QLabel, QFrame)
from PyQt6.QtCore import pyqtSignal
from src.widgets.rich_text_editor import RichTextEditor


class NoteEditor(QWidget):
    """Виджет для редактирования заметки"""

    # Сигналы
    content_changed = pyqtSignal()
    title_changed = pyqtSignal()
    tags_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_note_id = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        title_layout = QHBoxLayout()
        title_label = QLabel("Заголовок:")
        self.title_input = QLineEdit()
        self.title_input.textChanged.connect(self.title_changed)

        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # Теги
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Теги:")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("тег1, тег2, тег3")
        self.tags_input.textChanged.connect(self.tags_changed)

        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.tags_input)
        layout.addLayout(tags_layout)

        # Контент
        content_label = QLabel("Содержимое:")
        layout.addWidget(content_label)

        self.rich_editor = RichTextEditor()
        self.rich_editor.text_edit.textChanged.connect(self.content_changed)
        layout.addWidget(self.rich_editor)

    def load_note(self, note):
        """Загружает заметку в редактор"""
        self.current_note_id = note.id
        self.title_input.setText(note.title)
        self.rich_editor.set_html(note.content)

        if note.tags:
            tags_text = ", ".join([tag.name for tag in note.tags])
            self.tags_input.setText(tags_text)
        else:
            self.tags_input.clear()

    def clear(self):
        """Очищает редактор"""
        self.current_note_id = None
        self.title_input.clear()
        self.rich_editor.clear()
        self.tags_input.clear()

    def get_note_data(self):
        """Возвращает данные из редактора"""
        return {
            'title': self.title_input.text().strip(),
            'content': self.rich_editor.to_html(),
            'tags_text': self.tags_input.text().strip()
        }

    def get_tags_list(self):
        """Возвращает список тегов"""
        tags_text = self.tags_input.text().strip()
        if tags_text:
            return [tag.strip().lower() for tag in tags_text.split(",") if tag.strip()]
        return []
