from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QMessageBox,
                             QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon


class AddBookmarkDialog(QDialog):
    """Диалог для добавления новой веб-закладки"""

    bookmark_added = pyqtSignal()  # Сигнал при успешном добавлении закладки

    def __init__(self, bookmark_manager, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("Добавить веб-закладку")
        self.setModal(True)
        self.resize(500, 300)

        layout = QVBoxLayout(self)

        # Поле для URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL страницы:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com или example.com")
        self.url_input.textChanged.connect(self.on_url_changed)

        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Поле для тегов
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Теги (через запятую):")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("работа, программирование, интересное")

        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.tags_input)
        layout.addLayout(tags_layout)

        # Предпросмотр метаданных
        preview_label = QLabel("Предпросмотр:")
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setPlaceholderText("Здесь появится информация о странице...")

        layout.addWidget(preview_label)
        layout.addWidget(self.preview_text)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.fetch_btn = QPushButton("Получить информацию")
        self.fetch_btn.clicked.connect(self.fetch_metadata)
        self.fetch_btn.setEnabled(False)

        self.add_btn = QPushButton("Добавить закладку")
        self.add_btn.clicked.connect(self.add_bookmark)
        self.add_btn.setEnabled(False)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(self.fetch_btn)
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def on_url_changed(self, text):
        """Обработчик изменения URL"""
        is_valid = self.bookmark_manager.validate_url(text)
        self.fetch_btn.setEnabled(is_valid)
        self.add_btn.setEnabled(False)

        if not text:
            self.preview_text.clear()

    def fetch_metadata(self):
        """Получает метаданные страницы"""
        url = self.url_input.text().strip()
        if not url:
            return

        # Показываем прогресс
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Индикатор без определенного конца
        self.fetch_btn.setEnabled(False)

        # Получаем метаданные
        metadata = self.bookmark_manager.parse_url_metadata(url)

        # Форматируем предпросмотр
        preview_text = f"Заголовок: {metadata.get('title', 'Не найден')}\n"
        preview_text += f"Описание: {metadata.get('description', 'Не найдено')}\n"
        preview_text += f"URL: {metadata.get('url', url)}\n"

        if metadata.get('status_code'):
            status_text = "✅ Успешно" if metadata['status_code'] == 200 else f"⚠️  Ошибка {metadata['status_code']}"
            preview_text += f"Статус: {status_text}"

        self.preview_text.setPlainText(preview_text)

        # Скрываем прогресс и активируем кнопку добавления
        self.progress_bar.setVisible(False)
        self.add_btn.setEnabled(True)

    def add_bookmark(self):
        """Добавляет закладку"""
        url = self.url_input.text().strip()
        tags_text = self.tags_input.text().strip()

        # Парсим теги
        tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []
        tags = [tag for tag in tags if tag]  # Убираем пустые

        # Показываем прогресс
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # ИСПРАВЛЕНИЕ: Используем правильный метод bookmark_manager
        bookmark = self.bookmark_manager.add_bookmark_with_metadata(url, tags)

        # Скрываем прогресс
        self.progress_bar.setVisible(False)

        if bookmark:
            QMessageBox.information(self, "Успех",
                                    f"Закладка '{bookmark.title}' успешно добавлена!")
            self.bookmark_added.emit()
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка",
                                "Не удалось добавить закладку. Проверьте URL и попробуйте снова.")
