from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QLineEdit,
                             QPushButton, QHBoxLayout, QListWidgetItem, QMenu,
                             QMessageBox, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction, QColor, QPalette


class TagsWidget(QWidget):
    """Виджет для отображения и управления тегами в боковой панели"""

    tag_selected = pyqtSignal(str)  # Сигнал при выборе тега
    tag_created = pyqtSignal(str)  # Сигнал при создании тега
    tag_deleted = pyqtSignal(str)  # Сигнал при удалении тега

    def __init__(self, tag_manager, workspace_id=1, parent=None):
        super().__init__()
        self.tag_manager = tag_manager
        self.workspace_id = workspace_id
        self.selected_tag = None
        self.setup_ui()
        self.load_tags()

    def set_workspace(self, workspace_id):
        """Обновляет workspace и перезагружает теги"""
        self.workspace_id = workspace_id
        self.clear_selection()
        self.load_tags()

    def setup_ui(self):
        """Настройка интерфейса виджета"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Заголовок
        title_label = QLabel("Теги")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Поле для добавления новых тегов
        input_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Добавить тег...")
        self.tag_input.setMaxLength(50)
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(30, 30)
        self.add_button.setToolTip("Добавить тег")

        input_layout.addWidget(self.tag_input)
        input_layout.addWidget(self.add_button)

        # Список тегов
        self.tags_list = QListWidget()
        self.tags_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tags_list.setToolTip("Кликните для фильтрации по тегу\nПКМ для удаления")

        # Настраиваем стиль списка
        self.tags_list.setStyleSheet("""
            QListWidget {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid palette(midlight);
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QListWidget::item:hover {
                background-color: palette(alternate-base);
            }
        """)

        # Кнопка сброса фильтра
        self.clear_filter_btn = QPushButton("Сбросить фильтр")
        self.clear_filter_btn.setVisible(False)
        self.clear_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(mid);
                color: palette(text);
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)

        # Статистика
        self.stats_label = QLabel("Всего тегов: 0")
        self.stats_label.setStyleSheet("color: white; font-size: 11px; margin-top: 5px;")

        layout.addLayout(input_layout)
        layout.addWidget(self.tags_list)
        layout.addWidget(self.clear_filter_btn)
        layout.addWidget(self.stats_label)

        # Подключение сигналов
        self.add_button.clicked.connect(self.add_tag)
        self.tags_list.itemClicked.connect(self.on_tag_clicked)
        self.tags_list.customContextMenuRequested.connect(self.show_context_menu)
        self.tag_input.returnPressed.connect(self.add_tag)
        self.tag_input.textChanged.connect(self.on_input_changed)
        self.clear_filter_btn.clicked.connect(self.clear_selection)

    def on_input_changed(self, text):
        """Обновление состояния кнопки добавления"""
        self.add_button.setEnabled(bool(text.strip()))

    def load_tags(self):
        """Загрузка и отображение тегов для текущего workspace"""
        print(f"🔄 Загрузка тегов для workspace {self.workspace_id}")

        self.tags_list.clear()

        # Получаем теги только для текущего workspace
        tags = self.tag_manager.get_all(self.workspace_id)

        print(f"📋 Получено {len(tags)} тегов из базы данных для workspace {self.workspace_id}")

        # Сортируем теги по имени
        tags.sort(key=lambda x: x.name)

        for tag in tags:
            item = QListWidgetItem(tag.name)
            item.setData(Qt.ItemDataRole.UserRole, tag.id)

            # Получаем количество заметок и закладок с этим тегом в текущем workspace
            notes_count, bookmarks_count, total_count = self.get_note_count_for_tag(tag.name)

            # Форматируем текст в зависимости от наличия заметок и закладок
            # Используем иконки вместо текста
            if notes_count > 0 and bookmarks_count > 0:
                item.setText(f"{tag.name} (📝{notes_count} 🔖{bookmarks_count})")
                item.setToolTip(f"{notes_count} заметок и {bookmarks_count} закладок")
            elif notes_count > 0:
                item.setText(f"{tag.name} (📝{notes_count})")
                item.setToolTip(f"{notes_count} заметок")
            elif bookmarks_count > 0:
                item.setText(f"{tag.name} (🔖{bookmarks_count})")
                item.setToolTip(f"{bookmarks_count} закладок")
            else:
                item.setText(tag.name)
                item.setToolTip("Нет записей")

            self.tags_list.addItem(item)
            print(f"📝 Добавлен тег: {tag.name} ({notes_count} заметок, {bookmarks_count} закладок)")

        # Восстанавливаем выделение если есть активный тег
        if self.selected_tag:
            self.select_tag_by_name(self.selected_tag)

        # Обновляем статистику
        self.stats_label.setText(f"Тегов в workspace {self.workspace_id}: {len(tags)}")

        print(f"✅ Загружено {len(tags)} тегов для workspace {self.workspace_id}")

    def get_note_count_for_tag(self, tag_name):
        """Получает количество заметок И закладок для тега в текущем workspace"""
        try:
            # Считаем заметки в текущем workspace
            notes_with_tag = self.tag_manager.get_notes_by_tag(tag_name, self.workspace_id)

            # Считаем закладки в текущем workspace
            bookmarks_with_tag = self.get_bookmarks_by_tag(tag_name)

            notes_count = len(notes_with_tag)
            bookmarks_count = len(bookmarks_with_tag)
            total_count = notes_count + bookmarks_count

            # ДЕБАГ: выведем информацию о найденных записях
            print(
                f"🔍 Тег '{tag_name}': {notes_count} заметок + {bookmarks_count} закладок = {total_count} всего в workspace {self.workspace_id}")

            return notes_count, bookmarks_count, total_count

        except Exception as e:
            print(f"❌ Ошибка подсчета для тега {tag_name}: {e}")
            return 0, 0, 0

    def get_bookmarks_by_tag(self, tag_name):
        """Вспомогательный метод для получения закладок по тегу в текущем workspace"""
        try:
            from core.database_manager import DatabaseManager
            from core.bookmark_manager import BookmarkManager

            db = DatabaseManager()
            bookmark_manager = BookmarkManager(db)

            # Получаем все закладки и фильтруем по workspace и тегу
            all_bookmarks = bookmark_manager.get_all()

            bookmarks_with_tag = []
            for bookmark in all_bookmarks:
                # Проверяем workspace закладки
                bookmark_workspace_id = getattr(bookmark, 'workspace_id', 1)  # По умолчанию 1 если нет поля
                if bookmark_workspace_id != self.workspace_id:
                    continue

                # Проверяем теги закладки - ИСПРАВЛЕНО: точное совпадение
                bookmark_tags = [tag.name.lower() for tag in bookmark.tags] if hasattr(bookmark,
                                                                                       'tags') and bookmark.tags else []
                if tag_name.lower() in bookmark_tags:  # Это уже точное сравнение
                    bookmarks_with_tag.append(bookmark)

            print(f"📚 Для тега '{tag_name}' найдено {len(bookmarks_with_tag)} закладок в workspace {self.workspace_id}")
            return bookmarks_with_tag

        except Exception as e:
            print(f"❌ Ошибка получения закладок по тегу: {e}")
            return []

    def add_tag(self):
        """Добавление нового тега"""
        tag_name = self.tag_input.text().strip()
        if not tag_name:
            return

        # Проверяем валидность имени тега
        if len(tag_name) < 2:
            QMessageBox.warning(self, "Ошибка", "Имя тега должно содержать хотя бы 2 символа")
            return

        if len(tag_name) > 50:
            QMessageBox.warning(self, "Ошибка", "Имя тега не должно превышать 50 символов")
            return

        print(f"🔧 Создание тега '{tag_name}' в workspace {self.workspace_id}")

        # Пытаемся создать тег ДЛЯ ТЕКУЩЕГО WORKSPACE
        tag = self.tag_manager.create(tag_name, self.workspace_id)
        if tag:
            self.tag_input.clear()
            self.load_tags()
            self.tag_created.emit(tag_name)
            print(f"✅ Тег '{tag_name}' создан в workspace {self.workspace_id}")
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать тег '{tag_name}'")

    def on_tag_clicked(self, item):
        """Обработчик клика по тегу"""
        tag_name = self.extract_tag_name(item.text())

        # Если кликаем на уже выбранный тег - снимаем выделение
        if self.selected_tag == tag_name:
            self.clear_selection()
            print(f"🗑️ Сброшен фильтр по тегам в workspace {self.workspace_id}")
            self.tag_selected.emit("")  # Явно отправляем пустую строку
        else:
            self.set_selected_tag(tag_name)
            print(f"🏷️ Выбран тег: {tag_name} в workspace {self.workspace_id}")
            self.tag_selected.emit(tag_name)  # Отправляем имя тега

    def set_selected_tag(self, tag_name):
        """Устанавливает выбранный тег и обновляет выделение"""
        self.selected_tag = tag_name
        self.update_selection_visuals()
        self.clear_filter_btn.setVisible(bool(tag_name))

    def select_tag_by_name(self, tag_name):
        """Выбирает тег по имени (для внешнего использования)"""
        if not tag_name:
            self.clear_selection()
            return

        for i in range(self.tags_list.count()):
            item = self.tags_list.item(i)
            current_tag_name = self.extract_tag_name(item.text())
            if current_tag_name == tag_name:
                self.set_selected_tag(tag_name)
                # Устанавливаем выделение стандартными средствами QListWidget
                self.tags_list.setCurrentItem(item)
                # Прокручиваем к выбранному элементу
                self.tags_list.scrollToItem(item)
                break
        else:
            # Если тег не найден в списке, сбрасываем выделение
            self.clear_selection()

    def extract_tag_name(self, item_text):
        """Извлекает чистое имя тега из текста элемента (без счетчика)"""
        if " (" in item_text:
            return item_text.split(" (")[0]
        return item_text

    def update_selection_visuals(self):
        """Обновляет визуальное выделение тегов"""
        # QListWidget сам управляет выделением через setCurrentItem
        # Нам нужно только обновить состояние кнопки сброса
        self.clear_filter_btn.setVisible(bool(self.selected_tag))

    def clear_selection(self):
        """Снимает выделение со всех тегов"""
        self.selected_tag = None
        self.tags_list.clearSelection()
        self.clear_filter_btn.setVisible(False)
        self.tag_selected.emit("")  # Сигнал для сброса фильтра
        print(f"🗑️ Сброшен фильтр по тегам в workspace {self.workspace_id}")

    def get_selected_tag(self):
        """Возвращает выбранный тег"""
        return self.selected_tag

    def show_context_menu(self, position):
        """Показывает контекстное меню для тега"""
        item = self.tags_list.itemAt(position)
        if not item:
            return

        tag_name = self.extract_tag_name(item.text())
        tag_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)

        # Если тег не выбран, добавляем опцию фильтрации
        if self.selected_tag != tag_name:
            filter_action = QAction("Фильтровать по тегу", self)
            filter_action.triggered.connect(lambda: self.on_tag_clicked(item))
            menu.addAction(filter_action)

        delete_action = QAction("Удалить тег", self)
        delete_action.triggered.connect(lambda: self.delete_tag(tag_id, tag_name))
        menu.addAction(delete_action)

        menu.exec(self.tags_list.mapToGlobal(position))

    def delete_tag(self, tag_id, tag_name):
        """Удаление тега"""
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить тег '{tag_name}'?\n\n"
            f"Это действие удалит тег из всех записей в workspace {self.workspace_id}.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.tag_manager.delete(tag_id)
            if success:
                # Если удаляемый тег был выбран, снимаем выделение
                if self.selected_tag == tag_name:
                    self.clear_selection()

                self.load_tags()
                self.tag_deleted.emit(tag_name)

                print(f"✅ Тег '{tag_name}' удален из workspace {self.workspace_id}")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить тег '{tag_name}'")

    def refresh(self):
        """Обновление списка тегов"""
        self.load_tags()
