import os
import sys
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem
from PyQt6.QtCore import Qt
from src.gui.ui_main_window import Ui_MainWindow

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))
from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager


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


class MainWindow(QMainWindow, Ui_MainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_managers()
        self.setup_connections()
        self.load_notes()

        self.current_note_id = None

    def setup_managers(self):
        """Инициализация менеджеров базы данных"""
        db_path = "smart_organizer.db"
        self.db_manager = DatabaseManager(db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)

        # Обертка для списка заметок
        self.notes_list_widget = NotesListWidget(self.notes_list)

        print("Менеджеры базы данных инициализированы")

    def setup_connections(self):
        """Настройка соединений сигналов и слотов"""
        # Кнопки
        self.new_note_btn.clicked.connect(self.on_new_note)
        self.delete_note_btn.clicked.connect(self.on_delete_note)
        self.save_btn.clicked.connect(self.on_save_note)
        self.cancel_btn.clicked.connect(self.on_cancel_edit)
        self.search_button.clicked.connect(self.on_search_clicked)

        # Поиск
        self.search_input.textChanged.connect(self.on_search_changed)

        # Список заметок
        self.notes_list.currentItemChanged.connect(self.on_note_selected)

        # Редактор
        self.title_input.textChanged.connect(self.on_note_modified)
        self.content_editor.textChanged.connect(self.on_note_modified)
        self.tags_input.textChanged.connect(self.on_note_modified)

        # Меню
        self.actionNewNote.triggered.connect(self.on_new_note)
        self.actionRefresh.triggered.connect(self.load_notes)
        self.actionExit.triggered.connect(self.close)

    def load_notes(self, search_text=""):
        """Загружает заметки из базы данных"""
        try:
            if search_text:
                notes = self.note_manager.search(search_text)
            else:
                notes = self.note_manager.get_all()

            self.notes_list_widget.load_notes(notes)
            print(f"Загружено заметок: {len(notes)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заметки: {e}")

    def on_search_changed(self, text):
        """Обработчик изменения текста поиска"""
        if len(text) >= 2 or text == "":
            self.load_notes(text)

    def on_search_clicked(self):
        """Обработчик кнопки поиска"""
        self.load_notes(self.search_input.text())

    def on_note_selected(self, current, previous):
        """Обработчик выбора заметки из списка"""
        if current is None:
            return

        try:
            note_id = current.data(Qt.ItemDataRole.UserRole)
            note = self.note_manager.get(note_id)

            if note:
                self.display_note(note)
                self.current_note_id = note_id
                self.set_editor_enabled(True)
                self.save_btn.setEnabled(False)
                self.cancel_btn.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заметку: {e}")

    def display_note(self, note):
        """Отображает заметку в редакторе"""
        self.title_input.setText(note.title)
        self.content_editor.setPlainText(note.content)

        # Отображаем теги
        if note.tags:
            tags_text = ", ".join([tag.name for tag in note.tags])
            self.tags_input.setText(tags_text)
        else:
            self.tags_input.setText("")

    def set_editor_enabled(self, enabled):
        """Включает/выключает редактор"""
        self.title_input.setEnabled(enabled)
        self.tags_input.setEnabled(enabled)
        self.content_editor.setEnabled(enabled)

    def on_note_modified(self):
        """Обработчик изменения содержимого заметки"""
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

    def on_new_note(self):
        """Создание новой заметки"""
        self.set_editor_enabled(True)
        self.title_input.clear()
        self.content_editor.clear()
        self.tags_input.clear()
        self.current_note_id = None
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.title_input.setFocus()

    def on_save_note(self):
        """Сохранение заметки"""
        try:
            title = self.title_input.text().strip()
            if not title:
                QMessageBox.warning(self, "Предупреждение", "Заголовок не может быть пустым!")
                return

            content = self.content_editor.toPlainText()
            tags_text = self.tags_input.text().strip()
            tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []
            tags = [tag for tag in tags if tag]  # Убираем пустые

            if self.current_note_id:
                # Обновление существующей заметки
                success = self.note_manager.update(
                    self.current_note_id, title, content, tags
                )
                if success:
                    QMessageBox.information(self, "Успех", "Заметка обновлена!")
                    self.load_notes(self.search_input.text())
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить заметку")
            else:
                # Создание новой заметки
                note = self.note_manager.create(title, content, tags)
                if note:
                    QMessageBox.information(self, "Успех", f"Заметка создана! ID: {note.id}")
                    self.load_notes(self.search_input.text())
                    self.current_note_id = note.id
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать заметку")

            self.save_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")

    def on_cancel_edit(self):
        """Отмена редактирования"""
        if self.current_note_id:
            # Перезагружаем текущую заметку
            note = self.note_manager.get(self.current_note_id)
            if note:
                self.display_note(note)
        else:
            # Очищаем редактор для новой заметки
            self.title_input.clear()
            self.content_editor.clear()
            self.tags_input.clear()
            self.set_editor_enabled(False)

        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

    def on_delete_note(self):
        """Удаление выбранной заметки"""
        if not self.current_note_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите заметку для удаления!")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить эту заметку?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.note_manager.delete(self.current_note_id)
                if success:
                    QMessageBox.information(self, "Успех", "Заметка удалена!")
                    self.load_notes(self.search_input.text())
                    self.set_editor_enabled(False)
                    self.title_input.clear()
                    self.content_editor.clear()
                    self.tags_input.clear()
                    self.current_note_id = None
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить заметку")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")