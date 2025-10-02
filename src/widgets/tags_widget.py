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

    def __init__(self, tag_manager):
        super().__init__()
        self.tag_manager = tag_manager
        self.selected_tag = None
        self.setup_ui()
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
        self.stats_label.setStyleSheet("color: palette(mid); font-size: 11px; margin-top: 5px;")

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
        """Загрузка и отображение всех тегов"""
        self.tags_list.clear()
        tags = self.tag_manager.get_all()

        # Сортируем теги по имени
        tags.sort(key=lambda x: x.name)

        for tag in tags:
            item = QListWidgetItem(tag.name)
            item.setData(Qt.ItemDataRole.UserRole, tag.id)

            # Получаем количество заметок с этим тегом
            note_count = self.get_note_count_for_tag(tag.name)

            if note_count > 0:
                item.setText(f"{tag.name} ({note_count})")
                item.setToolTip(f"{note_count} заметок")
            else:
                item.setToolTip("Нет заметок")

            self.tags_list.addItem(item)

        # Восстанавливаем выделение если есть активный тег
        if self.selected_tag:
            self.select_tag_by_name(self.selected_tag)

        # Обновляем статистику
        self.stats_label.setText(f"Всего тегов: {len(tags)}")

        print(f"✅ Загружено тегов: {len(tags)}")

    def get_note_count_for_tag(self, tag_name):
        """Получает количество заметок для тега"""
        try:
            from src.core.database_manager import DatabaseManager
            from src.core.note_manager import NoteManager

            db = DatabaseManager()
            note_manager = NoteManager(db, self.tag_manager)
            notes = note_manager.search_by_tags([tag_name])
            return len(notes)
        except:
            return 0

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

        # Пытаемся создать тег
        tag = self.tag_manager.create(tag_name)
        if tag:
            self.tag_input.clear()
            self.load_tags()
            self.tag_created.emit(tag_name)
            print(f"✅ Тег '{tag_name}' создан")
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать тег '{tag_name}'")

    def on_tag_clicked(self, item):
        """Обработчик клика по тегу"""
        tag_name = self.extract_tag_name(item.text())

        # Если кликаем на уже выбранный тег - снимаем выделение
        if self.selected_tag == tag_name:
            self.clear_selection()
            print("🗑️ Сброшен фильтр по тегам")
            self.tag_selected.emit("")  # Явно отправляем пустую строку
        else:
            self.set_selected_tag(tag_name)
            print(f"🏷️ Выбран тег: {tag_name}")
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
        print("🗑️ Сброшен фильтр по тегам")

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
            f"Вы уверены, что хотите удалить тег '{tag_name}'?",
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

                print(f"✅ Тег '{tag_name}' удален")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить тег '{tag_name}'")

    def refresh(self):
        """Обновление списка тегов"""
        self.load_tags()