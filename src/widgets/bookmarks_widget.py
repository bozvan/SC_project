from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLabel, QPushButton, QHBoxLayout, QMenu, QMessageBox,
                             QScrollArea, QFrame, QLineEdit, QApplication, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont
import webbrowser

class BookmarksWidget(QWidget):
    def __init__(self, workspace_id=1, parent=None):
        super().__init__()
        # Создаем простой интерфейс для закладок
        layout = QVBoxLayout(self)
        self.workspace_id = workspace_id
        label = QLabel("<h1>Закладки</h1><p>Раздел в разработке</p>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

    def set_workspace(self, workspace_id):
        """Обновляет workspace и перезагружает закладки"""
        self.workspace_id = workspace_id
        self.load_bookmarks()

# class BookmarksWidget(QWidget):
#     """Виджет для отображения и управления веб-закладками"""
#
#     bookmark_selected = pyqtSignal(int)  # bookmark_id
#     bookmark_deleted = pyqtSignal(int)  # bookmark_id
#
#     def __init__(self, bookmark_manager):
#         super().__init__()
#         self.bookmark_manager = bookmark_manager
#         self.setup_ui()
#         self.load_bookmarks()
#
#     def setup_ui(self):
#         """Настройка интерфейса виджета"""
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(5, 5, 5, 5)
#         layout.setSpacing(5)
#
#         # Заголовок
#         title_label = QLabel("Веб-закладки")
#         title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
#         layout.addWidget(title_label)
#
#         # Поиск
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("Поиск закладок...")
#         self.search_input.textChanged.connect(self.on_search_changed)
#         layout.addWidget(self.search_input)
#
#         # Список закладок
#         self.bookmarks_list = QListWidget()
#         self.bookmarks_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
#         self.bookmarks_list.itemClicked.connect(self.on_bookmark_clicked)
#         self.bookmarks_list.customContextMenuRequested.connect(self.show_context_menu)
#
#         # Настраиваем стиль списка
#         self.bookmarks_list.setStyleSheet("""
#             QListWidget {
#                 background-color: palette(base);
#                 border: 1px solid palette(mid);
#                 border-radius: 3px;
#             }
#             QListWidget::item {
#                 border: none;
#                 padding: 0px;
#                 margin: 2px;
#             }
#             QListWidget::item:selected {
#                 background-color: transparent;
#             }
#             QListWidget::item:hover {
#                 background-color: transparent;
#             }
#         """)
#
#         layout.addWidget(self.bookmarks_list)
#
#         # Кнопка добавления
#         self.add_btn = QPushButton("➕ Добавить закладку")
#         self.add_btn.clicked.connect(self.on_add_bookmark)
#         layout.addWidget(self.add_btn)
#
#         # Статистика
#         self.stats_label = QLabel("Закладок: 0")
#         self.stats_label.setStyleSheet("color: palette(mid); font-size: 11px; margin-top: 5px;")
#         layout.addWidget(self.stats_label)
#
#     def load_bookmarks(self, search_text: str = ""):
#         """Загружает и отображает закладки с кнопками копирования"""
#         self.bookmarks_list.clear()
#
#         # Получаем все закладки
#         bookmarks = self.bookmark_manager.get_all()
#
#         # Фильтруем по поисковому запросу
#         if search_text:
#             search_text_lower = search_text.lower()
#             bookmarks = [
#                 b for b in bookmarks
#                 if (search_text_lower in b.title.lower() or
#                     search_text_lower in b.url.lower() or
#                     search_text_lower in (b.description or "").lower() or
#                     any(search_text_lower in tag.name.lower() for tag in b.tags))
#             ]
#
#         for bookmark in bookmarks:
#             # Создаем кастомный виджет для каждой закладки
#             bookmark_widget = self.create_bookmark_widget(bookmark)
#
#             # Создаем item для списка
#             item = QListWidgetItem()
#             item.setSizeHint(bookmark_widget.sizeHint())
#             item.setData(Qt.ItemDataRole.UserRole, bookmark.id)
#
#             self.bookmarks_list.addItem(item)
#             self.bookmarks_list.setItemWidget(item, bookmark_widget)
#
#         # Обновляем статистику
#         self.stats_label.setText(f"Закладок: {len(bookmarks)}")
#         print(f"✅ Загружено закладок: {len(bookmarks)}")
#
#     def create_bookmark_widget(self, bookmark):
#         """Создает виджет для отображения закладки с кнопками"""
#         widget = QFrame()
#         widget.setFrameStyle(QFrame.Shape.Box)
#         widget.setStyleSheet("""
#             QFrame {
#                 background-color: palette(base);
#                 border: 1px solid palette(midlight);
#                 border-radius: 5px;
#                 padding: 8px;
#             }
#             QFrame:hover {
#                 background-color: palette(alternate-base);
#                 border: 1px solid palette(highlight);
#             }
#         """)
#
#         layout = QVBoxLayout(widget)
#         layout.setContentsMargins(8, 8, 8, 8)
#         layout.setSpacing(4)
#
#         # Верхняя строка: заголовок и кнопки
#         top_layout = QHBoxLayout()
#
#         # Заголовок (кликабельный)
#         title_label = QLabel(f"🔖 {bookmark.title}")
#         title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
#         title_label.setCursor(Qt.CursorShape.PointingHandCursor)
#         title_label.mousePressEvent = lambda e: self.on_bookmark_title_clicked(bookmark.id)
#
#         top_layout.addWidget(title_label)
#         top_layout.addStretch()
#
#         # Кнопка копирования URL
#         copy_btn = QPushButton("📋")
#         copy_btn.setToolTip("Копировать URL")
#         copy_btn.setFixedSize(24, 24)
#         copy_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: palette(button);
#                 border: 1px solid palette(mid);
#                 border-radius: 3px;
#                 font-size: 10px;
#             }
#             QPushButton:hover {
#                 background-color: palette(light);
#             }
#             QPushButton:pressed {
#                 background-color: palette(mid);
#             }
#         """)
#         copy_btn.clicked.connect(lambda: self.copy_to_clipboard(bookmark.url))
#
#         # Кнопка открытия в браузере
#         open_btn = QPushButton("🌐")
#         open_btn.setToolTip("Открыть в браузере")
#         open_btn.setFixedSize(24, 24)
#         open_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: palette(button);
#                 border: 1px solid palette(mid);
#                 border-radius: 3px;
#                 font-size: 10px;
#             }
#             QPushButton:hover {
#                 background-color: palette(light);
#             }
#             QPushButton:pressed {
#                 background-color: palette(mid);
#             }
#         """)
#         open_btn.clicked.connect(lambda: self.open_in_browser(bookmark.url))
#
#         top_layout.addWidget(copy_btn)
#         top_layout.addWidget(open_btn)
#
#         layout.addLayout(top_layout)
#
#         # URL (выделяемый текст)
#         url_layout = QHBoxLayout()
#         url_label = QLabel("URL:")
#         url_label.setStyleSheet("font-size: 10px; color: palette(mid);")
#
#         url_text = QLabel(bookmark.url)
#         url_text.setStyleSheet("""
#             QLabel {
#                 background-color: palette(alternate-base);
#                 border: 1px solid palette(midlight);
#                 border-radius: 3px;
#                 padding: 4px;
#                 font-family: monospace;
#                 font-size: 10px;
#                 color: palette(text);
#             }
#         """)
#         url_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
#         url_text.setCursor(Qt.CursorShape.IBeamCursor)
#         url_text.setWordWrap(True)
#
#         url_layout.addWidget(url_label)
#         url_layout.addWidget(url_text, 1)
#         layout.addLayout(url_layout)
#
#         # Описание (если есть)
#         # if bookmark.description:
#         #     desc_label = QLabel(bookmark.description)
#         #     desc_label.setStyleSheet("font-size: 10px; color: palette(mid); font-style: italic;")
#         #     desc_label.setWordWrap(True)
#         #     desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
#         #     layout.addWidget(desc_label)
#         #
#         # # Теги (если есть)
#         # if bookmark.tags:
#         #     tags_text = "🏷️ " + ", ".join([tag.name for tag in bookmark.tags])
#         #     tags_label = QLabel(tags_text)
#         #     tags_label.setStyleSheet("font-size: 9px; color: palette(placeholder-text);")
#         #     layout.addWidget(tags_label)
#
#         # Домен и дата
#         # meta_layout = QHBoxLayout()
#         # domain_label = QLabel(f"🌐 {bookmark.get_domain()}")
#         # domain_label.setStyleSheet("font-size: 9px; color: palette(placeholder-text);")
#
#         # date_label = QLabel(bookmark.created_date.strftime("%d.%m.%Y"))
#         # date_label.setStyleSheet("font-size: 9px; color: palette(placeholder-text);")
#         #
#         # meta_layout.addWidget(domain_label)
#         # meta_layout.addStretch()
#         # meta_layout.addWidget(date_label)
#         # layout.addLayout(meta_layout)
#
#         return widget
#
#     def on_bookmark_title_clicked(self, bookmark_id):
#         """Обработчик клика по заголовку закладки"""
#         self.bookmark_selected.emit(bookmark_id)
#
#     def on_search_changed(self, text):
#         """Обработчик изменения поискового запроса"""
#         self.load_bookmarks(text.strip())
#
#     def on_bookmark_clicked(self, item):
#         """Обработчик клика по закладке"""
#         if not item:
#             return
#
#         bookmark_id = item.data(Qt.ItemDataRole.UserRole)
#         self.bookmark_selected.emit(bookmark_id)
#
#     def show_context_menu(self, position):
#         """Показывает контекстное меню для закладки"""
#         item = self.bookmarks_list.itemAt(position)
#         if not item:
#             return
#
#         bookmark_id = item.data(Qt.ItemDataRole.UserRole)
#         bookmark = self.bookmark_manager.get(bookmark_id)
#
#         if not bookmark:
#             return
#
#         menu = QMenu(self)
#
#         # Открыть в браузере
#         open_action = QAction("🌐 Открыть в браузере", self)
#         open_action.triggered.connect(lambda: self.open_in_browser(bookmark.url))
#         menu.addAction(open_action)
#
#         # Копировать URL
#         copy_url_action = QAction("📋 Копировать URL", self)
#         copy_url_action.triggered.connect(lambda: self.copy_to_clipboard(bookmark.url))
#         menu.addAction(copy_url_action)
#
#         menu.addSeparator()
#
#         # Удалить
#         delete_action = QAction("🗑️ Удалить закладку", self)
#         delete_action.triggered.connect(lambda: self.delete_bookmark(bookmark_id))
#         menu.addAction(delete_action)
#
#         menu.exec(self.bookmarks_list.mapToGlobal(position))
#
#     def open_in_browser(self, url: str):
#         """Открывает URL в браузере по умолчанию"""
#         try:
#             webbrowser.open(url)
#             print(f"🌐 Открыто в браузере: {url}")
#         except Exception as e:
#             QMessageBox.warning(self, "Ошибка", f"Не удалось открыть URL: {e}")
#
#     def copy_to_clipboard(self, text: str):
#         """Копирует текст в буфер обмена"""
#         QApplication.clipboard().setText(text)
#         print(f"📋 Скопировано в буфер: {text}")
#
#     def delete_bookmark(self, bookmark_id: int):
#         """Удаляет закладку"""
#         reply = QMessageBox.question(
#             self,
#             "Подтверждение удаления",
#             "Вы уверены, что хотите удалить эту закладку?",
#             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
#             QMessageBox.StandardButton.No
#         )
#
#         if reply == QMessageBox.StandardButton.Yes:
#             success = self.bookmark_manager.delete(bookmark_id)
#             if success:
#                 self.bookmark_deleted.emit(bookmark_id)
#                 self.load_bookmarks(self.search_input.text())
#                 print(f"✅ Закладка {bookmark_id} удалена")
#             else:
#                 QMessageBox.warning(self, "Ошибка", "Не удалось удалить закладку")
#
#     def on_add_bookmark(self):
#         """Обработчик добавления новой закладки"""
#         from src.widgets.add_bookmark_dialog import AddBookmarkDialog
#
#         dialog = AddBookmarkDialog(self.bookmark_manager, self)
#         dialog.bookmark_added.connect(self.on_bookmark_added)
#         dialog.exec()
#
#     def on_bookmark_added(self):
#         """Обработчик добавления новой закладки"""
#         self.load_bookmarks(self.search_input.text())
#         print("✅ Новая закладка добавлена")
#
#     def refresh(self):
#         """Обновляет список закладок"""
#         self.load_bookmarks(self.search_input.text())
#
#     # В класс BookmarksWidget добавим:
#
#     def load_bookmarks_data(self, bookmarks):
#         """Загружает переданный список закладок (для фильтрации)"""
#         self.bookmarks_list.clear()
#
#         for bookmark in bookmarks:
#             # Создаем кастомный виджет для каждой закладки
#             bookmark_widget = self.create_bookmark_widget(bookmark)
#
#             # Создаем item для списка
#             item = QListWidgetItem()
#             item.setSizeHint(bookmark_widget.sizeHint())
#             item.setData(Qt.ItemDataRole.UserRole, bookmark.id)
#
#             self.bookmarks_list.addItem(item)
#             self.bookmarks_list.setItemWidget(item, bookmark_widget)
#
#         # Обновляем статистику
#         self.stats_label.setText(f"Закладок: {len(bookmarks)}")
#         print(f"✅ Отображено закладок: {len(bookmarks)}")