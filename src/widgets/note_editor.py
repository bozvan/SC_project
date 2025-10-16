from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLineEdit,
                             QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from gui.ui_note_editor import Ui_NoteEditorWindow
import traceback


class NoteEditorWindow(QMainWindow, Ui_NoteEditorWindow):
    """Независимое окно для редактирования заметки"""

    note_saved = pyqtSignal(int)  # Сигнал при сохранении заметки
    window_closed = pyqtSignal(int)  # Сигнал при закрытии окна
    note_updated = pyqtSignal(int, str, str, list)  # ← ДОБАВЬТЕ ЭТОТ СИГНАЛ

    def __init__(self, note_manager, note_id):
        super().__init__()  # Без parent для независимости
        self.setupUi(self)

        # Установите флаги для настоящего независимого окна
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )

        self.note_manager = note_manager
        self.note_id = note_id

        self.setup_rich_editor()

        # Инициализация таймера автосохранения
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.auto_save_note)

        self.load_note()
        self.setup_connections()

    def setup_rich_editor(self):
        """Заменяет стандартный QTextEdit на RichTextEditor"""
        try:
            from widgets.rich_text_editor import RichTextEditor

            # Сохраняем позицию текущего редактора в layout
            old_editor = self.content_editor

            # Создаем богатый текстовый редактор
            self.rich_editor = RichTextEditor()

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
        # Подключаем сигналы изменений
        self.title_input.textChanged.connect(self.on_content_changed)
        self.tags_input.textChanged.connect(self.on_content_changed)

        # Если rich_editor имеет сигнал textChanged
        if hasattr(self.rich_editor, 'textChanged'):
            self.rich_editor.textChanged.connect(self.on_content_changed)
        elif hasattr(self.rich_editor, 'text_edit'):
            self.rich_editor.text_edit.textChanged.connect(self.on_content_changed)
        else:
            # Для обычного QTextEdit
            self.rich_editor.textChanged.connect(self.on_content_changed)

        # Подключение кнопок
        self.save_btn.clicked.connect(self.save_note)
        self.cancel_btn.clicked.connect(self.close)

    def load_note(self):
        """Загрузка данных заметки"""
        note = self.note_manager.get(self.note_id)
        if note:
            self.title_input.setText(note.title)

            # Установка содержимого
            if hasattr(self.rich_editor, 'set_html'):
                self.rich_editor.set_html(note.content)
            else:
                self.rich_editor.setPlainText(note.content)

            # Установка тегов
            if note.tags:
                tags_text = ", ".join([tag.name for tag in note.tags])
                self.tags_input.setText(tags_text)

            #self.setWindowTitle(f"Редактор: {note.title}")
            self.setWindowIcon(QIcon("assets/icons/icon3.png"))
            self.setWindowTitle("")
            self.update_status("✅ Загружено")

    def on_content_changed(self):
        """Обработчик изменения содержимого - запускает автосохранение"""
        self.schedule_auto_save()
        self.update_status("⚪ Не сохранено")

    def schedule_auto_save(self):
        """Планирует автосохранение через 3 секунды после последнего изменения"""
        self.auto_save_timer.start(50)  # 50 мс
        self.update_status("⏳ Сохранение через 3с...")

    def auto_save_note(self):
        """Автоматически сохраняет заметку"""
        try:
            title = self.title_input.text().strip()
            if not title:
                self.update_status("⚠️  Автосохранение пропущено: пустой заголовок")
                return

            # Получение содержимого
            if hasattr(self.rich_editor, 'to_html'):
                content = self.rich_editor.to_html()
            else:
                content = self.rich_editor.toPlainText()

            # Обработка тегов
            tags_text = self.tags_input.text().strip()
            tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
            tags = [tag for tag in tags if tag]  # Убираем пустые теги

            # Сохранение
            success = self.note_manager.update(self.note_id, title, content, tags, "html")
            if success:
                self.update_status("✅ Автосохранено")
                self.note_saved.emit(self.note_id)
                self.note_updated.emit(self.note_id, title, content, tags)  # ← Используем новый сигнал
                print(f"✅ Автосохранение заметки {self.note_id} в отдельном окне")
            else:
                self.update_status("❌ Ошибка автосохранения")
                print(f"❌ Ошибка автосохранения заметки {self.note_id}")

        except Exception as e:
            self.update_status("❌ Ошибка автосохранения")
            print(f"❌ Ошибка при автосохранении: {e}")
            traceback.print_exc()

    def update_status(self, message):
        """Обновляет статус сохранения"""
        self.status_label.setText(message)

        # Цвета статуса
        if "✅" in message:
            self.status_label.setStyleSheet("color: green; font-size: 11px;")
        elif "❌" in message or "⚠️" in message:
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
        elif "⏳" in message:
            self.status_label.setStyleSheet("color: orange; font-size: 11px;")
        else:
            self.status_label.setStyleSheet("color: gray; font-size: 11px;")

    def save_note(self):
        """Ручное сохранение заметки"""
        # Останавливаем таймер автосохранения
        self.auto_save_timer.stop()

        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка", "Заголовок не может быть пустым!")
            self.update_status("⚠️  Пустой заголовок")
            return

        # Получение содержимого
        if hasattr(self.rich_editor, 'to_html'):
            content = self.rich_editor.to_html()
        else:
            content = self.rich_editor.toPlainText()

        # Обработка тегов
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip().lower() for tag in tags_text.split(",")] if tags_text else []
        tags = [tag for tag in tags if tag]  # Убираем пустые теги

        # Сохранение
        success = self.note_manager.update(self.note_id, title, content, tags, "html")
        if success:
            self.update_status("✅ Сохранено")
            self.note_saved.emit(self.note_id)
            self.note_updated.emit(self.note_id, title, content, tags)  # ← Используем новый сигнал
            QMessageBox.information(self, "Успех", "Заметка сохранена!")
            print(f"✅ Заметка {self.note_id} сохранена в отдельном окне")
        else:
            self.update_status("❌ Ошибка сохранения")
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить заметку")

    def force_auto_save(self):
        """Принудительное автосохранение"""
        if self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
        self.auto_save_note()

    def closeEvent(self, event):
        """Обработчик закрытия окна - автосохранение перед закрытием"""
        print(f"🔴 Закрытие окна редактора для заметки {self.note_id}...")

        # Принудительное автосохранение при закрытии
        if hasattr(self, 'auto_save_timer') and self.auto_save_timer.isActive():
            print("💾 Выполняем автосохранение перед закрытием...")
            self.force_auto_save()

        # Останавливаем таймер
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        self.window_closed.emit(self.note_id)
        print(f"📌 Окно редактора для заметки {self.note_id} закрыто")
        super().closeEvent(event)
