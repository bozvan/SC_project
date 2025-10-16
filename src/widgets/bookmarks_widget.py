from PyQt6.QtWidgets import (QWidget, QListWidgetItem, QMenu,
                             QMessageBox, QApplication, QDialog)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction
import webbrowser

from gui.ui_bookmarks_widget import Ui_BookmarksWidget
from widgets.bookmark_item_widget import BookmarkItemWidget  # Импортируем из отдельного файла


class BookmarksWidget(QWidget, Ui_BookmarksWidget):
    """Виджет для отображения и управления веб-закладками"""

    bookmark_selected = pyqtSignal(int)  # bookmark_id
    bookmark_deleted = pyqtSignal(int)  # bookmark_id
    bookmark_description_changed = pyqtSignal(int, str)  # bookmark_id, new_description

    def __init__(self, bookmark_manager, workspace_id=1, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.workspace_id = workspace_id
        self.setupUi(self)
        self.setup_connections()
        self.load_bookmarks()

    def set_workspace(self, workspace_id):
        """Обновляет workspace и перезагружает закладки"""
        self.workspace_id = workspace_id
        self.load_bookmarks()

    def setup_connections(self):
        """Настраивает соединения сигналов"""
        self.search_input.textChanged.connect(self.on_search_changed)
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.add_btn.clicked.connect(self.on_add_bookmark)
        self.refresh_btn.clicked.connect(self.refresh)

        self.bookmarks_list.itemClicked.connect(self.on_bookmark_clicked)
        self.bookmarks_list.customContextMenuRequested.connect(self.show_context_menu)

    def clear_search(self):
        """Очищает поле поиска"""
        self.search_input.clear()

    def load_bookmarks(self, search_text: str = ""):
        """Загружает и отображает закладки ТОЛЬКО для текущего workspace"""
        self.bookmarks_list.clear()

        # Получаем закладки ТОЛЬКО для текущего workspace
        bookmarks = self.bookmark_manager.get_bookmarks_by_workspace(self.workspace_id)

        # Фильтруем по поисковому запросу
        if search_text:
            search_text_lower = search_text.lower()
            bookmarks = [
                b for b in bookmarks
                if (search_text_lower in b.title.lower() or
                    search_text_lower in b.url.lower() or
                    search_text_lower in (b.description or "").lower() or
                    any(search_text_lower in tag.name.lower() for tag in b.tags))
            ]

        for bookmark in bookmarks:
            # Создаем кастомный виджет для каждой закладки
            bookmark_widget = self.create_bookmark_widget(bookmark)

            # Создаем item для списка
            item = QListWidgetItem()
            item.setSizeHint(bookmark_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, bookmark.id)

            self.bookmarks_list.addItem(item)
            self.bookmarks_list.setItemWidget(item, bookmark_widget)

        # Обновляем статистику
        self.stats_label.setText(f"Закладок: {len(bookmarks)}")
        print(f"✅ Загружено закладок в workspace {self.workspace_id}: {len(bookmarks)}")

    def create_bookmark_widget(self, bookmark):
        """Создает виджет для отображения закладки"""
        widget = BookmarkItemWidget(bookmark, self.bookmark_manager, self)

        # Подключаем сигналы
        widget.clicked.connect(self.bookmark_selected.emit)
        widget.copy_requested.connect(self.copy_to_clipboard)
        widget.open_requested.connect(self.open_in_browser)
        widget.description_changed.connect(self.on_description_changed)
        widget.edit_requested.connect(self.edit_bookmark)
        widget.delete_requested.connect(self.delete_bookmark)

        return widget

    def on_description_changed(self, bookmark_id: int, new_description: str):
        """Обработчик изменения описания закладки"""
        self.bookmark_description_changed.emit(bookmark_id, new_description)

    def on_search_changed(self, text):
        """Обработчик изменения поискового запроса"""
        self.load_bookmarks(text.strip())

    def on_bookmark_clicked(self, item):
        """Обработчик клика по закладке"""
        if not item:
            return

        bookmark_id = item.data(Qt.ItemDataRole.UserRole)
        self.bookmark_selected.emit(bookmark_id)

    def show_context_menu(self, position):
        """Показывает контекстное меню для закладки"""
        item = self.bookmarks_list.itemAt(position)
        if not item:
            return

        bookmark_id = item.data(Qt.ItemDataRole.UserRole)
        bookmark = self.bookmark_manager.get(bookmark_id)

        if not bookmark:
            return

        menu = QMenu(self)

        # Открыть в браузере
        open_action = QAction("🌐 Открыть в браузере", self)
        open_action.triggered.connect(lambda: self.open_in_browser(bookmark.url))
        menu.addAction(open_action)

        # Копировать URL
        copy_url_action = QAction("📋 Копировать URL", self)
        copy_url_action.triggered.connect(lambda: self.copy_to_clipboard(bookmark.url))
        menu.addAction(copy_url_action)

        # Редактировать описание
        edit_action = QAction("✏️ Редактировать закладку", self)
        edit_action.triggered.connect(lambda: self.edit_bookmark(bookmark_id))
        menu.addAction(edit_action)

        menu.addSeparator()

        # Удалить
        delete_action = QAction("🗑️ Удалить закладку", self)
        delete_action.triggered.connect(lambda: self.delete_bookmark(bookmark_id))
        menu.addAction(delete_action)

        menu.exec(self.bookmarks_list.mapToGlobal(position))

    def edit_bookmark(self, bookmark_id: int):
        """Открывает диалог редактирования закладки"""
        from widgets.edit_bookmark_dialog import EditBookmarkDialog

        bookmark = self.bookmark_manager.get(bookmark_id)
        if not bookmark:
            QMessageBox.warning(self, "Ошибка", "Закладка не найдена")
            return

        dialog = EditBookmarkDialog(self.bookmark_manager, bookmark, self)
        dialog.bookmark_updated.connect(self.on_bookmark_updated)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            print(f"✅ Закладка {bookmark_id} отредактирована")

    def on_bookmark_updated(self, bookmark_id: int):
        """Обработчик обновления закладки"""
        self.load_bookmarks(self.search_input.text())
        print(f"🔄 Закладка {bookmark_id} обновлена, список перезагружен")

    def edit_bookmark_description(self, bookmark_id: int):
        """Редактирует описание закладки"""
        # Находим виджет закладки
        for i in range(self.bookmarks_list.count()):
            item = self.bookmarks_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == bookmark_id:
                widget = self.bookmarks_list.itemWidget(item)
                if hasattr(widget, 'toggle_edit_mode'):
                    widget.toggle_edit_mode()
                break

    def open_in_browser(self, url: str):
        """Открывает URL в браузере по умолчанию"""
        try:
            webbrowser.open(url)
            print(f"🌐 Открыто в браузере: {url}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть URL: {e}")

    def copy_to_clipboard(self, text: str):
        """Копирует текст в буфер обмена"""
        QApplication.clipboard().setText(text)
        print(f"📋 Скопировано в буфер: {text}")

    def delete_bookmark(self, bookmark_id: int):
        """Удаляет закладку"""
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить эту закладку?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.bookmark_manager.delete(bookmark_id)
            if success:
                self.bookmark_deleted.emit(bookmark_id)
                self.load_bookmarks(self.search_input.text())
                print(f"✅ Закладка {bookmark_id} удалена")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить закладку")

    def on_add_bookmark(self):
        """Обработчик добавления новой закладки"""
        from widgets.add_bookmark_dialog import AddBookmarkDialog

        try:
            # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
            print(f"🔍 Отладка BookmarksWidget.on_add_bookmark():")
            print(f"   - Текущий workspace_id: {self.workspace_id} (тип: {type(self.workspace_id)})")
            print(f"   - Bookmark Manager: {type(self.bookmark_manager)}")
            print(f"   - Parent: {type(self)}")

            dialog = AddBookmarkDialog(self.bookmark_manager, self.workspace_id, self)
            dialog.bookmark_added.connect(self.on_bookmark_added)
            dialog.exec()
        except Exception as e:
            print(f"❌ Ошибка при создании диалога добавления закладки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог добавления закладки: {str(e)}")

    def on_bookmark_added(self):
        """Обработчик добавления новой закладки"""
        self.load_bookmarks(self.search_input.text())
        print("✅ Новая закладка добавлена")

    def refresh(self):
        """Обновляет список закладок"""
        self.load_bookmarks(self.search_input.text())
