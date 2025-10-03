import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QMessageBox, QListWidgetItem,
                             QVBoxLayout, QHBoxLayout, QCheckBox, QLineEdit,
                             QPushButton, QScrollArea, QWidget, QLabel)
from PyQt6.QtCore import Qt

from src.core.task_manager import TaskManager
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
        self.setup_ui_with_tasks()  # ИЗМЕНИЛ НАЗВАНИЕ
        self.setup_connections()

        self._updating_from_search = False
        self._updating_from_tags = False
        self.task_manager = TaskManager(self.db_manager)

        self.load_notes()
        self.current_note_id = None

    def setup_ui_with_tasks(self):
        """Настройка UI с областью задач"""
        self.setup_rich_editor()

        # Создаем область задач
        self.setup_tasks_area()

        self.tags_widget = TagsWidget(self.tag_manager)
        self.tags_widget.tag_selected.connect(self.on_tag_selected_from_widget)
        self.verticalLayout.addWidget(self.tags_widget)

        print("✅ UI настроен с областью задач")

    def setup_tasks_area(self):
        """Создает область для задач под редактором"""
        # Создаем контейнер для задач
        self.tasks_container = QWidget()
        tasks_layout = QVBoxLayout(self.tasks_container)
        tasks_layout.setContentsMargins(0, 10, 0, 0)

        # Заголовок
        tasks_label = QLabel("Задачи этой заметки:")
        tasks_label.setStyleSheet("font-weight: bold;")
        tasks_layout.addWidget(tasks_label)

        # Область прокрутки для задач
        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setMaximumHeight(150)

        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setSpacing(5)

        self.tasks_scroll.setWidget(self.tasks_widget)
        tasks_layout.addWidget(self.tasks_scroll)

        # Кнопка добавления задачи
        add_task_layout = QHBoxLayout()
        self.new_task_input = QLineEdit()
        self.new_task_input.setPlaceholderText("Новая задача...")
        self.new_task_input.returnPressed.connect(self.add_task)

        self.add_task_btn = QPushButton("Добавить")
        self.add_task_btn.clicked.connect(self.add_task)

        add_task_layout.addWidget(self.new_task_input)
        add_task_layout.addWidget(self.add_task_btn)
        tasks_layout.addLayout(add_task_layout)

        # Добавляем контейнер задач в основной layout
        self.verticalLayout_2.addWidget(self.tasks_container)

    def add_task(self):
        """Добавляет новую задачу"""
        if not self.current_note_id:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте или откройте заметку!")
            return

        description = self.new_task_input.text().strip()
        if not description:
            return

        # Создаем задачу в БД
        task = self.task_manager.create_task(self.current_note_id, description)
        if task:
            self.add_task_widget(task)
            self.new_task_input.clear()
            self.on_note_modified()

    def add_task_widget(self, task):
        """Добавляет виджет задачи с правильным статусом"""
        task_widget = QWidget()
        task_widget.setObjectName(f"task_widget_{task.id}")  # УНИКАЛЬНЫЙ ID

        layout = QHBoxLayout(task_widget)
        layout.setContentsMargins(5, 2, 5, 2)

        checkbox = QCheckBox(task.description)
        checkbox.setChecked(task.is_completed)
        checkbox.setObjectName(f"task_checkbox_{task.id}")  # УНИКАЛЬНЫЙ ID

        # Сохраняем task.id в свойствах чекбокса
        checkbox.setProperty("task_id", task.id)

        checkbox.stateChanged.connect(
            lambda state, task_id=task.id: self.on_task_toggled(task_id, state)
        )

        layout.addWidget(checkbox)
        layout.addStretch()

        # Кнопка удаления
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("font-weight: bold; color: red;")
        delete_btn.setProperty("task_id", task.id)
        delete_btn.clicked.connect(
            lambda checked, task_id=task.id, widget=task_widget: self.delete_task(task_id, widget)
        )
        layout.addWidget(delete_btn)

        self.tasks_layout.addWidget(task_widget)

        print(f"   ✅ Добавлен виджет для задачи {task.id}: '{task.description}' -> {task.is_completed}")

    def on_task_toggled(self, task_id, state):
        """Обработчик переключения чекбокса"""
        is_checked = state == Qt.CheckState.Checked.value
        print(f"🔄 Переключение задачи {task_id}: {is_checked}")

        success = self.task_manager.update_task(task_id, is_completed=is_checked)
        if success:
            print(f"✅ Статус задачи {task_id} обновлен в БД: {is_checked}")
        else:
            print(f"❌ Ошибка обновления статуса задачи {task_id}")

        self.on_note_modified()

    def delete_task(self, task_id, widget):
        """Удаляет задачу"""
        print(f"🗑️ Удаление задачи {task_id}")
        success = self.task_manager.delete_task(task_id)
        if success:
            self.tasks_layout.removeWidget(widget)
            widget.deleteLater()
            self.on_note_modified()
            print(f"✅ Задача {task_id} удалена")
        else:
            print(f"❌ Ошибка удаления задачи {task_id}")

    def load_tasks_for_note(self, note_id):
        """Загружает задачи для заметки и отображает их с правильными статусами"""
        # Очищаем старые задачи
        self.clear_tasks()

        if not note_id:
            return

        # ОТЛАДКА: смотрим сырые данные из БД
        self.task_manager.debug_tasks_for_note(note_id)

        # Загружаем новые задачи
        tasks = self.task_manager.get_tasks_for_note(note_id)
        print(f"🔍 Загружено задач для заметки {note_id}: {len(tasks)}")

        for task in tasks:
            self.add_task_widget(task)

    def clear_tasks(self):
        """Очищает все задачи из области"""
        print("🧹 Очистка области задач")
        for i in reversed(range(self.tasks_layout.count())):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                self.tasks_layout.removeWidget(widget)
                widget.deleteLater()

    def display_note(self, note):
        """Отображает заметку и её задачи"""
        print(f"📝 Отображение заметки {note.id if note else 'None'}")

        self.title_input.setText(note.title)
        self.rich_editor.set_html(note.content)

        # Загружаем задачи
        if note and note.id:
            self.load_tasks_for_note(note.id)
        else:
            self.clear_tasks()

        if note.tags:
            tags_text = ", ".join([tag.name for tag in note.tags])
            self.tags_input.setText(tags_text)
        else:
            self.tags_input.setText("")

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

    def set_editor_enabled(self, enabled):
        self.title_input.setEnabled(enabled)
        self.tags_input.setEnabled(enabled)
        self.rich_editor.setEnabled(enabled)

    def on_note_modified(self):
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

    def on_save_note(self):
        """Сохраняет заметку"""
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
                    # Задачи уже сохраняются сразу при переключении чекбоксов
                    QMessageBox.information(self, "Успех", "Заметка обновлена!")
                    self.tags_widget.refresh()
                    self.load_notes(self.search_input.text())
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить заметку")
            else:
                note = self.note_manager.create(title, content, tags, "html")
                if note:
                    self.current_note_id = note.id
                    QMessageBox.information(self, "Успех", f"Заметка создана! ID: {note.id}")
                    self.tags_widget.refresh()
                    self.load_notes(self.search_input.text())
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать заметку")

            self.save_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")

    def on_new_note(self):
        """Создание новой заметки"""
        self.set_editor_enabled(True)
        self.title_input.clear()
        self.rich_editor.clear()
        self.tags_input.clear()
        self.clear_tasks()
        self.current_note_id = None
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.title_input.setFocus()

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