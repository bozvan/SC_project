import os
import sys
import traceback
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QCheckBox, QLineEdit, QPushButton, QScrollArea, \
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print(f"✅ Python path: {sys.path}")
print(f"✅ Current directory: {os.getcwd()}")

try:
    from src.gui.ui_main_window import Ui_MainWindow
    from src.core.database_manager import DatabaseManager
    from src.core.tag_manager import TagManager
    from src.core.note_manager import NoteManager
    from src.widgets.rich_text_editor import RichTextEditor
    from src.widgets.tags_widget import TagsWidget
    print("✅ Все модули успешно импортированы")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    traceback.print_exc()
    sys.exit(1)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # ВАЖНО: Инициализируем все атрибуты ПЕРЕД использованием
        self.current_note_id = None
        self._updating_from_search = False
        self._updating_from_tags = False

        self.setup_managers()
        self.setup_ui_simple()
        self.setup_connections()

        # Таймер для автосохранения
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.auto_save_note)

        # Инициализируем TaskManager
        from src.core.task_manager import TaskManager
        self.task_manager = TaskManager(self.db_manager)

        self.load_notes()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        print("🔴 Закрытие приложения...")

        # Останавливаем таймеры
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        # Закрываем соединения с БД
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            print("✅ Соединение с БД закрыто")

        # Принудительно завершаем
        QApplication.instance().quit()

        event.accept()
        print("✅ Приложение завершено корректно")

    def setup_managers(self):
        db_path = "smart_organizer.db"
        self.db_manager = DatabaseManager(db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        print("✅ Менеджеры базы данных инициализированы")

    def setup_ui_simple(self):
        """Настройка UI с областью задач"""
        self.setup_rich_editor()

        # Создаем область задач
        self.setup_tasks_area()

        self.tags_widget = TagsWidget(self.tag_manager)
        self.tags_widget.tag_selected.connect(self.on_tag_selected_from_widget)
        self.verticalLayout.addWidget(self.tags_widget)

        # Скрываем кнопку "Отменить"
        self.cancel_btn.setVisible(False)

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
        self.tasks_scroll.setMaximumHeight(200)

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
        """Добавляет виджет задачи"""
        task_widget = QWidget()
        layout = QHBoxLayout(task_widget)
        layout.setContentsMargins(5, 2, 5, 2)

        checkbox = QCheckBox(task.description)
        checkbox.setChecked(task.is_completed)
        checkbox.stateChanged.connect(
            lambda state, task_id=task.id: self.on_task_toggled(task_id, state)
        )

        layout.addWidget(checkbox)
        layout.addStretch()

        # Кнопка удаления
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("font-weight: bold; color: red;")
        delete_btn.clicked.connect(
            lambda checked, task_id=task.id, widget=task_widget: self.delete_task(task_id, widget)
        )
        layout.addWidget(delete_btn)

        self.tasks_layout.addWidget(task_widget)

    def on_task_toggled(self, task_id, state):
        """Обработчик переключения чекбокса"""
        is_checked = state == Qt.CheckState.Checked.value
        success = self.task_manager.update_task(task_id, is_completed=is_checked)
        if success:
            print(f"✅ Статус задачи {task_id} обновлен: {is_checked}")
        self.on_note_modified()

    def delete_task(self, task_id, widget):
        """Удаляет задачу"""
        success = self.task_manager.delete_task(task_id)
        if success:
            self.tasks_layout.removeWidget(widget)
            widget.deleteLater()
            self.on_note_modified()

    def load_tasks_for_note(self, note_id):
        """Загружает задачи для заметки"""
        # Очищаем старые задачи
        for i in reversed(range(self.tasks_layout.count())):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                self.tasks_layout.removeWidget(widget)
                widget.deleteLater()

        if not note_id:
            return

        # Загружаем новые задачи
        tasks = self.task_manager.get_tasks_for_note(note_id)
        for task in tasks:
            self.add_task_widget(task)

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
        self.search_button.clicked.connect(self.on_search_clicked)

        self.notes_list.currentItemChanged.connect(self.on_note_selected)

        # Подключаем автосохранение при изменениях
        self.title_input.textChanged.connect(self.schedule_auto_save)
        self.rich_editor.text_edit.textChanged.connect(self.schedule_auto_save)
        self.tags_input.textChanged.connect(self.schedule_auto_save)

        self.actionNewNote.triggered.connect(self.on_new_note)
        self.actionRefresh.triggered.connect(self.load_notes)
        self.actionExit.triggered.connect(self.close)

    def schedule_auto_save(self):
        """Планирует автосохранение через 3 секунды после последнего изменения"""
        # Добавьте проверку на существование атрибута
        if hasattr(self, 'current_note_id') and self.current_note_id:
            self.auto_save_timer.start(1000)  # 3 секунды
            self.save_btn.setEnabled(True)

    def auto_save_note(self):
        """Автоматически сохраняет заметку"""
        # Добавьте проверку на существование атрибута
        if not hasattr(self, 'current_note_id') or not self.current_note_id:
            return

        try:
            title = self.title_input.text().strip()
            if not title:
                return  # Не сохраняем заметки без заголовка

            content = self.rich_editor.to_html()
            tags_text = self.tags_input.text().strip()
            tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
            tags = [tag for tag in tags if tag]

            success = self.note_manager.update(self.current_note_id, title, content, tags, "html")
            if success:
                print(f"✅ Автосохранение заметки {self.current_note_id}")
                self.save_btn.setEnabled(False)
            else:
                print(f"❌ Ошибка автосохранения заметки {self.current_note_id}")

        except Exception as e:
            print(f"❌ Ошибка при автосохранении: {e}")

    def load_notes(self, search_query=""):
        """Загружает заметки с учетом поискового запроса"""
        try:
            search_text, tags = self.parse_search_query(search_query)

            if tags and search_text:
                notes = self.note_manager.search_by_text_and_tags(search_text, tags)
            elif tags:
                notes = self.note_manager.search_by_tags(tags)
            elif search_text:
                notes = self.note_manager.search(search_text)
            else:
                notes = self.note_manager.get_all()
                print("📚 Показаны все заметки")

            self.display_notes(notes)

        except Exception as e:
            print(f"❌ Ошибка загрузки заметок: {e}")

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

        # Автоматически выбираем первую заметку если есть заметки
        if notes and self.notes_list.count() > 0:
            self.notes_list.setCurrentRow(0)

    def on_note_selected(self, current, previous):
        """Обработчик выбора заметки"""
        # Останавливаем таймер автосохранения при переключении
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        if current is None:
            return

        try:
            note_id = current.data(Qt.ItemDataRole.UserRole)
            note = self.note_manager.get(note_id)
            if note:
                self.display_note(note)
                self.current_note_id = note_id  # Устанавливаем ID
                self.set_editor_enabled(True)
                self.save_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заметку: {e}")

    def display_note(self, note):
        """Отображает заметку и её задачи"""
        self.title_input.setText(note.title)
        self.rich_editor.set_html(note.content)

        # Загружаем задачи
        if note.id:
            self.load_tasks_for_note(note.id)

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
        """Обработчик изменения заметки"""
        self.save_btn.setEnabled(True)
        # Для автосохранения существующих заметок
        if self.current_note_id:
            self.schedule_auto_save()

    def on_new_note(self):
        """Создание новой заметки"""
        # Останавливаем автосохранение
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        self.set_editor_enabled(True)
        self.title_input.clear()
        self.rich_editor.clear()
        self.tags_input.clear()

        # Очищаем задачи
        if hasattr(self, 'tasks_layout'):
            for i in reversed(range(self.tasks_layout.count())):
                widget = self.tasks_layout.itemAt(i).widget()
                if widget:
                    self.tasks_layout.removeWidget(widget)
                    widget.deleteLater()

        self.current_note_id = None  # Сбрасываем ID для новой заметки
        self.save_btn.setEnabled(True)
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
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")

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

    def on_search_clicked(self):
        query = self.search_input.text()
        self.load_notes(query)

    def on_tag_selected_from_widget(self, tag_name):
        if self._updating_from_search:
            return

        print(f"🏷️ Фильтр по тегу из виджета: '{tag_name}'")
        self._updating_from_tags = True

        try:
            if tag_name:
                self.search_input.setText(f"#{tag_name}")
                self.load_notes(f"#{tag_name}")
            else:
                self.search_input.clear()
                self.load_notes("")
        finally:
            self._updating_from_tags = False

    def sync_tags_selection(self, search_query):
        if self._updating_from_tags:
            return

        self._updating_from_search = True
        try:
            search_text, tags = self.parse_search_query(search_query)

            if len(tags) == 1:
                self.tags_widget.select_tag_by_name(tags[0])
            else:
                self.tags_widget.clear_selection()
        finally:
            self._updating_from_search = False
# [file content end]