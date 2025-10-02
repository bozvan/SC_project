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
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_managers()
        self.setup_connections()
        self.load_notes()
        self.current_note_id = None

    def setup_managers(self):
        db_path = "smart_organizer.db"
        self.db_manager = DatabaseManager(db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        print("✅ Менеджеры базы данных инициализированы")

    def setup_connections(self):
        self.new_note_btn.clicked.connect(self.on_new_note)
        self.delete_note_btn.clicked.connect(self.on_delete_note)
        self.save_btn.clicked.connect(self.on_save_note)
        self.cancel_btn.clicked.connect(self.on_cancel_edit)
        self.search_button.clicked.connect(self.on_search_clicked)

        self.search_input.textChanged.connect(self.on_search_changed)
        self.notes_list.currentItemChanged.connect(self.on_note_selected)

        self.title_input.textChanged.connect(self.on_note_modified)
        self.content_editor.textChanged.connect(self.on_note_modified)
        self.tags_input.textChanged.connect(self.on_note_modified)

        self.actionNewNote.triggered.connect(self.on_new_note)
        self.actionRefresh.triggered.connect(self.load_notes)
        self.actionExit.triggered.connect(self.close)

    def parse_search_query(self, query):
        """
        Парсит поисковый запрос и извлекает текст и теги
        Форматы:
        - "текст" - поиск по тексту
        - "#тег" - поиск по тегу
        - "текст #тег" - комбинированный поиск
        """
        if not query.strip():
            return "", []

        words = query.strip().split()
        text_parts = []
        tags = []

        for word in words:
            if word.startswith('#') and len(word) > 1:
                # Это тег - приводим к нижнему регистру для поиска
                tag_name = word[1:]  # Убираем #
                tags.append(tag_name.lower())
            else:
                # Это текст для поиска - сохраняем как есть, но поиск будет без учета регистра
                text_parts.append(word)

        search_text = " ".join(text_parts)
        return search_text, tags

    def load_notes(self, search_query=""):
        """Загружает заметки с учетом поискового запроса"""
        try:
            search_text, tags = self.parse_search_query(search_query)

            if tags and search_text:
                # Комбинированный поиск: текст + теги
                notes = self.note_manager.search_by_text_and_tags(search_text, tags)
                print(f"🔍 Комбинированный поиск: '{search_text}' + теги {tags}")
            elif tags:
                # Поиск только по тегам
                notes = self.note_manager.search_by_tags(tags)
                print(f"🏷️ Поиск по тегам: {tags}")
            elif search_text:
                # Поиск только по тексту
                notes = self.note_manager.search(search_text)
                print(f"📝 Поиск по тексту: '{search_text}'")
            else:
                # Показать все заметки
                notes = self.note_manager.get_all()
                print("📚 Показаны все заметки")

            self.display_notes(notes)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заметки: {e}")
            print(f"❌ Ошибка загрузки заметок: {e}")

    def display_notes(self, notes):
        """Отображает список заметок"""
        self.notes_list.clear()

        for note in notes:
            item = QListWidgetItem(note.title)
            item.setData(Qt.ItemDataRole.UserRole, note.id)

            # Добавляем информацию о тегах в подсказку
            if note.tags:
                tags_str = ", ".join([tag.name for tag in note.tags])
                item.setToolTip(f"Теги: {tags_str}\nСоздана: {note.created_date.strftime('%d.%m.%Y')}")
            else:
                item.setToolTip(f"Создана: {note.created_date.strftime('%d.%m.%Y')}")

            self.notes_list.addItem(item)

        print(f"✅ Отображено заметок: {len(notes)}")

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
            tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
            tags = [tag for tag in tags if tag]

            if self.current_note_id:
                success = self.note_manager.update(self.current_note_id, title, content, tags)
                if success:
                    QMessageBox.information(self, "Успех", "Заметка обновлена!")
                    self.load_notes(self.search_input.text())
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить заметку")
            else:
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
            note = self.note_manager.get(self.current_note_id)
            if note:
                self.display_note(note)
        else:
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
            self, "Подтверждение удаления", "Вы уверены, что хотите удалить эту заметку?",
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