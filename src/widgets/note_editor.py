from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLineEdit,
                             QPushButton, QLabel, QHBoxLayout, QMessageBox, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from gui.ui_note_editor import Ui_NoteEditorWindow
import traceback


class NoteEditorWindow(QMainWindow, Ui_NoteEditorWindow):
    """Независимое окно для редактирования заметки"""

    note_saved = pyqtSignal(int)  # Сигнал при сохранении заметки
    window_closed = pyqtSignal(int)  # Сигнал при закрытии окна
    note_updated = pyqtSignal(int, str, str, list)  # note_id, title, content, tags

    def __init__(self, note_manager, note_id):
        super().__init__()  # Без parent для независимости

        # Устанавливаем флаги для настоящего независимого окна СРАЗУ с режимом поверх всех окон
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowStaysOnTopHint  # ВСЕГДА поверх всех окон
        )

        self.setupUi(self)
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))

        self.note_manager = note_manager
        self.note_id = note_id

        # Сохраняем оригинальный заголовок
        self._original_title = ""
        self._original_content = ""
        self._original_tags = []

        # Флаг "Поверх всех окон" - ВСЕГДА True
        self._always_on_top = True

        self.setup_rich_editor()
        self.setup_minimal_ui()  # Создаем минимальный UI если нужно
        self.setup_context_menu()  # Создаем контекстное меню

        # УСКОРЕННОЕ АВТОСОХРАНЕНИЕ (500 мс)
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.auto_save_note)
        self.auto_save_delay = 100  # 0.1 секунды
        self.last_content_change = 0

        # Статус сохранения
        self._saved = True
        self._changes_made = False

        self.load_note()
        self.setup_connections()

        # Устанавливаем иконку и заголовок
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.update_window_title()

    def setup_context_menu(self):
        """Создает контекстное меню для окна"""
        # Создаем контекстное меню
        self.context_menu = QMenu(self)

        # Действие "Поверх всех окон" - всегда включено и недоступно для изменения
        self.always_on_top_action = QAction("📌 Всегда поверх окон", self)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.setChecked(True)
        self.always_on_top_action.setEnabled(False)  # Делаем недоступным для изменения
        self.context_menu.addAction(self.always_on_top_action)

        # Разделитель
        self.context_menu.addSeparator()

        # Действие "Сохранить"
        save_action = QAction("💾 Сохранить", self)
        save_action.triggered.connect(self.save_note)
        self.context_menu.addAction(save_action)

        # Действие "Закрыть"
        close_action = QAction("❌ Закрыть", self)
        close_action.triggered.connect(self.close)
        self.context_menu.addAction(close_action)

    def contextMenuEvent(self, event):
        """Обработчик события контекстного меню"""
        self.context_menu.exec(event.globalPos())

    def setup_minimal_ui(self):
        """Создает минимальный UI если в ui_note_editor нет полей заголовка и тегов"""
        # Проверяем, есть ли уже поля заголовка и тегов
        if not hasattr(self, 'title_input') or not self.title_input:
            # Создаем поле заголовка
            self.title_input = QLineEdit()
            self.title_input.setPlaceholderText("Заголовок заметки...")
            self.title_input.setObjectName("title_input")
            self.title_input.setVisible(False)

            # Добавляем в layout перед редактором контента
            layout = self.centralwidget.layout()
            if layout:
                layout.insertWidget(0, self.title_input)
            else:
                # Если нет layout, создаем новый
                new_layout = QVBoxLayout(self.centralwidget)
                new_layout.addWidget(self.title_input)
                new_layout.addWidget(self.rich_editor)

        if not hasattr(self, 'tags_input') or not self.tags_input:
            # Создаем поле тегов
            self.tags_input = QLineEdit()
            self.tags_input.setPlaceholderText("Теги (через запятую)...")
            self.tags_input.setObjectName("tags_input")
            self.tags_input.setVisible(False)

            # Добавляем в layout после редактора контента
            layout = self.centralwidget.layout()
            if layout:
                layout.addWidget(self.tags_input)

    def setup_rich_editor(self):
        """Заменяет стандартный QTextEdit на RichTextEditor"""
        try:
            from widgets.rich_text_editor import RichTextEditor

            # Сохраняем позицию текущего редактора в layout
            old_editor = self.content_editor

            # Создаем богатый текстовый редактор
            self.rich_editor = RichTextEditor()
            self.rich_editor.setObjectName("content_editor")

            # Заменяем в layout
            layout = self.centralwidget.layout()
            for i in range(layout.count()):
                if layout.itemAt(i).widget() == old_editor:
                    layout.removeWidget(old_editor)
                    old_editor.deleteLater()
                    layout.insertWidget(i, self.rich_editor)
                    break

        except ImportError:
            # Используем стандартный QTextEdit
            self.rich_editor = self.content_editor
            print("⚠️  RichTextEditor не найден, используется стандартный QTextEdit")

    def setup_connections(self):
        """Настройка соединений для автосохранения"""
        # Подключаем сигналы изменений для УСКОРЕННОГО автосохранения
        if hasattr(self, 'title_input') and self.title_input:
            self.title_input.textChanged.connect(self.on_content_changed)

        if hasattr(self, 'tags_input') and self.tags_input:
            self.tags_input.textChanged.connect(self.on_content_changed)

        # Подключаем редактор контента
        if hasattr(self.rich_editor, 'textChanged'):
            self.rich_editor.textChanged.connect(self.on_content_changed)
        elif hasattr(self.rich_editor, 'text_edit'):
            self.rich_editor.text_edit.textChanged.connect(self.on_content_changed)
        else:
            # Для обычного QTextEdit
            self.rich_editor.textChanged.connect(self.on_content_changed)

        # Подключение кнопки сохранения если есть
        if hasattr(self, 'save_btn') and self.save_btn:
            self.save_btn.clicked.connect(self.save_note)

    def load_note(self):
        """Загрузка данных заметки"""
        note = self.note_manager.get(self.note_id)
        if note:
            # Сохраняем оригинальные данные
            self._original_title = note.title
            self._original_content = note.content
            self._original_tags = [tag.name for tag in note.tags] if note.tags else []

            # Загружаем заголовок если есть поле
            if hasattr(self, 'title_input') and self.title_input:
                self.title_input.setText(note.title)

            # Установка содержимого
            if hasattr(self.rich_editor, 'set_html'):
                self.rich_editor.set_html(note.content)
            else:
                self.rich_editor.setPlainText(note.content)

            # Установка тегов если есть поле
            if hasattr(self, 'tags_input') and self.tags_input:
                if note.tags:
                    tags_text = ", ".join([tag.name for tag in note.tags])
                    self.tags_input.setText(tags_text)
                else:
                    self.tags_input.clear()

            print(f"✅ Заметка {self.note_id} загружена в отдельное окно")
            print(f"   Заголовок: {note.title}")
            print(f"   Теги: {[tag.name for tag in note.tags] if note.tags else 'нет'}")

    def on_content_changed(self):
        """Обработчик изменения содержимого - запускает УСКОРЕННОЕ автосохранение"""
        current_time = self.get_current_time()
        self.last_content_change = current_time
        self._saved = False
        self._changes_made = True

        # Планируем автосохранение через 0.5 секунды
        self.schedule_auto_save()
        self.update_window_title()

    def get_current_time(self):
        """Возвращает текущее время в миллисекундах"""
        from datetime import datetime
        return datetime.now().timestamp() * 1000

    def schedule_auto_save(self):
        """Планирует автосохранение через 0.5 секунды"""
        self.auto_save_timer.start(self.auto_save_delay)

    def auto_save_note(self):
        """Автоматически сохраняет заметку через 0.5 секунды"""
        current_time = self.get_current_time()

        # Проверяем, что прошло достаточно времени с последнего изменения
        if current_time - self.last_content_change >= self.auto_save_delay - 10:
            self.save_note(silent=True)

    def save_note(self, silent=False):
        """Сохранение заметки"""
        try:
            # Получаем заголовок из поля ввода
            title = ""
            if hasattr(self, 'title_input') and self.title_input:
                title = self.title_input.text().strip()

            # Если поле заголовка пустое, используем оригинальный заголовок
            if not title:
                title = self._original_title

            # Если и оригинальный заголовок пустой, используем первые 50 символов контента
            if not title:
                if hasattr(self.rich_editor, 'to_plain_text'):
                    content_text = self.rich_editor.to_plain_text()
                else:
                    content_text = self.rich_editor.toPlainText()
                title = content_text[:50].strip() or "Без названия"

            # Получение содержимого
            if hasattr(self.rich_editor, 'to_html'):
                content = self.rich_editor.to_html()
            else:
                content = self.rich_editor.toPlainText()

            # Обработка тегов
            tags = []
            if hasattr(self, 'tags_input') and self.tags_input:
                tags_text = self.tags_input.text().strip()
                tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
                tags = [tag for tag in tags if tag]  # Убираем пустые теги

            print(f"💾 Сохранение заметки {self.note_id}:")
            print(f"   Заголовок: '{title}'")
            print(f"   Теги: {tags}")
            print(f"   Длина контента: {len(content)} символов")

            # Сохранение
            success = self.note_manager.update(self.note_id, title, content, tags, "html")
            if success:
                self._saved = True
                self._changes_made = False

                # Обновляем оригинальные данные
                self._original_title = title
                self._original_content = content
                self._original_tags = tags

                if not silent:
                    print(f"✅ Заметка {self.note_id} сохранена из отдельного окна")

                # Отправляем сигналы об обновлении
                self.note_saved.emit(self.note_id)
                self.note_updated.emit(self.note_id, title, content, tags)

                self.update_window_title()
                return True
            else:
                if not silent:
                    print(f"❌ Ошибка сохранения заметки {self.note_id}")
                    QMessageBox.critical(self, "Ошибка", "Не удалось сохранить заметку")
                return False

        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            traceback.print_exc()
            if not silent:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")
            return False

    def update_window_title(self):
        """Обновляет заголовок окна с указанием статуса сохранения"""
        # Используем оригинальный заголовок или текущий из поля ввода
        display_title = self._original_title
        if hasattr(self, 'title_input') and self.title_input:
            current_title = self.title_input.text().strip()
            if current_title:
                display_title = current_title

        if not display_title:
            display_title = f"Заметка #{self.note_id}"

        # Всегда добавляем значок "поверх всех окон"
        display_title = f"📌 {display_title}"

        base_title = f"{display_title}"

        if not self._saved:
            self.setWindowTitle(f"● {base_title}")
        else:
            self.setWindowTitle(base_title)

    def force_auto_save(self):
        """Принудительное автосохранение"""
        if self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
        self.save_note(silent=True)

    def closeEvent(self, event):
        """Обработчик закрытия окна - автосохранение перед закрытием"""
        print(f"🔴 Закрытие окна редактора для заметки {self.note_id}...")

        # Если есть несохраненные изменения, сохраняем
        if self._changes_made and not self._saved:
            print("💾 Выполняем автосохранение перед закрытием...")
            self.force_auto_save()

        # Останавливаем таймер
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        # Отправляем сигнал о закрытии
        self.window_closed.emit(self.note_id)
        print(f"📌 Окно редактора для заметки {self.note_id} закрыто")

        super().closeEvent(event)

    def has_unsaved_changes(self):
        """Проверяет, есть ли несохраненные изменения"""
        return self._changes_made and not self._saved

    def is_always_on_top(self):
        """Проверяет, включен ли режим 'Поверх всех окон'"""
        return True  # Всегда True
