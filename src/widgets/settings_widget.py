from datetime import datetime

from PyQt6.QtWidgets import (QWidget, QMessageBox, QFileDialog, QApplication)
from PyQt6.QtCore import pyqtSignal, QSettings, QDateTime, Qt, QDate
import json
import os
from src.gui.ui_settings_widget import Ui_SettingsWidget

class SettingsWidget(QWidget, Ui_SettingsWidget):
    """Виджет настроек приложения для встраивания в главное окно"""

    settings_changed = pyqtSignal()  # Сигнал при изменении настроек
    data_imported = pyqtSignal()  # Сигнал при импорте данных
    theme_changed = pyqtSignal(str)  # Сигнал при изменении темы

    def __init__(self, note_manager, current_workspace_id=1, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.note_manager = note_manager
        self.settings = QSettings("SmartOrganizer", "SmartOrganizer")
        self.current_workspace_id = current_workspace_id
        self.original_settings = {}
        print(f"🔧 SettingsWidget.__init__:")
        print(f"   Переданный current_workspace_id: {current_workspace_id}")
        print(f"   self.current_workspace_id установлен в: {self.current_workspace_id}")

        # ДОБАВЬТЕ ОТЛАДКУ
        print(f"🔧 SettingsWidget инициализирован с workspace_id: {self.current_workspace_id}")
        print(f"🔧 Переданный current_workspace_id: {current_workspace_id}")

        # Если note_manager не передан, отключаем функции импорта/экспорта
        if self.note_manager is None:
            self.import_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            self.import_btn.setToolTip("Импорт недоступен: менеджер заметок не инициализирован")
            self.export_btn.setToolTip("Экспорт недоступен: менеджер заметок не инициализирован")
            print("⚠️  Менеджер заметок не передан, импорт/экспорт отключен")

        self.setup_connections()
        self.load_settings()
        self.update_apply_button()

    def setup_connections(self):
        """Настраивает соединения сигналов"""
        self.apply_btn.clicked.connect(self.apply_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        self.import_btn.clicked.connect(self.import_notes)
        self.export_btn.clicked.connect(self.export_notes)

        # Отслеживаем изменения для кнопки "Применить"
        self.theme_combo.currentIndexChanged.connect(self.on_setting_changed)
        self.auto_save_check.stateChanged.connect(self.on_setting_changed)
        self.load_session_check.stateChanged.connect(self.on_setting_changed)

    def load_settings(self):
        """Загружает текущие настройки"""
        # Тема оформления
        theme = self.settings.value("appearance/theme", "system", type=str)
        theme_index = {"system": 0, "light": 1, "dark": 2}.get(theme, 0)
        self.theme_combo.setCurrentIndex(theme_index)

        # Автосохранение
        auto_save = self.settings.value("behavior/auto_save", True, type=bool)
        self.auto_save_check.setChecked(auto_save)

        # Загрузка сессии
        load_session = self.settings.value("behavior/load_session", True, type=bool)
        self.load_session_check.setChecked(load_session)

        # Сохраняем оригинальные настройки для сравнения
        self.original_settings = self.get_current_settings()

    def get_current_workspace_id(self) -> int:
        """Возвращает ID текущего рабочего пространства"""
        # ПРОСТО ВОЗВРАЩАЕМ self.current_workspace_id
        print(f"🔧 get_current_workspace_id: возвращаем {self.current_workspace_id}")
        return self.current_workspace_id

    def get_current_settings(self):
        """Возвращает текущие настройки из UI"""
        theme_map = {0: "system", 1: "light", 2: "dark"}
        return {
            "theme": theme_map[self.theme_combo.currentIndex()],
            "auto_save": self.auto_save_check.isChecked(),
            "load_session": self.load_session_check.isChecked()
        }

    def on_setting_changed(self):
        """Обработчик изменения любой настройки"""
        self.update_apply_button()

    def update_apply_button(self):
        """Обновляет состояние кнопки 'Применить'"""
        current_settings = self.get_current_settings()
        has_changes = current_settings != self.original_settings

        self.apply_btn.setEnabled(has_changes)

        if has_changes:
            self.apply_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: 1px solid #45a049;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
        else:
            self.apply_btn.setStyleSheet("""
                QPushButton {
                    background-color: #cccccc;
                    color: #666666;
                    border: 1px solid #bbbbbb;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: normal;
                }
            """)

    def apply_settings(self):
        """Применяет настройки"""
        try:
            current_settings = self.get_current_settings()

            # Сохраняем настройки
            self.settings.setValue("appearance/theme", current_settings["theme"])
            self.settings.setValue("behavior/auto_save", current_settings["auto_save"])
            self.settings.setValue("behavior/load_session", current_settings["load_session"])

            self.settings.sync()

            # Обновляем оригинальные настройки
            self.original_settings = current_settings
            self.update_apply_button()

            # Отправляем сигналы
            self.settings_changed.emit()
            self.theme_changed.emit(current_settings["theme"])

            QMessageBox.information(self, "Успех", "Настройки применены!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить настройки: {str(e)}")

    def reset_settings(self):
        """Сбрасывает настройки к исходным значениям"""
        reply = QMessageBox.question(
            self,
            "Сброс настроек",
            "Вернуть настройки к исходным значениям?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.load_settings()  # Перезагружаем оригинальные настройки
            self.update_apply_button()
            QMessageBox.information(self, "Успех", "Настройки сброшены!")

    def import_notes(self):
        """Импортирует заметки, закладки и задачи из JSON файла в текущий workspace"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Импорт данных из JSON",
                "",
                "JSON Files (*.json);;All Files (*)"
            )

            if not file_path:
                return

            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Проверяем структуру данных
            if not isinstance(data, dict):
                QMessageBox.warning(self, "Ошибка", "Некорректный формат файла")
                return

            current_workspace_id = self.current_workspace_id

            print(f"🔧 ИМПОРТ: начинаем импорт в workspace {current_workspace_id}")

            # Подсчитываем элементы для импорта
            notes_count = len(data.get('notes', []))
            bookmarks_count = len(data.get('bookmarks', []))
            web_bookmarks_count = len(data.get('web_bookmarks', []))
            tasks_count = len(data.get('tasks', []))

            total_count = notes_count + bookmarks_count + web_bookmarks_count + tasks_count

            if total_count == 0:
                QMessageBox.information(self, "Информация", "В файле нет данных для импорта")
                return

            # ИЗМЕНЕНИЕ: предупреждение о смене workspace_id
            file_workspace_id = data.get('workspace_id', 'unknown')
            if file_workspace_id != current_workspace_id:
                reply = QMessageBox.question(
                    self,
                    "Разные workspace",
                    f"Файл был экспортирован из workspace {file_workspace_id}, "
                    f"но вы импортируете в workspace {current_workspace_id}.\n\n"
                    "Все данные будут импортированы в текущий workspace.\n\n"
                    "Продолжить?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            # Подтверждение импорта
            reply = QMessageBox.question(
                self,
                "Подтверждение импорта",
                f"Будет импортировано в workspace {current_workspace_id}:\n"
                f"• Заметок: {notes_count}\n"
                f"• Закладок (из notes): {bookmarks_count}\n"
                f"• Закладок (из bookmarks): {web_bookmarks_count}\n"
                f"• Задач: {tasks_count}\n\n"
                "Существующие данные не будут удалены.\n\n"
                "Продолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Импортируем данные
            imported_notes = 0
            imported_bookmarks = 0
            imported_web_bookmarks = 0
            imported_tasks = 0

            # Импорт заметок - ИГНОРИРУЕМ workspace_id из файла
            for note_data in data.get('notes', []):
                try:
                    # ИЗМЕНЕНИЕ: импортируем ВСЕ заметки независимо от workspace_id
                    note = self.note_manager.create(
                        title=note_data.get('title', 'Без названия'),
                        content=note_data.get('content', ''),
                        tags=note_data.get('tags', []),
                        content_type=note_data.get('content_type', 'plain'),
                        note_type='note',
                        workspace_id=current_workspace_id  # Используем текущий workspace
                    )
                    if note:
                        imported_notes += 1
                        print(f"   ✅ Импортирована заметка: {note.title}")
                    else:
                        print(f"   ❌ Не удалось импортировать заметку: {note_data.get('title')}")
                except Exception as e:
                    print(f"❌ Ошибка при импорте заметки: {e}")

            # Импорт закладок из таблицы notes - ИГНОРИРУЕМ workspace_id из файла
            for bookmark_data in data.get('bookmarks', []):
                try:
                    # ИЗМЕНЕНИЕ: импортируем ВСЕ закладки независимо от workspace_id
                    bookmark = self.note_manager.create_bookmark(
                        url=bookmark_data.get('url', ''),
                        title=bookmark_data.get('title', ''),
                        description=bookmark_data.get('description', ''),
                        tags=bookmark_data.get('tags', []),
                        workspace_id=current_workspace_id  # Используем текущий workspace
                    )
                    if bookmark:
                        imported_bookmarks += 1
                        print(f"   ✅ Импортирована закладка из notes: {bookmark.title}")
                    else:
                        print(f"   ❌ Не удалось импортировать закладку из notes: {bookmark_data.get('title')}")
                except Exception as e:
                    print(f"❌ Ошибка при импорте закладки из notes: {e}")

            # Импорт закладок из таблицы bookmarks - ИГНОРИРУЕМ workspace_id из файла
            for web_bookmark_data in data.get('web_bookmarks', []):
                try:
                    # ИЗМЕНЕНИЕ: импортируем ВСЕ закладки независимо от workspace_id
                    web_bookmark = None
                    if hasattr(self.note_manager, 'bookmark_manager') and self.note_manager.bookmark_manager:
                        web_bookmark = self.note_manager.bookmark_manager.create(
                            url=web_bookmark_data.get('url', ''),
                            title=web_bookmark_data.get('title', ''),
                            description=web_bookmark_data.get('description', ''),
                            tags=web_bookmark_data.get('tags', []),
                            favicon_url=web_bookmark_data.get('favicon_url'),
                            workspace_id=current_workspace_id  # Используем текущий workspace
                        )

                    if web_bookmark:
                        imported_web_bookmarks += 1
                        print(f"   ✅ Импортирована закладка из bookmarks: {web_bookmark.title}")
                    else:
                        print(f"   ❌ Не удалось импортировать закладку из bookmarks: {web_bookmark_data.get('title')}")
                except Exception as e:
                    print(f"❌ Ошибка при импорте закладки из bookmarks: {e}")

            # Импорт задач - ИГНОРИРУЕМ workspace_id из файла
            # В функции импорта, в разделе импорта задач:
            # В функции import_notes, в разделе импорта задач:
            for task_data in data.get('tasks', []):
                try:
                    # ИСПРАВЛЕНИЕ: находим заметку для привязки задачи
                    task_title = task_data.get('title', '')
                    if not task_title or not task_title.strip():
                        task_description = task_data.get('description', '')
                        if task_description:
                            task_title = task_description[:50] + '...' if len(
                                task_description) > 50 else task_description
                        else:
                            task_title = 'Задача без названия'

                    # ИЩЕМ ЗАМЕТКУ ДЛЯ ПРИВЯЗКИ ЗАДАЧИ
                    note_id = self.find_note_for_task(task_data, current_workspace_id)

                    if note_id:
                        # Создаем задачу ПРИВЯЗАННУЮ К ЗАМЕТКЕ
                        task = self.note_manager.task_manager.create_task(
                            note_id=note_id,
                            description=task_data.get('description', ''),
                            due_date=datetime.fromisoformat(task_data['due_date']) if task_data.get(
                                'due_date') else None,
                            priority=task_data.get('priority', 'medium'),
                            is_completed=task_data.get('is_completed', False),
                            workspace_id=current_workspace_id
                        )

                        if task:
                            imported_tasks += 1
                            print(f"   ✅ Импортирована задача: '{task.description}' (привязана к заметке {note_id})")
                        else:
                            print(f"   ❌ Не удалось импортировать задачу: {task_title}")
                    else:
                        print(f"   ⚠️  Не найдена заметка для задачи: {task_title}")

                except Exception as e:
                    print(f"❌ Ошибка при импорте задачи: {e}")

            # Формируем сообщение о результате
            success_message = (
                f"Импорт завершен в workspace {current_workspace_id}:\n\n"
                f"✅ Заметок: {imported_notes}/{notes_count}\n"
                f"✅ Закладок (из notes): {imported_bookmarks}/{bookmarks_count}\n"
                f"✅ Закладок (из bookmarks): {imported_web_bookmarks}/{web_bookmarks_count}\n"
                f"✅ Задач: {imported_tasks}/{tasks_count}"
            )

            # Проверка данных после импорта
            print(f"🔧 ПРОВЕРКА ДАННЫХ ПОСЛЕ ИМПОРТА:")

            # Проверяем что действительно импортировалось
            imported_notes_check = self.note_manager.get_notes_by_workspace(current_workspace_id)
            imported_bookmarks_check = self.note_manager.get_all_bookmarks(current_workspace_id)
            imported_web_bookmarks_check = []
            if hasattr(self.note_manager, 'bookmark_manager') and self.note_manager.bookmark_manager:
                imported_web_bookmarks_check = self.note_manager.bookmark_manager.get_all(current_workspace_id)
            imported_tasks_check = self.note_manager.task_manager.get_tasks_by_workspace(current_workspace_id)

            print(f"   📝 Заметок в БД: {len(imported_notes_check)}")
            print(f"   🔖 Закладок из notes в БД: {len(imported_bookmarks_check)}")
            print(f"   🔖 Закладок из bookmarks в БД: {len(imported_web_bookmarks_check)}")
            print(f"   ✅ Задач в БД: {len(imported_tasks_check)}")

            # Детальная проверка
            print(f"🔍 ДЕТАЛЬНАЯ ПРОВЕРКА ИМПОРТИРОВАННЫХ ДАННЫХ:")
            for note in imported_notes_check:
                print(f"   📝 Заметка: '{note.title}' (ID: {note.id}, workspace: {note.workspace_id})")
            for bookmark in imported_bookmarks_check:
                print(
                    f"   🔖 Закладка из notes: '{bookmark.title}' (ID: {bookmark.id}, workspace: {bookmark.workspace_id})")
            for web_bookmark in imported_web_bookmarks_check:
                print(
                    f"   🔖 Закладка из bookmarks: '{web_bookmark.title}' (ID: {web_bookmark.id}, workspace: {web_bookmark.workspace_id})")
            for task in imported_tasks_check:
                print(f"   ✅ Задача: '{task.title}' (ID: {task.id}, workspace: {task.workspace_id})")

            if imported_notes + imported_bookmarks + imported_web_bookmarks + imported_tasks == total_count:
                QMessageBox.information(self, "Импорт завершен", success_message)
            else:
                QMessageBox.warning(self, "Импорт завершен",
                                    f"{success_message}\n\n"
                                    f"Некоторые элементы не были импортированы.")

            # Отправляем сигнал с обновлением данных
            self.data_imported.emit()

            # Прямое обновление интерфейса
            self.refresh_current_view()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать данные: {str(e)}")
            print(f"❌ Ошибка импорта: {e}")
            import traceback
            traceback.print_exc()

    def find_note_for_task(self, task_data, workspace_id):
        """Находит подходящую заметку для привязки задачи"""
        try:
            # Получаем все заметки workspace
            notes = self.note_manager.get_notes_by_workspace(workspace_id)

            if not notes:
                print(f"   ⚠️  В workspace {workspace_id} нет заметок для привязки задач")
                return None

            # Пытаемся найти заметку по заголовку из данных задачи
            task_note_title = task_data.get('note_title')
            if task_note_title:
                for note in notes:
                    if note.title == task_note_title:
                        print(f"   🔗 Найдена заметка по заголовку: '{note.title}' (ID: {note.id})")
                        return note.id

            # Если не нашли по заголовку, берем первую заметку
            first_note = notes[0]
            print(f"   🔗 Используем первую заметку: '{first_note.title}' (ID: {first_note.id})")
            return first_note.id

        except Exception as e:
            print(f"❌ Ошибка при поиске заметки для задачи: {e}")
            return None

    def refresh_current_view(self):
        """Обновляет текущий вид после импорта данных"""
        try:
            # Получаем родительское окно (MainWindow)
            parent = self.parent()
            while parent and not hasattr(parent, 'refresh_all_widgets'):
                parent = parent.parent()

            if parent and hasattr(parent, 'refresh_all_widgets'):
                print("🔄 Вызываем обновление всех виджетов...")
                parent.refresh_all_widgets()
            else:
                print("⚠️  Не удалось найти MainWindow для обновления")

        except Exception as e:
            print(f"❌ Ошибка при обновлении вида: {e}")

    def update_workspace_id(self, new_workspace_id: int):
        """Обновляет текущий workspace_id"""
        print(f"🔧 Обновление workspace_id в SettingsWidget: {self.current_workspace_id} -> {new_workspace_id}")
        self.current_workspace_id = new_workspace_id

    def export_notes(self):
        """Экспортирует заметки, закладки и задачи текущего workspace в JSON файл"""
        try:
            # Получаем текущий workspace_id
            current_workspace_id = self.get_current_workspace_id()

            print(f"🔧 ЭКСПОРТ: current_workspace_id = {current_workspace_id}")

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Экспорт данных в JSON",
                f"workspace_{current_workspace_id}_backup_{QDate.currentDate().toString('yyyy-MM-dd')}.json",
                "JSON Files (*.json);;All Files (*)"
            )

            if not file_path:
                return

            # Получаем данные только для текущего workspace
            notes = self.note_manager.get_notes_by_workspace(current_workspace_id)
            bookmarks = self.note_manager.get_all_bookmarks(current_workspace_id)  # Закладки из таблицы notes
            web_bookmarks = self.note_manager.bookmark_manager.get_all(
                current_workspace_id)  # Закладки из таблицы bookmarks
            tasks = self.note_manager.task_manager.get_tasks_by_workspace(current_workspace_id)

            print(f"🔧 ДАННЫЕ ДЛЯ ЭКСПОРТА workspace {current_workspace_id}:")
            print(f"   📝 Заметок: {len(notes)}")
            print(f"   🔖 Закладок (из notes): {len(bookmarks)}")
            print(f"   🔖 Закладок (из bookmarks): {len(web_bookmarks)}")
            print(f"   ✅ Задач: {len(tasks)}")

            if not notes and not bookmarks and not web_bookmarks and not tasks:
                QMessageBox.information(self, "Информация",
                                        f"Нет данных для экспорта в workspace {current_workspace_id}")
                return

            # Подготавливаем данные для экспорта
            export_data = {
                "version": "1.0",
                "export_date": QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate),
                "app_name": QApplication.instance().applicationName(),
                "workspace_id": current_workspace_id,
                "notes_count": len(notes),
                "bookmarks_count": len(bookmarks),
                "web_bookmarks_count": len(web_bookmarks),
                "tasks_count": len(tasks),
                "notes": [],
                "bookmarks": [],  # Закладки из таблицы notes
                "web_bookmarks": [],  # ДОБАВЛЕНО: закладки из таблицы bookmarks
                "tasks": []
            }

            # Экспорт заметок
            for note in notes:
                if note.workspace_id == current_workspace_id and note.note_type == "note":
                    note_data = {
                        "title": note.title,
                        "content": note.content,
                        "tags": [tag.name for tag in note.tags],
                        "created_date": note.created_date.isoformat() if note.created_date else None,
                        "modified_date": note.modified_date.isoformat() if note.modified_date else None,
                        "content_type": note.content_type,
                        "note_type": note.note_type,
                        "workspace_id": note.workspace_id
                    }
                    export_data["notes"].append(note_data)

            # Экспорт закладок из таблицы notes
            for bookmark in bookmarks:
                if bookmark.workspace_id == current_workspace_id and bookmark.note_type == "bookmark":
                    bookmark_data = {
                        "title": bookmark.title,
                        "url": bookmark.url,
                        "description": bookmark.page_description or "",
                        "page_title": bookmark.page_title,
                        "tags": [tag.name for tag in bookmark.tags],
                        "created_date": bookmark.created_date.isoformat() if bookmark.created_date else None,
                        "modified_date": bookmark.modified_date.isoformat() if bookmark.modified_date else None,
                        "workspace_id": bookmark.workspace_id
                    }
                    export_data["bookmarks"].append(bookmark_data)

            # ДОБАВЛЕНО: Экспорт закладок из таблицы bookmarks
            for web_bookmark in web_bookmarks:
                if web_bookmark.workspace_id == current_workspace_id:
                    web_bookmark_data = {
                        "title": web_bookmark.title,
                        "url": web_bookmark.url,
                        "description": web_bookmark.description or "",
                        "favicon_url": web_bookmark.favicon_url,
                        "tags": [tag.name for tag in web_bookmark.tags],
                        "created_date": web_bookmark.created_date.isoformat() if web_bookmark.created_date else None,
                        "updated_date": web_bookmark.updated_date.isoformat() if web_bookmark.updated_date else None,
                        "workspace_id": web_bookmark.workspace_id
                    }
                    export_data["web_bookmarks"].append(web_bookmark_data)

            # Экспорт задач
            for task in tasks:
                if task.workspace_id == current_workspace_id:
                    task_data = {
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority,
                        "is_completed": task.is_completed,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "created_date": task.created_date.isoformat() if task.created_date else None,
                        "modified_date": task.modified_date.isoformat() if hasattr(task,
                                                                                   'modified_date') and task.modified_date else None,
                        "tags": [tag.name for tag in task.tags],
                        "workspace_id": task.workspace_id
                    }
                    export_data["tasks"].append(task_data)

            # Сохраняем в файл
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, ensure_ascii=False, indent=2)

            total_size = os.path.getsize(file_path) // 1024

            QMessageBox.information(
                self,
                "Экспорт завершен",
                f"✅ Успешно экспортировано из workspace {current_workspace_id}:\n\n"
                f"📝 Заметок: {len(notes)}\n"
                f"🔖 Закладок (из notes): {len(bookmarks)}\n"
                f"🔖 Закладок (из bookmarks): {len(web_bookmarks)}\n"
                f"✅ Задач: {len(tasks)}\n\n"
                f"📁 Файл: {os.path.basename(file_path)}\n"
                f"💾 Размер: {total_size} КБ"
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")
            print(f"❌ Ошибка экспорта: {e}")
            import traceback
            traceback.print_exc()

    def showEvent(self, event):
        """Обработчик показа виджета"""
        super().showEvent(event)
        # При показе виджета загружаем актуальные настройки
        self.load_settings()

    def get_settings_summary(self):
        """Возвращает текстовое описание текущих настроек"""
        current = self.get_current_settings()
        theme_names = {"system": "Системная", "light": "Светлая", "dark": "Тёмная"}

        return (f"Тема: {theme_names[current['theme']]}\n"
                f"Автосохранение: {'Вкл' if current['auto_save'] else 'Выкл'}\n"
                f"Загрузка сессии: {'Вкл' if current['load_session'] else 'Выкл'}")
