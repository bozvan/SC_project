import os
import sys
import traceback
from datetime import datetime

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMessageBox, QListWidgetItem, QCheckBox, QLineEdit, QPushButton, QScrollArea, \
    QWidget, QLabel, QHBoxLayout, QVBoxLayout

# Получаем путь к корневой папке SC_project
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Поднимаемся на уровень выше из src/gui/
sc_project_root = os.path.dirname(project_root)  # Еще выше - в SC_project

try:
    from src.gui.ui_main_window import Ui_MainWindow
    from src.gui.ui_notes_page import Ui_NotesPage
    from src.core.database_manager import DatabaseManager
    from src.core.task_manager import TaskManager
    from src.core.tag_manager import TagManager
    from src.widgets.tags_widget import TagsWidget
    from src.core.note_manager import NoteManager
    from src.widgets.rich_text_editor import RichTextEditor
    from src.widgets.note_editor import NoteEditorWindow
    print("✅ Все модули успешно импортированы")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    traceback.print_exc()
    sys.exit(1)


def parse_search_query(query):
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


class NotesWidget(QtWidgets.QWidget, Ui_NotesPage):
    def __init__(self):
        super().__init__()
        self.content_editor = None
        self.rich_editor = None
        self.current_bookmark_id = None
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

        self.setup_managers()
        self.setup_ui_simple()
        self.setup_connections()

        # Автопоиск при вводе текста
        self.search_input.textChanged.connect(self.on_search_text_changed)

        # Таймер для автосохранения
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.auto_save_note)

        self.load_notes()

    def navigate_to_note_by_id(self, note_id):
        """Переходит к заметке по ID (вызывается извне)"""
        print(f"🔍 Навигация к заметке {note_id}")

        # Ищем заметку в текущем списке
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                print(f"✅ Найдена заметка: {item.text()}")
                return

        # Если не нашли в текущем списке, загружаем все заметки и ищем снова
        print("⚠️  Заметка не найдена в текущем списке, загружаем все заметки...")
        self.load_notes("")  # Загружаем все заметки

        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                print(f"✅ Найдена заметка после перезагрузки: {item.text()}")
                return

        print(f"❌ Заметка с ID {note_id} не найдена")
        QMessageBox.warning(self, "Ошибка", f"Заметка с ID {note_id} не найдена")

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

    def on_search_text_changed(self, text):
        """Обработчик изменения текста в поле поиска - автопоиск"""
        # Используем таймер для задержки поиска (чтобы не искать на каждый символ)
        if not hasattr(self, 'search_timer'):
            self.search_timer = QTimer()
            self.search_timer.setSingleShot(True)
            self.search_timer.timeout.connect(self.perform_auto_search)

        # Перезапускаем таймер при каждом изменении текста
        self.search_timer.start(50)  # Поиск через 50 мс после последнего ввода

    def perform_auto_search(self):
        """Выполняет поиск после задержки"""
        query = self.search_input.text()
        self.load_notes(query)

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

        self.tags_widget = TagsWidget(self.tag_manager)
        self.tags_widget.tag_selected.connect(self.on_tag_selected_from_widget)
        self.verticalLayout.addWidget(self.tags_widget)

        self.save_btn.setVisible(True)
        self.save_btn.setEnabled(False)  # Изначально выключена
        self.save_btn.clicked.connect(self.on_save_clicked)

        # self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)

        # Добавляем кнопку открепления
        self.detach_btn = QPushButton("📌 Открепить")
        self.detach_btn.setToolTip("Открыть в отдельном окне")
        self.detach_btn.clicked.connect(self.detach_note)

        # Добавьте кнопку в ваш layout, например в заголовок:
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Редактор заметки"))
        header_layout.addStretch()
        header_layout.addWidget(self.detach_btn)

        self.verticalLayout.insertLayout(0, header_layout)

        print("✅ UI настроен с отдельными разделами для задач и закладок")

    def detach_note(self):
        """Открепление текущей заметки в отдельное окно"""
        if not hasattr(self, 'current_note_id') or not self.current_note_id:
            QMessageBox.warning(self, "Предупреждение", "Сначала откройте заметку!")
            return

        try:
            # Автосохранение текущей заметки перед откреплением
            if hasattr(self, 'force_auto_save'):
                self.force_auto_save()

            self.editor_window = NoteEditorWindow(self.note_manager, self.current_note_id)

            # Подключаем все сигналы
            self.editor_window.note_saved.connect(self.on_note_saved_from_window)
            self.editor_window.note_updated.connect(self.on_note_updated_from_window)  # ← Новый обработчик
            self.editor_window.window_closed.connect(self.on_editor_window_closed)

            self.editor_window.show()

            # Поднимаем окно на передний план
            self.editor_window.raise_()
            self.editor_window.activateWindow()

            print(f"📌 Заметка {self.current_note_id} откреплена в отдельное окно")

        except Exception as e:
            print(f"❌ Ошибка при создании окна редактора: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть окно редактора: {e}")

    def on_note_updated_from_window(self, note_id, title, content, tags):
        """Обработчик обновления заметки из отдельного окна"""
        print(f"🔄 Заметка {note_id} обновлена в отдельном окне")

        # Обновляем текущую заметку если она открыта
        if hasattr(self, 'current_note_id') and self.current_note_id == note_id:
            # Обновляем данные в редакторе
            self.title_input.setText(title)

            if hasattr(self, 'rich_editor') and hasattr(self.rich_editor, 'set_html'):
                self.rich_editor.set_html(content)

            # Обновляем теги
            tags_text = ", ".join(tags)
            self.tags_input.setText(tags_text)

            print(f"✅ Данные заметки {note_id} обновлены в основном редакторе")

        # Принудительно обновляем список заметок
        self.load_notes(self.search_input.text())

        # Обновляем виджет тегов если есть
        if hasattr(self, 'tags_widget'):
            self.tags_widget.refresh()

    def on_note_saved_from_window(self, note_id):
        """Обработчик сохранения заметки из отдельного окна"""
        print(f"💾 Заметка {note_id} сохранена из отдельного окна")
        # Вызываем обновление через новый метод
        self.on_note_updated_from_window(note_id, "", "", [])

    def on_editor_window_closed(self, note_id):
        """Обработчик закрытия окна редактора"""
        # Включаем редактор обратно в основном окне
        self.set_editor_enabled(True)
        print(f"📌 Окно редактора для заметки {note_id} закрыто")

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
            self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ
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
            self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ
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
            self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ
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
        # Обновляем список заметок, чтобы показать новую закладку
        self.load_notes(self.search_input.text())
        # Обновляем теги
        self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ

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
        """Создает область для задач под редактором с расширенными возможностями"""
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

        # РАСШИРЕННАЯ ФОРМА ДОБАВЛЕНИЯ ЗАДАЧИ
        self.setup_expanded_task_form(tasks_layout)

        # Добавляем контейнер задач в основной layout
        self.verticalLayout_2.addWidget(self.tasks_container)

    def setup_expanded_task_form(self, parent_layout):
        """Настраивает расширенную форму добавления задачи"""
        # Основной контейнер для формы
        self.task_form_container = QWidget()
        task_form_layout = QVBoxLayout(self.task_form_container)
        task_form_layout.setContentsMargins(0, 5, 0, 5)

        # Первая строка - описание задачи
        description_layout = QHBoxLayout()
        self.new_task_input = QLineEdit()
        self.new_task_input.setPlaceholderText("Описание задачи...")
        self.new_task_input.returnPressed.connect(self.on_task_form_submit)

        self.add_task_btn = QPushButton("Добавить")
        self.add_task_btn.clicked.connect(self.on_task_form_submit)

        description_layout.addWidget(self.new_task_input)
        description_layout.addWidget(self.add_task_btn)

        # Вторая строка - расширенные опции (изначально скрыты)
        self.extended_options_container = QWidget()
        extended_layout = QHBoxLayout(self.extended_options_container)
        extended_layout.setContentsMargins(0, 5, 0, 0)

        # Приоритет
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Приоритет:"))
        self.priority_combo = QtWidgets.QComboBox()
        self.priority_combo.addItems(["🔴 Высокий", "🟡 Средний", "🟢 Низкий"])
        self.priority_combo.setCurrentText("🟡 Средний")  # По умолчанию
        priority_layout.addWidget(self.priority_combo)
        priority_layout.addStretch()

        # Срок выполнения
        due_date_layout = QHBoxLayout()
        due_date_layout.addWidget(QLabel("Срок:"))
        self.due_date_edit = QtWidgets.QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QtCore.QDate.currentDate())
        self.due_date_edit.setMinimumDate(QtCore.QDate.currentDate())
        due_date_layout.addWidget(self.due_date_edit)
        due_date_layout.addStretch()

        # Кнопка очистки срока
        self.clear_due_date_btn = QPushButton("×")
        self.clear_due_date_btn.setFixedSize(20, 20)
        self.clear_due_date_btn.setToolTip("Очистить срок")
        self.clear_due_date_btn.clicked.connect(self.clear_due_date)
        due_date_layout.addWidget(self.clear_due_date_btn)

        extended_layout.addLayout(priority_layout)
        extended_layout.addLayout(due_date_layout)
        extended_layout.addStretch()

        # Изначально скрываем расширенные опции
        self.extended_options_container.setVisible(False)

        # Кнопка показа/скрытия расширенных опций
        self.toggle_options_btn = QPushButton("⚙️ Дополнительно")
        self.toggle_options_btn.setCheckable(True)
        self.toggle_options_btn.setChecked(False)
        self.toggle_options_btn.clicked.connect(self.toggle_extended_options)

        # Собираем всю форму
        task_form_layout.addLayout(description_layout)
        task_form_layout.addWidget(self.toggle_options_btn)
        task_form_layout.addWidget(self.extended_options_container)

        parent_layout.addWidget(self.task_form_container)

    def toggle_extended_options(self, checked):
        """Переключает видимость расширенных опций"""
        self.extended_options_container.setVisible(checked)
        if checked:
            self.toggle_options_btn.setText("⚙️ Скрыть")
        else:
            self.toggle_options_btn.setText("⚙️ Дополнительно")

    def clear_due_date(self):
        """Очищает срок выполнения"""
        self.due_date_edit.setDate(QtCore.QDate.currentDate())

    def on_task_form_submit(self):
        """Обработчик отправки формы задачи"""
        if not self.current_note_id:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте или откройте заметку!")
            return

        description = self.new_task_input.text().strip()
        if not description:
            return

        # Получаем приоритет
        priority_text = self.priority_combo.currentText()
        priority_map = {
            "🔴 Высокий": "high",
            "🟡 Средний": "medium",
            "🟢 Низкий": "low"
        }
        priority = priority_map.get(priority_text, "medium")

        # Получаем срок выполнения (если установлен)
        due_date = None
        selected_date = self.due_date_edit.date()
        if selected_date > QtCore.QDate.currentDate():
            due_date = QtCore.QDateTime(selected_date, QtCore.QTime(23, 59)).toPyDateTime()

        # Создаем задачу в БД
        task = self.task_manager.create_task(
            note_id=self.current_note_id,
            description=description,
            due_date=due_date,
            priority=priority
        )

        if task:
            self.add_task_widget(task)  # Уже включает сортировку
            self.clear_task_form()

            # Автоматически обновляем список предстоящих задач
            self.refresh_upcoming_tasks()
            self.on_note_modified()

            print(f"✅ Задача создана: {description} (приоритет: {priority})")

    def clear_task_form(self):
        """Очищает форму добавления задачи"""
        self.new_task_input.clear()
        self.priority_combo.setCurrentText("🟡 Средний")
        self.due_date_edit.setDate(QtCore.QDate.currentDate())

        # Скрываем расширенные опции
        self.toggle_options_btn.setChecked(False)
        self.extended_options_container.setVisible(False)
        self.toggle_options_btn.setText("⚙️ Дополнительно")

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
        """Добавляет виджет задачи с отображением приоритета и срока"""
        task_widget = QWidget()
        layout = QHBoxLayout(task_widget)
        layout.setContentsMargins(5, 2, 5, 2)

        # Чекбокс с дополнительной информацией
        task_text = task.description

        # Добавляем иконку приоритета
        priority_icons = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        priority_icon = priority_icons.get(task.priority, "🟡")

        # Добавляем информацию о сроке
        due_info = ""
        if task.due_date:
            due_date_str = task.due_date.strftime('%d.%m.%Y')
            due_info = f" (до {due_date_str})"

        checkbox = QCheckBox(f"{priority_icon} {task_text}{due_info}")
        checkbox.setChecked(task.is_completed)
        checkbox.stateChanged.connect(
            lambda state, task_id=task.id: self.on_task_toggled(task_id, state)
        )

        # Кнопка редактирования
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.setToolTip("Редактировать задачу")
        edit_btn.clicked.connect(
            lambda checked, task_id=task.id: self.edit_task(task_id)
        )

        # Кнопка удаления
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("font-weight: bold; color: red;")
        delete_btn.setToolTip("Удалить задачу")
        delete_btn.clicked.connect(
            lambda checked, task_id=task.id, widget=task_widget: self.delete_task(task_id, widget)
        )

        layout.addWidget(checkbox)
        layout.addStretch()
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

        self.tasks_layout.addWidget(task_widget)
        self.sort_tasks()

    def sort_tasks(self):
        """Сортирует задачи по приоритету и сроку выполнения"""
        if not hasattr(self, 'tasks_layout') or self.tasks_layout.count() == 0:
            return

        # Если есть текущая заметка, перезагружаем задачи с сортировкой из БД
        if hasattr(self, 'current_note_id') and self.current_note_id:
            self.load_tasks_for_note(self.current_note_id)

    def edit_task(self, task_id):
        """Редактирование существующей задачи"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return

        # Создаем диалог редактирования
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Редактировать задачу")
        dialog.setModal(True)
        dialog.setFixedWidth(400)

        layout = QVBoxLayout(dialog)

        # Описание
        layout.addWidget(QLabel("Описание:"))
        description_edit = QLineEdit(task.description)
        layout.addWidget(description_edit)

        # Приоритет
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Приоритет:"))
        priority_combo = QtWidgets.QComboBox()
        priority_combo.addItems(["🔴 Высокий", "🟡 Средний", "🟢 Низкий"])

        # Устанавливаем текущий приоритет
        priority_map_reverse = {
            "high": "🔴 Высокий",
            "medium": "🟡 Средний",
            "low": "🟢 Низкий"
        }
        priority_combo.setCurrentText(priority_map_reverse.get(task.priority, "🟡 Средний"))
        priority_layout.addWidget(priority_combo)
        priority_layout.addStretch()
        layout.addLayout(priority_layout)

        # Срок выполнения
        due_date_layout = QHBoxLayout()
        due_date_layout.addWidget(QLabel("Срок:"))
        due_date_edit = QtWidgets.QDateEdit()
        due_date_edit.setCalendarPopup(True)

        if task.due_date:
            due_date_edit.setDate(QtCore.QDate(
                task.due_date.year,
                task.due_date.month,
                task.due_date.day
            ))
        else:
            due_date_edit.setDate(QtCore.QDate.currentDate())

        due_date_edit.setMinimumDate(QtCore.QDate.currentDate())
        due_date_layout.addWidget(due_date_edit)

        # Кнопка очистки срока
        clear_due_date_btn = QPushButton("×")
        clear_due_date_btn.setFixedSize(20, 20)
        clear_due_date_btn.setToolTip("Очистить срок")
        clear_due_date_btn.clicked.connect(lambda: due_date_edit.setDate(QtCore.QDate.currentDate()))
        due_date_layout.addWidget(clear_due_date_btn)
        due_date_layout.addStretch()
        layout.addLayout(due_date_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Обновляем задачу
            new_description = description_edit.text().strip()
            if not new_description:
                QMessageBox.warning(self, "Ошибка", "Описание не может быть пустым!")
                return

            new_priority_text = priority_combo.currentText()
            new_priority_map = {
                "🔴 Высокий": "high",
                "🟡 Средний": "medium",
                "🟢 Низкий": "low"
            }
            new_priority = new_priority_map.get(new_priority_text, "medium")

            new_due_date = None
            selected_date = due_date_edit.date()
            if selected_date > QtCore.QDate.currentDate():
                new_due_date = QtCore.QDateTime(selected_date, QtCore.QTime(23, 59)).toPyDateTime()

            success = self.task_manager.update_task(
                task_id,
                description=new_description,
                priority=new_priority,
                due_date=new_due_date
            )

            if success:
                print(f"✅ Задача {task_id} обновлена")
                # ПЕРЕЗАГРУЖАЕМ ВСЕ ЗАДАЧИ С СОРТИРОВКОЙ
                self.load_tasks_for_note(self.current_note_id)
                self.refresh_upcoming_tasks()
                self.on_note_modified()

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

            # СОРТИРУЕМ ЗАДАЧИ ПОСЛЕ ИЗМЕНЕНИЯ СТАТУСА
            self.sort_tasks()
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

            # СОРТИРОВКА НЕ НУЖНА - просто удалили элемент

    def load_tasks_for_note(self, note_id):
        """Загружает задачи для заметки с автоматической сортировкой"""
        # Очищаем старые задачи
        for i in reversed(range(self.tasks_layout.count())):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                self.tasks_layout.removeWidget(widget)
                widget.deleteLater()

        if not note_id:
            return

        # Загружаем новые задачи ИЗ БД С СОРТИРОВКОЙ
        tasks = self.task_manager.get_tasks_for_note(note_id)

        # Сортируем задачи по приоритету и сроку
        priority_order = {"high": 1, "medium": 2, "low": 3}
        tasks.sort(key=lambda task: (
            priority_order.get(task.priority, 2),  # Сначала по приоритету
            task.due_date or datetime(9999, 12, 31),  # Затем по сроку (без срока - в конец)
            task.description.lower()  # Затем по описанию
        ))

        for task in tasks:
            self.add_task_widget_without_sort(task)  # Добавляем без повторной сортировки

        print(f"✅ Загружено {len(tasks)} задач для заметки {note_id}")

    def add_task_widget_without_sort(self, task):
        """Добавляет виджет задачи без вызова сортировки (для использования в load_tasks_for_note)"""
        task_widget = QWidget()
        layout = QHBoxLayout(task_widget)
        layout.setContentsMargins(5, 2, 5, 2)

        # Чекбокс с дополнительной информацией
        task_text = task.description

        # Добавляем иконку приоритета
        priority_icons = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        priority_icon = priority_icons.get(task.priority, "🟡")

        # Добавляем информацию о сроке
        due_info = ""
        if task.due_date:
            due_date_str = task.due_date.strftime('%d.%m.%Y')
            due_info = f" (до {due_date_str})"

        checkbox = QCheckBox(f"{priority_icon} {task_text}{due_info}")
        checkbox.setChecked(task.is_completed)
        checkbox.stateChanged.connect(
            lambda state, task_id=task.id: self.on_task_toggled(task_id, state)
        )

        # Кнопка редактирования
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.setToolTip("Редактировать задачу")
        edit_btn.clicked.connect(
            lambda checked, task_id=task.id: self.edit_task(task_id)
        )

        # Кнопка удаления
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("font-weight: bold; color: red;")
        delete_btn.setToolTip("Удалить задачу")
        delete_btn.clicked.connect(
            lambda checked, task_id=task.id, widget=task_widget: self.delete_task(task_id, widget)
        )

        layout.addWidget(checkbox)
        layout.addStretch()
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

        self.tasks_layout.addWidget(task_widget)

    def add_task_widget(self, task):
        """Добавляет виджет задачи и сортирует список"""
        self.add_task_widget_without_sort(task)
        self.sort_tasks()  # Теперь просто перезагружает с сортировкой из БД

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

        # Подключаем автосохранение И включение кнопки. Сохранить при изменениях
        self.title_input.textChanged.connect(self.on_content_changed)
        self.rich_editor.text_edit.textChanged.connect(self.on_content_changed)
        self.tags_input.textChanged.connect(self.on_content_changed)

    def on_content_changed(self):
        """Обработчик изменения содержимого"""
        # Включаем кнопку. Сохранить при любых изменениях
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
            search_text, tags = parse_search_query(search_query)

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
                self.tags_widget.refresh() # РАССКОММЕНТИРОВАТЬ, КОГДА ПОЯВИТСЯ ВИДЖЕТ ТЕГОВ
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
