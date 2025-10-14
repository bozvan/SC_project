from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt

from src.gui.ui_add_bookmark_dialog import Ui_AddBookmarkDialog


class AddBookmarkDialog(QDialog, Ui_AddBookmarkDialog):
    """Диалоговое окно для добавления новой закладки"""

    bookmark_added = pyqtSignal()  # Сигнал при добавлении закладки

    def __init__(self, bookmark_manager, workspace_id=1, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.bookmark_manager = bookmark_manager
        self.workspace_id = workspace_id  # Сохраняем workspace_id

        # Проверяем, что кнопки существуют перед настройкой
        if hasattr(self, 'add_btn') and self.add_btn is not None:
            self.add_btn.setDefault(True)
            self.add_btn.setAutoDefault(True)
        else:
            print("⚠️ Кнопка add_btn не найдена в UI")

        if hasattr(self, 'cancel_btn') and self.cancel_btn is not None:
            self.cancel_btn.setAutoDefault(False)
        else:
            print("⚠️ Кнопка cancel_btn не найдена в UI")

        self.setup_connections()

    def setup_connections(self):
        """Настраивает соединения сигналов"""
        if hasattr(self, 'cancel_btn') and self.cancel_btn is not None:
            self.cancel_btn.clicked.connect(self.reject)
        else:
            print("⚠️ Кнопка cancel_btn не найдена для подключения сигнала")

        if hasattr(self, 'add_btn') and self.add_btn is not None:
            self.add_btn.clicked.connect(self.add_bookmark)
        else:
            print("⚠️ Кнопка add_btn не найдена для подключения сигнала")

        # Обработка нажатия Enter в полях ввода
        if hasattr(self, 'url_edit') and self.url_edit is not None:
            self.url_edit.returnPressed.connect(self.on_enter_pressed)

        if hasattr(self, 'title_edit') and self.title_edit is not None:
            self.title_edit.returnPressed.connect(self.on_enter_pressed)

        if hasattr(self, 'tags_edit') and self.tags_edit is not None:
            self.tags_edit.returnPressed.connect(self.on_enter_pressed)

        # Валидация в реальном времени
        if hasattr(self, 'url_edit') and self.url_edit is not None:
            self.url_edit.textChanged.connect(self.validate_form)

    def on_enter_pressed(self):
        """Обработчик нажатия Enter в полях ввода"""
        if self.validate_form():
            self.add_bookmark()

    def keyPressEvent(self, event):
        """Обработчик нажатия клавиш"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Проверяем, что cancel_btn существует и имеет фокус
            if (hasattr(self, 'cancel_btn') and self.cancel_btn is not None and
                    self.cancel_btn.hasFocus()):
                return
            if self.validate_form():
                self.add_bookmark()
            else:
                self.focusNextChild()
        else:
            super().keyPressEvent(event)

    def validate_form(self):
        """Проверяет валидность формы"""
        if not hasattr(self, 'url_edit') or self.url_edit is None:
            return False

        url = self.url_edit.text().strip()
        is_valid = bool(url)

        # Включаем/выключаем кнопку добавления если она существует
        if hasattr(self, 'add_btn') and self.add_btn is not None:
            self.add_btn.setEnabled(is_valid)

        # Подсветка поля URL
        if not url:
            self.url_edit.setStyleSheet("border: 1px solid red;")
        else:
            self.url_edit.setStyleSheet("")

        return is_valid

    def add_bookmark(self):
        """Добавляет новую закладку"""
        # Проверяем существование необходимых виджетов
        if not hasattr(self, 'url_edit') or self.url_edit is None:
            QMessageBox.warning(self, "Ошибка", "Поле URL не найдено")
            return

        url = self.url_edit.text().strip()

        # Получаем опциональные поля если они существуют
        title = ""
        if hasattr(self, 'title_edit') and self.title_edit is not None:
            title = self.title_edit.text().strip()

        description = ""
        if hasattr(self, 'description_edit') and self.description_edit is not None:
            description = self.description_edit.toPlainText().strip()

        tags_text = ""
        if hasattr(self, 'tags_edit') and self.tags_edit is not None:
            tags_text = self.tags_edit.text().strip()

        # Валидация
        if not url:
            QMessageBox.warning(self, "Ошибка", "URL закладки не может быть пустым")
            if hasattr(self, 'url_edit') and self.url_edit is not None:
                self.url_edit.setFocus()
            return

        try:
            # Парсим теги
            tags = []
            if tags_text:
                tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

            # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
            print(f"🔍 Отладка AddBookmarkDialog.add_bookmark():")
            print(f"   - URL: {url}")
            print(f"   - Title: {title}")
            print(f"   - Description: {description}")
            print(f"   - Tags: {tags}")
            print(f"   - Workspace ID: {self.workspace_id} (тип: {type(self.workspace_id)})")
            print(f"   - Bookmark Manager: {type(self.bookmark_manager)}")

            # Добавляем закладку с указанием workspace_id
            bookmark = self.bookmark_manager.add_bookmark_with_metadata(
                url=url,
                tags=tags,
                workspace_id=self.workspace_id  # Передаем workspace_id
            )

            if bookmark:
                print(f"✅ Закладка добавлена в workspace {self.workspace_id}: {bookmark.title}")
                self.bookmark_added.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить закладку")

        except Exception as e:
            print(f"❌ Ошибка при добавлении закладки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении закладки: {str(e)}")
