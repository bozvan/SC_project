from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal

from gui.ui_edit_bookmark_dialog import Ui_EditBookmarkDialog


class EditBookmarkDialog(QDialog, Ui_EditBookmarkDialog):
    """Диалоговое окно для редактирования закладки"""

    bookmark_updated = pyqtSignal(int)  # Сигнал при обновлении закладки

    def __init__(self, bookmark_manager, bookmark, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.bookmark_manager = bookmark_manager
        self.bookmark = bookmark
        self.original_data = {
            'title': bookmark.title,
            'url': bookmark.url,
            'description': bookmark.description or '',
            'tags': ', '.join([tag.name for tag in bookmark.tags]) if bookmark.tags else ''
        }

        # Установить кнопку "Сохранить" как кнопку по умолчанию
        self.save_btn.setDefault(True)
        self.save_btn.setAutoDefault(True)
        self.cancel_btn.setAutoDefault(False)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Заполняет форму данными закладки"""
        self.title_edit.setText(self.bookmark.title)
        self.url_edit.setText(self.bookmark.url)

        if self.bookmark.description:
            self.description_edit.setPlainText(self.bookmark.description)

        if self.bookmark.tags:
            tags_text = ', '.join([tag.name for tag in self.bookmark.tags])
            self.tags_edit.setText(tags_text)

        # Устанавливаем фокус на поле названия
        self.title_edit.setFocus()
        self.title_edit.selectAll()

    def setup_connections(self):
        """Настраивает соединения сигналов"""
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.save_bookmark)

        # Валидация в реальном времени
        self.title_edit.textChanged.connect(self.validate_form)
        self.url_edit.textChanged.connect(self.validate_form)

    def validate_form(self):
        """Проверяет валидность формы"""
        title = self.title_edit.text().strip()
        url = self.url_edit.text().strip()

        is_valid = bool(title) and bool(url)
        self.save_btn.setEnabled(is_valid)

        # Подсветка невалидных полей
        if not title:
            self.title_edit.setStyleSheet("border: 1px solid red;")
        else:
            self.title_edit.setStyleSheet("")

        if not url:
            self.url_edit.setStyleSheet("border: 1px solid red;")
        else:
            self.url_edit.setStyleSheet("")

        return is_valid

    def save_bookmark(self):
        """Сохраняет изменения закладки"""
        title = self.title_edit.text().strip()
        url = self.url_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        tags_text = self.tags_edit.text().strip()

        # Валидация
        if not title:
            QMessageBox.warning(self, "Ошибка", "Название закладки не может быть пустым")
            self.title_edit.setFocus()
            return

        if not url:
            QMessageBox.warning(self, "Ошибка", "URL закладки не может быть пустым")
            self.url_edit.setFocus()
            return

        # Проверяем, изменились ли данные
        new_data = {
            'title': title,
            'url': url,
            'description': description,
            'tags': tags_text
        }

        if new_data == self.original_data:
            self.accept()
            return

        try:
            # Парсим теги
            tags = []
            if tags_text:
                tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

            # Обновляем закладку в БД
            success = self.bookmark_manager.update_bookmark(
                self.bookmark.id,
                title=title,
                url=url,
                description=description,
                tags=tags
            )

            if success:
                print(f"✅ Закладка {self.bookmark.id} обновлена")
                self.bookmark_updated.emit(self.bookmark.id)
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить закладку")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def get_updated_data(self):
        """Возвращает обновленные данные"""
        return {
            'title': self.title_edit.text().strip(),
            'url': self.url_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'tags': self.tags_edit.text().strip()
        }
