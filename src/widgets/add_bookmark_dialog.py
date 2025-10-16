from typing import Optional, List

from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt

from core.models import WebBookmark
from gui.ui_add_bookmark_dialog import Ui_AddBookmarkDialog


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

    def create_bookmark_with_custom_data(self, url: str, title: str = "", description: str = "",
                                         tags: Optional[List[str]] = None, workspace_id: int = 1) -> Optional[
        WebBookmark]:
        """
        Создает закладку с пользовательскими title и description
        """
        if not url or not url.strip():
            print("❌ Ошибка: URL не может быть пустым")
            return None

        # Нормализуем URL
        normalized_url = self.normalize_url(url)

        # Если заголовок не указан, используем домен из URL
        if not title.strip():
            from urllib.parse import urlparse
            parsed_url = urlparse(normalized_url)
            title = parsed_url.netloc or normalized_url

        print(f"🔍 Создание закладки с пользовательскими данными:")
        print(f"   - URL: {normalized_url}")
        print(f"   - Title: {title}")
        print(f"   - Description: {description}")
        print(f"   - Tags: {tags}")
        print(f"   - Workspace ID: {workspace_id}")

        # Создаем закладку с пользовательскими данными
        return self.safe_create_bookmark(
            url=normalized_url,
            title=title.strip(),
            description=description.strip(),
            tags=tags or [],
            workspace_id=workspace_id
        )

    def safe_create_bookmark(self, url: str, title: str = "", description: str = "",
                             tags: Optional[List[str]] = None, workspace_id: int = 1) -> Optional[WebBookmark]:
        """
        Безопасно создает закладку с обработкой ошибок
        """
        try:
            print(f"🔍 Отладка BookmarkManager.safe_create_bookmark():")
            print(f"   - URL: {url}")
            print(f"   - Title: {title}")
            print(f"   - Description: {description}")
            print(f"   - Tags: {tags}")
            print(f"   - Workspace ID: {workspace_id} (тип: {type(workspace_id)})")

            # Создаем закладку через основной метод create
            bookmark = self.create(
                url=url,
                title=title,
                description=description,
                tags=tags or [],
                workspace_id=workspace_id
            )

            if bookmark:
                print(f"✅ Закладка создана: {bookmark.title}")
            else:
                print("❌ Не удалось создать закладку")

            return bookmark

        except Exception as e:
            print(f"❌ Ошибка при создании закладки: {e}")
            import traceback
            traceback.print_exc()
            return None

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

            # Пробуем создать закладку с пользовательскими данными
            bookmark = None

            # Способ 1: Используем новый метод create_bookmark_with_custom_data
            if hasattr(self.bookmark_manager, 'create_bookmark_with_custom_data'):
                try:
                    bookmark = self.bookmark_manager.create_bookmark_with_custom_data(
                        url=url,
                        title=title,
                        description=description,
                        tags=tags,
                        workspace_id=self.workspace_id
                    )
                    print("✅ Использован метод create_bookmark_with_custom_data")
                except Exception as e:
                    print(f"❌ Ошибка в create_bookmark_with_custom_data: {e}")

            # Способ 2: Если нового метода нет, используем существующий и обновляем
            if not bookmark and hasattr(self.bookmark_manager, 'add_bookmark_with_metadata'):
                try:
                    # Создаем базовую закладку
                    bookmark = self.bookmark_manager.add_bookmark_with_metadata(
                        url=url,
                        tags=tags,
                        workspace_id=self.workspace_id
                    )

                    # Обновляем title и description если они указаны
                    if bookmark and (title or description):
                        success = self._update_bookmark_metadata(bookmark.id, title, description)
                        if success:
                            print("✅ Закладка создана и обновлена с пользовательскими данными")
                        else:
                            print("⚠️ Закладка создана, но не удалось обновить метаданные")
                    else:
                        print("✅ Закладка создана (без пользовательских данных)")

                except Exception as e:
                    print(f"❌ Ошибка в add_bookmark_with_metadata: {e}")

            if bookmark:
                print(f"✅ Закладка добавлена в workspace {self.workspace_id}: {bookmark.title}")
                print(f"   🔗 URL: {bookmark.url}")
                print(f"   📝 Описание: {getattr(bookmark, 'description', 'N/A')}")
                print(f"   🏷️ Теги: {[tag.name for tag in getattr(bookmark, 'tags', [])]}")

                self.bookmark_added.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить закладку")

        except Exception as e:
            print(f"❌ Ошибка при добавлении закладки: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении закладки: {str(e)}")

    def _update_bookmark_metadata(self, bookmark_id, title, description):
        """Обновляет метаданные закладки после создания"""
        try:
            print(f"🔍 Обновление метаданных закладки {bookmark_id}:")
            print(f"   - Title: {title}")
            print(f"   - Description: {description}")

            success = False

            # Пробуем разные методы обновления
            if hasattr(self.bookmark_manager, 'update_bookmark'):
                success = self.bookmark_manager.update_bookmark(
                    bookmark_id,
                    title=title,
                    description=description
                )
                print("✅ Использован метод update_bookmark")
            elif hasattr(self.bookmark_manager, 'update'):
                success = self.bookmark_manager.update(
                    bookmark_id,
                    title=title,
                    description=description
                )
                print("✅ Использован метод update")

            if success:
                print(f"✅ Метаданные закладки {bookmark_id} обновлены")
            else:
                print(f"❌ Не удалось обновить метаданные закладки {bookmark_id}")

            return success

        except Exception as e:
            print(f"❌ Ошибка обновления метаданных: {e}")
            return False
