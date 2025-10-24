from PyQt6.QtWidgets import (QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor

from gui.ui_bookmark_item_widget import Ui_BookmarkItemWidget


class BookmarkItemWidget(QFrame, Ui_BookmarkItemWidget):
    """Виджет для отображения отдельной закладки в списке"""

    clicked = pyqtSignal(int)  # bookmark_id
    copy_requested = pyqtSignal(str)  # url
    open_requested = pyqtSignal(str)  # url
    description_changed = pyqtSignal(int, str)  # bookmark_id, new_description
    edit_requested = pyqtSignal(int)  # bookmark_id - теперь открывает диалог
    delete_requested = pyqtSignal(int)  # bookmark_id

    def __init__(self, bookmark, bookmark_manager, parent=None):
        super().__init__(parent)
        self.bookmark = bookmark
        self.bookmark_manager = bookmark_manager
        self.is_editing = False
        self._is_destroyed = False  # Флаг для отслеживания уничтожения виджета
        self.setupUi(self)

        # Таймер для автосохранения
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.auto_save_description)

        self.setup_bookmark_data()
        self.setup_connections()

    def setup_bookmark_data(self):
        """Заполняет виджет данными закладки"""
        # Заголовок
        self.title_label.setText(f"🔖 {self.bookmark.title}")

        # URL
        self.url_label.setText(self.bookmark.url)

        # Описание - ВСЕГДА редактируемое
        if self.bookmark.description:
            self.description_edit.setPlainText(self.bookmark.description)
        else:
            self.description_edit.setPlainText("")

        # Делаем поле описания ВСЕГДА доступным для редактирования
        self.description_edit.setReadOnly(False)
        self.description_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Разрешаем фокус

        # Устанавливаем курсор в конец текста
        cursor = self.description_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.description_edit.setTextCursor(cursor)

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
        self.edit_btn.clicked.connect(self.on_edit_clicked)  # Теперь открывает диалог
        self.delete_btn.clicked.connect(self.on_delete_clicked)

        # АВТОСОХРАНЕНИЕ ПРИ ИЗМЕНЕНИИ ТЕКСТА
        self.description_edit.textChanged.connect(self.schedule_auto_save)

    def schedule_auto_save(self):
        """Планирует автосохранение через 1 секунду после изменения"""
        if self._is_destroyed:
            return

        # Перезапускаем таймер при каждом изменении
        self.auto_save_timer.start(1000)  # 1 секунда

    def auto_save_description(self):
        """Автоматически сохраняет описание"""
        if self._is_destroyed:
            return

        new_description = self.description_edit.toPlainText().strip()
        old_description = self.bookmark.description or ""

        # Сохраняем только если текст изменился
        if new_description != old_description:
            success = self.bookmark_manager.update_bookmark_description(
                self.bookmark.id, new_description
            )

            if success:
                self.bookmark.description = new_description
                self.description_changed.emit(self.bookmark.id, new_description)
                print(f"✅ Описание закладки {self.bookmark.id} автосохранено")
            else:
                print(f"❌ Ошибка автосохранения описания закладки {self.bookmark.id}")

    def force_save_description(self):
        """Принудительно сохраняет описание (немедленно)"""
        if self._is_destroyed:
            return False

        # Останавливаем таймер, чтобы избежать дублирования
        if hasattr(self, 'auto_save_timer') and not self._is_destroyed:
            try:
                if self.auto_save_timer.isActive():
                    self.auto_save_timer.stop()
            except RuntimeError:
                # Таймер уже удален, игнорируем ошибку
                pass

        new_description = self.description_edit.toPlainText().strip()
        old_description = self.bookmark.description or ""

        # Сохраняем только если текст изменился
        if new_description != old_description:
            success = self.bookmark_manager.update_bookmark_description(
                self.bookmark.id, new_description
            )

            if success:
                self.bookmark.description = new_description
                self.description_changed.emit(self.bookmark.id, new_description)
                print(f"💾 Описание закладки {self.bookmark.id} принудительно сохранено")
                return True
            else:
                print(f"❌ Ошибка принудительного сохранения описания закладки {self.bookmark.id}")
                return False
        return True

    def on_title_clicked(self, event):
        """Обработчик клика по заголовку"""
        if self._is_destroyed:
            return
        self.clicked.emit(self.bookmark.id)

    def on_copy_clicked(self):
        """Обработчик кнопки копирования"""
        if self._is_destroyed:
            return
        self.copy_requested.emit(self.bookmark.url)

    def on_open_clicked(self):
        """Обработчик кнопки открытия в браузере"""
        if self._is_destroyed:
            return
        self.open_requested.emit(self.bookmark.url)

    def on_edit_clicked(self):
        """Обработчик кнопки редактирования - ОТКРЫВАЕТ ДИАЛОГ РЕДАКТИРОВАНИЯ"""
        if self._is_destroyed:
            return

        # НЕМЕДЛЕННО сохраняем текущие изменения перед открытием диалога
        self.force_save_description()

        # Испускаем сигнал для открытия диалога
        self.edit_requested.emit(self.bookmark.id)

    def on_delete_clicked(self):
        """Обработчик кнопки удаления закладки"""
        if self._is_destroyed:
            return

        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить закладку:\n\"{self.bookmark.title}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            self
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.bookmark.id)
            print(f"🗑️ Запрос на удаление закладки {self.bookmark.id}")

    def mousePressEvent(self, event):
        """Обработчик клика по всему виджету"""
        if self._is_destroyed:
            return

        # Если клик не на кнопках, устанавливаем фокус на описание
        if (event.button() == Qt.MouseButton.LeftButton and
                not self.copy_btn.underMouse() and
                not self.open_btn.underMouse() and
                not self.edit_btn.underMouse() and
                not self.delete_btn.underMouse() and
                not self.title_label.underMouse()):
            self.description_edit.setFocus()

        super().mousePressEvent(event)

    def focusInEvent(self, event):
        """Обработчик получения фокуса виджетом"""
        if self._is_destroyed:
            return

        if event.reason() in [Qt.FocusReason.MouseFocusReason, Qt.FocusReason.TabFocusReason]:
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
            self.is_editing = True
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Обработчик потери фокуса виджетом"""
        if self._is_destroyed:
            return

        if self.is_editing:
            # Принудительно сохраняем при потере фокуса
            self.force_save_description()
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
            self.is_editing = False
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """Обработчик нажатия клавиш"""
        if self._is_destroyed:
            return

        if event.key() == Qt.Key.Key_Escape and self.description_edit.hasFocus():
            # Отмена редактирования по Escape - восстанавливаем оригинальный текст
            original_text = self.bookmark.description or ""
            self.description_edit.setPlainText(original_text)
            if hasattr(self, 'auto_save_timer') and not self._is_destroyed:
                try:
                    if self.auto_save_timer.isActive():
                        self.auto_save_timer.stop()
                except RuntimeError:
                    # Таймер уже удален, игнорируем ошибку
                    pass
            self.clearFocus()  # Снимаем фокус
        elif (event.key() == Qt.Key.Key_Return and
              event.modifiers() == Qt.KeyboardModifier.ControlModifier and
              self.description_edit.hasFocus()):
            # Принудительное сохранение по Ctrl+Enter
            self.force_save_description()
            self.clearFocus()  # Снимаем фокус после сохранения
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Обработчик закрытия виджета"""
        self.cleanup()
        super().closeEvent(event)

    def cleanup(self):
        """Очистка ресурсов перед удалением виджета"""
        if self._is_destroyed:
            return

        self._is_destroyed = True

        # Останавливаем таймер с обработкой ошибок
        if hasattr(self, 'auto_save_timer'):
            try:
                if self.auto_save_timer.isActive():
                    self.auto_save_timer.stop()
                # Не вызываем deleteLater() - Qt сам управляет временем жизни
            except RuntimeError:
                # Таймер уже удален, игнорируем ошибку
                pass

        # Сохраняем описание
        try:
            self.force_save_description()
        except RuntimeError:
            # Виджет уже удален, игнорируем ошибку
            pass