from PyQt6.QtWidgets import (QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

from src.gui.ui_bookmark_item_widget import Ui_BookmarkItemWidget


class BookmarkItemWidget(QFrame, Ui_BookmarkItemWidget):
    """Виджет для отображения отдельной закладки в списке"""

    clicked = pyqtSignal(int)  # bookmark_id
    copy_requested = pyqtSignal(str)  # url
    open_requested = pyqtSignal(str)  # url
    description_changed = pyqtSignal(int, str)  # bookmark_id, new_description
    edit_requested = pyqtSignal(int)  # bookmark_id
    delete_requested = pyqtSignal(int)  # bookmark_id - НОВЫЙ СИГНАЛ

    def __init__(self, bookmark, bookmark_manager, parent=None):
        super().__init__(parent)
        self.bookmark = bookmark
        self.bookmark_manager = bookmark_manager
        self.is_editing = False
        self.setupUi(self)

        self.setup_bookmark_data()
        self.setup_connections()

    def setup_bookmark_data(self):
        """Заполняет виджет данными закладки"""
        # Заголовок
        self.title_label.setText(f"🔖 {self.bookmark.title}")

        # URL
        self.url_label.setText(self.bookmark.url)

        # Описание
        if self.bookmark.description:
            self.description_edit.setPlainText(self.bookmark.description)
        else:
            self.description_edit.setPlainText("")

        # Теги (если есть)
        if self.bookmark.tags:
            tags_text = "🏷️ " + ", ".join([tag.name for tag in self.bookmark.tags])
            self.tags_label.setText(tags_text)
        else:
            self.tags_label.hide()

        # Дата
        if hasattr(self.bookmark, 'created_date'):
            self.date_label.setText(self.bookmark.created_date.strftime("%d.%m.%Y"))
        else:
            self.date_label.hide()

    def setup_connections(self):
        """Настраивает соединения сигналов"""
        self.title_label.mousePressEvent = self.on_title_clicked
        self.copy_btn.clicked.connect(self.on_copy_clicked)
        self.open_btn.clicked.connect(self.on_open_clicked)
        self.edit_btn.clicked.connect(self.on_edit_clicked)
        self.delete_btn.clicked.connect(self.on_delete_clicked)  # НОВОЕ СОЕДИНЕНИЕ

        # Двойной клик по описанию для редактирования
        self.description_edit.mouseDoubleClickEvent = self.on_description_double_click

    def on_title_clicked(self, event):
        """Обработчик клика по заголовку"""
        self.clicked.emit(self.bookmark.id)

    def on_copy_clicked(self):
        """Обработчик кнопки копирования"""
        self.copy_requested.emit(self.bookmark.url)

    def on_open_clicked(self):
        """Обработчик кнопки открытия в браузере"""
        self.open_requested.emit(self.bookmark.url)

    def on_edit_clicked(self):
        """Обработчик кнопки редактирования - открывает диалог"""
        if hasattr(self, 'edit_requested'):
            self.edit_requested.emit(self.bookmark.id)
        else:
            # Если в родительском виджете нет сигнала, открываем диалог напрямую
            from src.widgets.edit_bookmark_dialog import EditBookmarkDialog
            dialog = EditBookmarkDialog(self.bookmark_manager, self.bookmark, self)
            if dialog.exec():
                # Обновляем данные в виджете
                self.setup_bookmark_data()

    def on_delete_clicked(self):
        """Обработчик кнопки удаления закладки"""
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить закладку:\n\"{self.bookmark.title}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Отправляем сигнал родительскому виджету для удаления
            self.delete_requested.emit(self.bookmark.id)
            print(f"🗑️ Запрос на удаление закладки {self.bookmark.id}")

    def on_description_double_click(self, event):
        """Обработчик двойного клика по описанию"""
        self.toggle_edit_mode()

    def toggle_edit_mode(self):
        """Переключает режим редактирования описания"""
        if self.is_editing:
            self.save_description()
        else:
            self.start_editing()

    def start_editing(self):
        """Начинает редактирование описания"""
        self.is_editing = True
        self.description_edit.setReadOnly(False)
        self.description_edit.setStyleSheet("""
            QTextEdit {
                background-color: palette(base);
                border: 2px solid palette(highlight);
                border-radius: 3px;
                padding: 4px;
                font-size: 10px;
                color: palette(text);
            }
        """)
        self.edit_btn.setText("💾")
        self.edit_btn.setToolTip("Сохранить описание")

        # Устанавливаем фокус и выделяем весь текст
        self.description_edit.setFocus()
        self.description_edit.selectAll()

    def save_description(self):
        """Сохраняет описание и выходит из режима редактирования"""
        new_description = self.description_edit.toPlainText().strip()

        # Обновляем в базе данных
        success = self.bookmark_manager.update_bookmark_description(
            self.bookmark.id, new_description
        )

        if success:
            self.bookmark.description = new_description
            self.description_changed.emit(self.bookmark.id, new_description)
            print(f"✅ Описание закладки {self.bookmark.id} обновлено")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить описание")
            # Восстанавливаем старое значение
            self.description_edit.setPlainText(self.bookmark.description or "")

        self.finish_editing()

    def finish_editing(self):
        """Завершает редактирование"""
        self.is_editing = False
        self.description_edit.setReadOnly(True)
        self.description_edit.setStyleSheet("""
            QTextEdit {
                background-color: palette(alternate-base);
                border: 1px solid palette(midlight);
                border-radius: 3px;
                padding: 4px;
                font-size: 10px;
                color: palette(text);
            }
        """)
        self.edit_btn.setText("✏️")
        self.edit_btn.setToolTip("Редактировать описание")

    def keyPressEvent(self, event):
        """Обработчик нажатия клавиш"""
        if self.is_editing and event.key() == Qt.Key.Key_Escape:
            # Отмена редактирования по Escape
            self.description_edit.setPlainText(self.bookmark.description or "")
            self.finish_editing()
        elif self.is_editing and event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Сохранение по Ctrl+Enter
            self.save_description()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        """Обработчик потери фокуса"""
        if self.is_editing:
            self.save_description()
        super().focusOutEvent(event)
