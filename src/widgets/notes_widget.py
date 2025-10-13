import os
import sys
import traceback
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QCheckBox, QLineEdit, QPushButton, QScrollArea, \
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication

from src.gui.ui_notes_page import Ui_NotesPage

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from src.gui.ui_main_window import Ui_MainWindow
    from src.core.database_manager import DatabaseManager
    from src.core.task_manager import TaskManager
    from src.core.tag_manager import TagManager
    from src.core.note_manager import NoteManager
    from src.widgets.rich_text_editor import RichTextEditor
    from src.gui.note_editor import NoteEditor
    print("✅ Все модули успешно импортированы")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    traceback.print_exc()
    sys.exit(1)


class NotesWidget(QtWidgets.QWidget, Ui_NotesPage):
    def __init__(self):
        super().__init__()
        self.tasks_layout = None
        self.tasks_widget = None
        self.tasks_scroll = None
        self.tasks_container = None
        self.add_task_btn = None
        self.new_task_input = None
        self.bookmark_manager = None
        self.task_manager = None
        self.note_manager = None
        self.tag_manager = None
        self.db_manager = None
        self.setupUi(self)

        # ИНИЦИАЛИЗИРУЙТЕ ВСЕ АТРИБУТЫ ПЕРВЫМ ДЕЛОМ
        self.current_note_id = None
        self._updating_from_search = False
        self._updating_from_tags = False

        self.setup_managers()  # ДОЛЖНО БЫТЬ ДО setup_ui_simple()
        self.setup_ui_simple()
        self.setup_connections()

        # Таймер для автосохранения
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.auto_save_note)

        self.load_notes()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        print("🔴 Закрытие приложения...")

        # Автосохранение при закрытии
        if (hasattr(self, 'current_note_id') and
                self.current_note_id):
            self.force_auto_save()

        # Останавливаем таймеры
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        # Закрываем соединения с БД
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            print("✅ Соединение с БД закрыто")

        event.accept()
        print("✅ Приложение завершено корректно")

    def setup_managers(self):
        db_path = "smart_organizer.db"
        self.db_manager = DatabaseManager(db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        self.task_manager = TaskManager(self.db_manager)
        print("✅ Все менеджеры инициализированы")

    def setup_ui_simple(self):
        """Настройка UI с отдельными разделами для задач и закладок"""
        self.setup_rich_editor()
        self.setup_tasks_area()

        self.save_btn.setVisible(True)
        self.save_btn.setEnabled(False)  # Изначально выключена
        self.save_btn.clicked.connect(self.on_save_clicked)

        # self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)

        print("✅ UI настроен с отдельными разделами для задач и закладок")

    def on_save_clicked(self):
        """Обработчик нажатия кнопки Сохранить"""
        try:
            # Определяем что сохраняем - заметку или закладку
            if hasattr(self, 'current_note_id') and self.current_note_id:
                self.save_note()
            elif hasattr(self, 'current_bookmark_id') and self.current_bookmark_id:
                self.save_bookmark()
            else:
                self.save_new_note()  # Новая заметка
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")

    def save_note(self):
        """Сохраняет существующую заметку"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Предупреждение", "Заголовок не может быть пустым!")
            return

        content = self.rich_editor.to_html()
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
        tags = [tag for tag in tags if tag]

        success = self.note_manager.update(self.current_note_id, title, content, tags, "html")
        if success:
            print(f"✅ Заметка {self.current_note_id} сохранена")
            self.save_btn.setEnabled(False)
            # Обновляем список заметок
            self.load_notes(self.search_input.text())
            #self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить заметку")

    def save_bookmark(self):
        """Сохраняет изменения в закладке"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Предупреждение", "Заголовок не может быть пустым!")
            return

        # Получаем текущую закладку
        bookmark = self.bookmark_manager.get(self.current_bookmark_id)
        if not bookmark:
            QMessageBox.critical(self, "Ошибка", "Закладка не найдена!")
            return

        # Получаем теги
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
        tags = [tag for tag in tags if tag]

        # Обновляем закладку
        # Нужно добавить метод update в BookmarkManager
        success = self.bookmark_manager.update(
            self.current_bookmark_id,
            title=title,
            description=bookmark.description,  # Пока не редактируем описание
            tags=tags
        )

        if success:
            print(f"✅ Закладка {self.current_bookmark_id} сохранена")
            self.save_btn.setEnabled(False)
            # Обновляем список закладок
            # self.bookmarks_widget.refresh() # РАССКОМЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ЗАКЛАДОК
            # self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить закладку")

    def save_new_note(self):
        """Создает новую заметку"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Предупреждение", "Заголовок не может быть пустым!")
            return

        content = self.rich_editor.to_html()
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
        tags = [tag for tag in tags if tag]

        note = self.note_manager.create(title, content, tags, "html")
        if note:
            print(f"✅ Новая заметка создана: {note.id}")
            self.save_btn.setEnabled(False)
            self.current_note_id = note.id
            # Обновляем список заметок
            self.load_notes(self.search_input.text())
            # self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось создать заметку")

    def on_bookmark_selected(self, bookmark_id: int):
        """Обработчик выбора закладки"""
        bookmark = self.bookmark_manager.get(bookmark_id)
        if bookmark:
            # Показываем информацию о закладке в редакторе
            self.display_bookmark(bookmark)

    def display_bookmark(self, bookmark):
        """Отображает закладку в редакторе в простом формате"""
        # Очищаем редактор
        self.title_input.clear()
        self.rich_editor.clear()
        self.tags_input.clear()

        # Заполняем информацию о закладке
        self.title_input.setText(bookmark.title)

        # Простой текст без HTML форматирования
        content = f"""🔖 {bookmark.title}

    URL: {bookmark.url}

    """

        if bookmark.description:
            content += f"Описание: {bookmark.description}\n\n"

        content += f"Домен: {bookmark.get_domain()}\n"
        content += f"Добавлена: {bookmark.created_date.strftime('%d.%m.%Y %H:%M')}\n"

        if bookmark.tags:
            tags_text = ", ".join([tag.name for tag in bookmark.tags])
            content += f"Теги: {tags_text}\n"

        self.rich_editor.set_plain_text(content)
        self.rich_editor.setEnabled(False)

        # Показываем теги
        if bookmark.tags:
            tags_text = ", ".join([tag.name for tag in bookmark.tags])
            self.tags_input.setText(tags_text)

        # Выключаем кнопку Сохранить (нет изменений)
        self.save_btn.setEnabled(False)
        self.current_note_id = None
        self.current_bookmark_id = bookmark.id

    def show_add_bookmark_dialog(self):
        """Показывает диалог добавления закладки"""
        from src.widgets.add_bookmark_dialog import AddBookmarkDialog

        dialog = AddBookmarkDialog(self.bookmark_manager, self)
        dialog.bookmark_added.connect(self.on_bookmark_added)
        dialog.exec()

    def on_bookmark_added(self):
        """Обработчик добавления новой закладки"""
        print("✅ Новая закладка добавлена")
        # Обновляем список заметок чтобы показать новую закладку
        self.load_notes(self.search_input.text())
        # Обновляем теги
        # self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ

    def navigate_to_note_by_id(self, note_id):
        """Переходит к заметке по ID"""
        print(f"🔍 Переход к заметке {note_id}")

        # Ищем заметку в списке
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                print(f"✅ Найдена заметка: {item.text()}")
                return

        # Если не нашли в текущем списке, загружаем все заметки и ищем снова
        print("⚠️  Заметка не найдена в текущем списке, загружаем все заметки...")
        self.load_notes()

        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                print(f"✅ Найдена заметка после перезагрузки: {item.text()}")
                return

        print(f"❌ Заметка с ID {note_id} не найдена")

    def on_task_toggled_from_widget(self, task_id, is_completed):
        """Обработчик изменения задачи из виджета предстоящих задач"""
        print(f"🔄 Задача {task_id} изменена: выполнена = {is_completed}")

        # Обновляем задачи в текущей заметке если она открыта
        if (hasattr(self, 'current_note_id') and
                self.current_note_id and
                hasattr(self, 'tasks_layout')):
            # Перезагружаем задачи для текущей заметки
            self.load_tasks_for_note(self.current_note_id)
            print("✅ Задачи текущей заметки обновлены")

        # Автоматически обновляем список предстоящих задач
        self.refresh_upcoming_tasks()

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

            # Автоматически обновляем список предстоящих задач
            self.refresh_upcoming_tasks()

            self.on_note_modified()

    def refresh_upcoming_tasks(self):
        """Обновляет виджет предстоящих задач"""
        if hasattr(self, 'upcoming_tasks_widget'):
            self.upcoming_tasks_widget.refresh()
            print("✅ Список предстоящих задач обновлен")

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

        # Кнопка удаления
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("font-weight: bold; color: red;")
        delete_btn.clicked.connect(
            lambda checked, task_id=task.id, widget=task_widget: self.delete_task(task_id, widget)
        )

        layout.addWidget(checkbox)
        layout.addStretch()
        layout.addWidget(delete_btn)

        self.tasks_layout.addWidget(task_widget)

    def on_task_toggled(self, task_id, state):
        """Обработчик переключения чекбокса в редакторе заметки"""
        is_checked = state == Qt.CheckState.Checked.value
        success = self.task_manager.update_task(task_id, is_completed=is_checked)
        if success:
            print(f"✅ Статус задачи {task_id} обновлен: {is_checked}")

            # Автоматически обновляем список предстоящих задач
            self.refresh_upcoming_tasks()

            # Обновляем состояние заметки
            self.on_note_modified()
        else:
            print(f"❌ Ошибка обновления задачи {task_id}")

    def delete_task(self, task_id, widget):
        """Удаляет задачу"""
        success = self.task_manager.delete_task(task_id)
        if success:
            self.tasks_layout.removeWidget(widget)
            widget.deleteLater()

            # Автоматически обновляем список предстоящих задач
            self.refresh_upcoming_tasks()

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

        print(f"✅ Загружено {len(tasks)} задач для заметки {note_id}")

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
        self.search_button.clicked.connect(self.on_search_clicked)

        self.notes_list.currentItemChanged.connect(self.on_note_selected)

        # Подключаем автосохранение И включение кнопки Сохранить при изменениях
        self.title_input.textChanged.connect(self.on_content_changed)
        self.rich_editor.text_edit.textChanged.connect(self.on_content_changed)
        self.tags_input.textChanged.connect(self.on_content_changed)


    def on_content_changed(self):
        """Обработчик изменения содержимого"""
        # Включаем кнопку Сохранить при любых изменениях
        self.save_btn.setEnabled(True)

        # Для заметок также планируем автосохранение
        if hasattr(self, 'current_note_id') and self.current_note_id:
            self.schedule_auto_save()

    def schedule_auto_save(self):
        """Планирует автосохранение через 3 секунды после последнего изменения"""
        if hasattr(self, 'current_note_id') and self.current_note_id:
            self.auto_save_timer.start(3000)  # 3 секунды
            print("⏰ Автосохранение запланировано через 3 секунды...")

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
            else:
                print(f"❌ Ошибка автосохранения заметки {self.current_note_id}")

        except Exception as e:
            print(f"❌ Ошибка при автосохранении: {e}")

    def force_auto_save(self):
        """Принудительное автосохранение текущей заметки"""
        if not hasattr(self, 'current_note_id') or not self.current_note_id:
            return False

        # Останавливаем таймер, чтобы не было дублирования
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        try:
            title = self.title_input.text().strip()
            if not title:
                print("⚠️  Автосохранение пропущено: пустой заголовок")
                return False

            content = self.rich_editor.to_html()
            tags_text = self.tags_input.text().strip()
            tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
            tags = [tag for tag in tags if tag]

            success = self.note_manager.update(self.current_note_id, title, content, tags, "html")
            if success:
                print(f"✅ Автосохранение заметки {self.current_note_id}")

                # Обновляем список предстоящих задач после сохранения заметки
                self.refresh_upcoming_tasks()

                return True
            else:
                print(f"❌ Ошибка автосохранения заметки {self.current_note_id}")
                return False

        except Exception as e:
            print(f"❌ Ошибка при автосохранении: {e}")
            return False

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
        # Автосохранение предыдущей заметки перед переключением
        if (previous is not None and
                hasattr(self, 'current_note_id') and
                self.current_note_id and
                not hasattr(self, 'current_bookmark_id')):  # Только для заметок

            self.force_auto_save()

        # Останавливаем таймер автосохранения
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        if current is None:
            return

        try:
            note_id = current.data(Qt.ItemDataRole.UserRole)
            note = self.note_manager.get(note_id)
            if note:
                # Убираем флаг закладки при выборе заметки
                if hasattr(self, 'current_bookmark_id'):
                    del self.current_bookmark_id

                self.display_note(note)
                self.current_note_id = note_id
                self.set_editor_enabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заметку: {e}")

    def display_note(self, note):
        """Отображает заметку в редакторе"""
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

        # Выключаем кнопку Сохранить (нет изменений)
        self.save_btn.setEnabled(False)

    def set_editor_enabled(self, enabled):
        self.title_input.setEnabled(enabled)
        self.tags_input.setEnabled(enabled)
        self.rich_editor.setEnabled(enabled)

    def update_window_title(self):
        """Обновляет заголовок окна"""
        base_title = "Умный Органайзер"
        # Теперь всегда показываем чистый заголовок, так как автосохранение
        self.setWindowTitle(base_title)

    # В методах, где меняется состояние сохранения:
    def on_note_modified(self):
        """Обработчик изменения заметки (теперь только для автосохранения)"""

        # Для автосохранения существующих заметок
        if hasattr(self, 'current_note_id') and self.current_note_id:
            self.schedule_auto_save()

    def on_new_note(self):
        """Создание новой заметки"""
        # Автосохранение текущей заметки если есть изменения
        if (hasattr(self, 'current_note_id') and
                self.current_note_id and
                self.save_btn.isEnabled()):

            reply = QMessageBox.question(
                self,
                "Несохраненные изменения",
                "Сохранить изменения в текущей заметке перед созданием новой?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.on_save_clicked()

        # Останавливаем автосохранение
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        # Очищаем все атрибуты
        if hasattr(self, 'current_bookmark_id'):
            del self.current_bookmark_id

        self.current_note_id = None

        # Очищаем поля
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

        # Включаем кнопку Сохранить (новая заметка)
        self.save_btn.setEnabled(True)
        self.title_input.setFocus()

    def on_delete_note(self):
        """Удаление заметки"""
        # Автосохранение если есть изменения
        if (hasattr(self, 'current_note_id') and
                self.current_note_id):
            self.force_auto_save()  # Просто сохраняем без вопросов

        if not self.current_note_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите заметку для удаления!")
            return

        # Удаляем без лишних подтверждений
        try:
            success = self.note_manager.delete(self.current_note_id)
            if success:
                print(f"✅ Заметка {self.current_note_id} удалена")
                # self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ
                self.load_notes(self.search_input.text())
                self.set_editor_enabled(True)
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
