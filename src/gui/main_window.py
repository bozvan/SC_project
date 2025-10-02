import os
import sys
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QHBoxLayout, QSplitter, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from src.gui.ui_main_window import Ui_MainWindow

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))
from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager
from src.widgets.rich_text_editor import RichTextEditor
from src.widgets.tags_widget import TagsWidget


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_managers()
        self.setup_ui_simple()
        self.setup_connections()

        # Флаги для предотвращения рекурсии
        self._updating_from_search = False
        self._updating_from_tags = False

        self.load_notes()
        self.current_note_id = None

    def setup_managers(self):
        db_path = "smart_organizer.db"
        self.db_manager = DatabaseManager(db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        print("✅ Менеджеры базы данных инициализированы")

    def setup_ui_simple(self):
        """Упрощенная настройка UI"""
        self.setup_rich_editor()
        self.tags_widget = TagsWidget(self.tag_manager)
        self.tags_widget.tag_selected.connect(self.on_tag_selected_from_widget)
        self.verticalLayout.addWidget(self.tags_widget)
        print("✅ UI настроен упрощенно")

    def setup_rich_editor(self):
        """Замена стандартного QTextEdit на наш RichTextEditor"""
        old_editor = self.content_editor
        self.verticalLayout_2.removeWidget(old_editor)
        old_editor.deleteLater()
        self.rich_editor = RichTextEditor()
        self.content_editor = self.rich_editor.get_text_edit()
        self.verticalLayout_2.insertWidget(3, self.rich_editor)
        print("✅ Богатый текстовый редактор установлен")

    def setup_connections(self):
        """Настройка соединений"""
        self.new_note_btn.clicked.connect(self.on_new_note)
        self.delete_note_btn.clicked.connect(self.on_delete_note)
        self.save_btn.clicked.connect(self.on_save_note)
        self.cancel_btn.clicked.connect(self.on_cancel_edit)
        self.search_button.clicked.connect(self.on_search_clicked)

        # Отключаем автоматическое обновление при вводе чтобы избежать рекурсии
        # self.search_input.textChanged.connect(self.on_search_changed)

        self.notes_list.currentItemChanged.connect(self.on_note_selected)

        self.title_input.textChanged.connect(self.on_note_modified)
        self.rich_editor.text_edit.textChanged.connect(self.on_note_modified)
        self.tags_input.textChanged.connect(self.on_note_modified)

        self.actionNewNote.triggered.connect(self.on_new_note)
        self.actionRefresh.triggered.connect(self.load_notes)
        self.actionExit.triggered.connect(self.close)

    def on_tag_selected_from_widget(self, tag_name):
        """Обработчик выбора тега из виджета"""
        if self._updating_from_search:
            return

        print(f"🏷️ Фильтр по тегу из виджета: '{tag_name}'")
        self._updating_from_tags = True

        try:
            if tag_name:
                # Устанавливаем поисковый запрос БЕЗ вызова load_notes
                self.search_input.setText(f"#{tag_name}")
                # Загружаем заметки по тегу
                self.load_notes_with_tag(tag_name)
            else:
                # Сбрасываем фильтр
                self.search_input.clear()
                self.load_notes_with_tag("")
        finally:
            self._updating_from_tags = False

    def load_notes_with_tag(self, tag_name):
        """Загружает заметки с фильтром по тегу"""
        if tag_name:
            notes = self.note_manager.search_by_tags([tag_name])
            print(f"🏷️ Заметки с тегом '{tag_name}': {len(notes)}")
        else:
            notes = self.note_manager.get_all()
            print("📚 Все заметки")

        self.display_notes(notes)

    def parse_search_query(self, query):
        """Парсит поисковый запрос"""
        if not query.strip():
            return "", []

        words = query.strip().split()
        text_parts = []
        tags = []

        for word in words:
            if word.startswith('#') and len(word) > 1:
                tag_name = word[1:]
                tags.append(tag_name.lower())
            else:
                text_parts.append(word)

        search_text = " ".join(text_parts)
        return search_text, tags

    def load_notes(self, search_query=""):
        """Загружает заметки с учетом поискового запроса"""
        if self._updating_from_tags:
            return

        try:
            search_text, tags = self.parse_search_query(search_query)

            if tags and search_text:
                notes = self.note_manager.search_by_text_and_tags(search_text, tags)
                print(f"🔍 Комбинированный поиск: '{search_text}' + теги {tags}")
            elif tags:
                notes = self.note_manager.search_by_tags(tags)
                print(f"🏷️ Поиск по тегам: {tags}")
            elif search_text:
                notes = self.note_manager.search(search_text)
                print(f"📝 Поиск по тексту: '{search_text}'")
            else:
                notes = self.note_manager.get_all()
                print("📚 Показаны все заметки")

            self.display_notes(notes)

            # Синхронизируем выделение тегов после загрузки
            self.sync_tags_selection(search_query)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заметки: {e}")
            print(f"❌ Ошибка загрузки заметок: {e}")

    def sync_tags_selection(self, search_query):
        """Синхронизирует выделение тегов с поисковым запросом"""
        if self._updating_from_tags:
            return

        self._updating_from_search = True
        try:
            search_text, tags = self.parse_search_query(search_query)

            if len(tags) == 1:
                # Выделяем соответствующий тег
                self.tags_widget.select_tag_by_name(tags[0])
            else:
                # Сбрасываем выделение
                self.tags_widget.clear_selection()
        finally:
            self._updating_from_search = False

    def display_notes(self, notes):
        """Отображает список заметок"""
        self.notes_list.clear()
        for note in notes:
            item = QListWidgetItem(note.title)
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            tooltip_parts = []
            if note.tags:
                tags_str = ", ".join([tag.name for tag in note.tags])
                tooltip_parts.append(f"Теги: {tags_str}")
            tooltip_parts.append(f"Создана: {note.created_date.strftime('%d.%m.%Y')}")
            item.setToolTip("\n".join(tooltip_parts))
            self.notes_list.addItem(item)
        print(f"✅ Отображено заметок: {len(notes)}")

    def on_search_clicked(self):
        """Обработчик кнопки поиска"""
        query = self.search_input.text()
        self.load_notes(query)

    # Остальные методы без изменений...
    def on_note_selected(self, current, previous):
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
        self.title_input.setText(note.title)
        self.rich_editor.set_html(note.content)
        if note.tags:
            tags_text = ", ".join([tag.name for tag in note.tags])
            self.tags_input.setText(tags_text)
        else:
            self.tags_input.setText("")

    def set_editor_enabled(self, enabled):
        self.title_input.setEnabled(enabled)
        self.tags_input.setEnabled(enabled)
        self.rich_editor.setEnabled(enabled)

    def on_note_modified(self):
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

    def on_new_note(self):
        self.set_editor_enabled(True)
        self.title_input.clear()
        self.rich_editor.clear()
        self.tags_input.clear()
        self.current_note_id = None
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.title_input.setFocus()

    def on_save_note(self):
        try:
            title = self.title_input.text().strip()
            if not title:
                QMessageBox.warning(self, "Предупреждение", "Заголовок не может быть пустым!")
                return

            content = self.rich_editor.to_html()
            tags_text = self.tags_input.text().strip()
            tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
            tags = [tag for tag in tags if tag]

            if self.current_note_id:
                success = self.note_manager.update(self.current_note_id, title, content, tags, "html")
                if success:
                    QMessageBox.information(self, "Успех", "Заметка обновлена!")
                    self.tags_widget.refresh()
                    self.load_notes(self.search_input.text())
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить заметку")
            else:
                note = self.note_manager.create(title, content, tags, "html")
                if note:
                    QMessageBox.information(self, "Успех", f"Заметка создана! ID: {note.id}")
                    self.tags_widget.refresh()
                    self.load_notes(self.search_input.text())
                    self.current_note_id = note.id
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать заметку")

            self.save_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")

    def on_cancel_edit(self):
        if self.current_note_id:
            note = self.note_manager.get(self.current_note_id)
            if note:
                self.display_note(note)
        else:
            self.title_input.clear()
            self.rich_editor.clear()
            self.tags_input.clear()
            self.set_editor_enabled(False)
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

    def on_delete_note(self):
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
                    self.tags_widget.refresh()
                    self.load_notes(self.search_input.text())
                    self.set_editor_enabled(False)
                    self.title_input.clear()
                    self.rich_editor.clear()
                    self.tags_input.clear()
                    self.current_note_id = None
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить заметку")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")