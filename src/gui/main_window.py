import os

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication

from core.settings_manager import QtSettingsManager
from gui.ui_main_window import Ui_MainWindow
from widgets.notes_widget import NotesWidget
from widgets.bookmarks_widget import BookmarksWidget
from widgets.upcoming_tasks_widget import UpcomingTasksWidget
from widgets.settings_widget import SettingsWidget
from widgets.workspaces_widget import WorkspacesWidget
from core.task_manager import TaskManager
from core.bookmark_manager import BookmarkManager
from core.database_manager import DatabaseManager
from core.tag_manager import TagManager
from core.note_manager import NoteManager
from core.workspace_manager import WorkspaceManager
from core.theme_manager import ThemeManager


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.workspace_manager = None
        self.bookmark_manager = None
        self.task_manager = None
        self.note_manager = None
        self.tag_manager = None
        self.db_manager = None
        self.theme_manager = None

        # Инициализация менеджера настроек ПЕРВЫМ делом
        self.settings_manager = QtSettingsManager()

        # Инициализация менеджера тем ВТОРЫМ делом
        self.theme_manager = ThemeManager()

        # Загружаем последний workspace из настроек
        self.current_workspace_id = self.settings_manager.get_last_workspace()
        print(f"🔧 MainWindow инициализирован с workspace_id: {self.current_workspace_id}")

        self.setupUi(self)
        self.current_widget = None

        self.setup_ui()
        self.setup_icons()
        self.setup_managers()
        self.connect_signals()

        # ПРИМЕНЯЕМ ТЕМУ ПРИ ЗАПУСКЕ
        self.apply_theme_on_startup()
        self.apply_styles()

        self.show_notes_widget()

    def setup_ui(self):
        """Настройка дополнительных параметров UI"""
        self.setWindowTitle("MINDSPACE")
        self.setMinimumSize(1100, 600)
        self.splitter.setSizes([100, 600])

        if self.widgetConteiner.layout() is None:
            layout = QtWidgets.QVBoxLayout(self.widgetConteiner)
            layout.setContentsMargins(0, 0, 0, 0)
            print("✅ Layout контейнера создан")
        else:
            print("✅ Layout контейнера уже существует")

    def setup_icons(self, theme_name=None):
        """Устанавливает иконки для кнопок в зависимости от темы"""
        if theme_name is None:
            theme_name = self.theme_manager.get_effective_theme_name()

        icon_size = QSize(24, 24)
        color = "white" if theme_name == "dark" else "black"
        icon_path = "assets/icons/app_icon.png"

        if os.path.exists(icon_path):
            self.titleLabel.setText(f"""
                    <html>
                    <body>
                        <div align="center">
                            <table cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                                <tr>
                                    <td style="vertical-align: middle;">
                                        <img src="{icon_path}" width="32" height="32"/>
                                    </td>
                                    <td style="vertical-align: middle; padding-left: 10px;">
                                        <span style="color: {color}; font-size: 28px; font-family: 'Segoe UI', Arial, sans-serif; font-weight: 900;">
                                            MINDSPACE
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </div>
                    </body>
                    </html>
                """)
        else:
            self.titleLabel.setText(f"""
                    <html>
                    <body>
                        <div align="center">
                            <span style="color: {color}; font-size: 28px; font-family: 'Segoe UI', Arial, sans-serif; font-weight: 900;">
                                MINDSPACE
                            </span>
                        </div>
                    </body>
                    </html>
                """)

        # Выбираем иконки в зависимости от темы
        if theme_name == "light":
            buttons_icons = {
                'btnTasks': 'assets/icons/checkbox-line.png',
                'btnNotes': 'assets/icons/sticky-note-line.png',
                'btnBookmarks': 'assets/icons/bookmark-line.png',
                'btnWorkspaces': 'assets/icons/folder-line.png',
                'btnSettings': 'assets/icons/settings-line.png'
            }
        else:  # dark
            buttons_icons = {
                'btnTasks': 'assets/icons/checkbox-line-light.png',
                'btnNotes': 'assets/icons/sticky-note-line-light.png',
                'btnBookmarks': 'assets/icons/bookmark-line-light.png',
                'btnWorkspaces': 'assets/icons/folder-line-light.png',
                'btnSettings': 'assets/icons/settings-line-light.png'
            }

        print(f"🎨 Установка иконок для темы: {theme_name}")

        for button_name, icon_path in buttons_icons.items():
            button = getattr(self, button_name)

            # Проверяем существование файла
            if os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
                print(f"✅ Установлена иконка для {button_name}: {icon_path}")
            else:
                # Если файл не найден, пробуем альтернативный путь
                alt_path = self.find_icon_file(icon_path)
                if alt_path:
                    button.setIcon(QIcon(alt_path))
                    print(f"✅ Установлена иконка для {button_name} (альтернативный путь): {alt_path}")
                else:
                    print(f"⚠️ Файл иконки не найден: {icon_path}")
                    # Можно использовать встроенные иконки Qt как запасной вариант
                    button.setIcon(QIcon())

            button.setIconSize(icon_size)

    def find_icon_file(self, icon_path):
        """Пытается найти файл иконки по разным путям"""
        possible_paths = [
            icon_path,
            f"src/{icon_path}",
            f"../{icon_path}",
            f"../../{icon_path}",
            os.path.join(os.path.dirname(__file__), icon_path),
            os.path.join(os.path.dirname(__file__), "..", icon_path)
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def setup_managers(self):
        db_path = "smart_organizer.db"
        self.db_manager = DatabaseManager(db_path)
        self.tag_manager = TagManager(self.db_manager)
        self.workspace_manager = WorkspaceManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        self.task_manager = TaskManager(self.db_manager)
        self.bookmark_manager = BookmarkManager(self.db_manager)
        self.workspace_manager.workspaceDeleted.connect(self.on_workspace_deleted)
        print("✅ Все менеджеры инициализированы")

    def apply_theme_on_startup(self):
        """Применяет тему при запуске приложения"""
        # Получаем сохраненную тему из настроек
        saved_theme = self.theme_manager.get_current_theme()
        effective_theme = self.theme_manager.get_effective_theme_name()

        print(f"🎨 Загружена тема из настроек: {saved_theme}")
        print(f"🎨 Эффективная тема: {effective_theme}")

        # Применяем тему
        self.theme_manager.apply_theme(saved_theme)

        # ОБНОВЛЯЕМ ИКОНКИ при запуске с правильной темой
        self.setup_icons(effective_theme)

    def apply_styles(self):
        """Принудительное применение стилей"""
        # Базовый стиль для неактивных кнопок
        if self.theme_manager.current_theme == "dark":
            self.inactive_style = """
                QPushButton {
                    margin: 0px;
                    padding: 12px 8px;
                    border: none;
                    border-top: 1px solid #e0e0e0;
                    border-bottom: 1px solid #e0e0e0;
                    border-radius: 0px;
                    text-align: left;
                    background-color: #0d1117;
                }
                QPushButton:hover {
                    background-color: #ad420f;
                }
                QPushButton:pressed {
                    background-color: #0d1117;
                }
            """
        else:
            self.inactive_style = """
                QPushButton {
                    margin: 0px;
                    padding: 12px 8px;
                    border: none;
                    border-top: 1px solid #e0e0e0;
                    border-bottom: 1px solid #e0e0e0;
                    border-radius: 0px;
                    text-align: left;
                    background-color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #e1885e;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
            """

        # Стиль для активной кнопки
        self.active_style = """
            QPushButton {
                margin: 0px;
                padding: 12px 8px;
                border: none;
                border-top: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 0px;
                text-align: left;
                background-color: #E16428;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E16428;
            }
            
        """
        if self.theme_manager.current_theme == "dark":
            self.active_style += """
                        QPushButton:pressed {
                            background-color: #ffff;
                        }
                        """
        else:
            self.active_style += """
                        QPushButton:pressed {
                            background-color: #fffff;
                        }
                        """

        # Изначально все кнопки неактивны
        buttons = [
            self.btnTasks,
            self.btnNotes,
            self.btnBookmarks,
            self.btnWorkspaces,
            self.btnSettings
        ]

        for button in buttons:
            button.setStyleSheet(self.inactive_style)

    def connect_signals(self):
        """Подключение сигналов кнопок"""
        self.btnNotes.clicked.connect(self.show_notes_widget)
        self.btnTasks.clicked.connect(self.show_tasks_widget)
        self.btnBookmarks.clicked.connect(self.show_bookmarks_widget)
        self.btnWorkspaces.clicked.connect(self.show_workspaces_widget)
        self.btnSettings.clicked.connect(self.show_settings_widget)

    def set_content_widget(self, widget):
        """Установка виджета в контейнер"""
        # Удаляем текущий виджет
        if self.current_widget:
            self.current_widget.setParent(None)
            self.current_widget.deleteLater()

        # Устанавливаем новый виджет
        self.current_widget = widget
        layout = self.widgetConteiner.layout()
        layout.addWidget(widget)

    def show_notes_widget(self):
        """Показать виджет заметок"""
        try:
            # Передаем текущий workspace_id в виджет заметок
            notes_widget = NotesWidget(
                workspace_id=self.current_workspace_id
            )
            self.set_content_widget(notes_widget)
            self.reset_other_buttons(self.btnNotes)
        except Exception as e:
            print(f"Ошибка при создании виджета заметок: {e}")
            self.show_placeholder("Виджет заметок")

    def show_tasks_widget(self):
        """Показать виджет задач"""
        try:
            # Передаем текущий workspace_id в виджет задач
            tasks_widget = UpcomingTasksWidget(
                self.task_manager,
                self.note_manager,
                workspace_id=self.current_workspace_id
            )

            # Устанавливаем parent после создания
            tasks_widget.setParent(self)

            # Подключаем сигнал перехода к заметке
            tasks_widget.navigate_to_note_requested.connect(self.navigate_to_note_from_task)

            self.set_content_widget(tasks_widget)
            self.reset_other_buttons(self.btnTasks)
        except Exception as e:
            print(f"Ошибка при создании виджета задач: {e}")
            import traceback
            traceback.print_exc()
            self.show_placeholder("Виджет задач")

    def navigate_to_note_from_task(self, note_id):
        """Переходит к заметке из виджета задач"""
        print(f"🔄 Запрос перехода к заметке {note_id} из виджета задач")

        # Переключаемся на виджет заметок
        self.show_notes_widget()

        # Даем время на создание виджета заметок
        QtCore.QTimer.singleShot(100, lambda: self.open_note_in_notes_widget(note_id))

    def open_note_in_notes_widget(self, note_id):
        """Открывает конкретную заметку в виджете заметок"""
        if hasattr(self.current_widget, 'navigate_to_note_by_id'):
            self.current_widget.navigate_to_note_by_id(note_id)
            print(f"✅ Заметка {note_id} открыта в редакторе")
        else:
            print(f"❌ Не удалось открыть заметку {note_id}: виджет заметок не поддерживает навигацию")

    def show_bookmarks_widget(self):
        """Показать виджет закладок"""
        try:
            # Передаем текущий workspace_id в виджет закладок
            bookmarks_widget = BookmarksWidget(
                bookmark_manager=self.bookmark_manager,
                workspace_id=self.current_workspace_id
            )
            self.set_content_widget(bookmarks_widget)
            self.reset_other_buttons(self.btnBookmarks)
        except Exception as e:
            print(f"Ошибка при создании виджета закладок: {e}")
            self.show_placeholder("Виджет закладок")

    def show_workspaces_widget(self):
        """Показать виджет рабочих пространств"""
        try:
            # Передаем workspace_manager и текущий workspace_id
            workspaces_widget = WorkspacesWidget(
                workspace_manager=self.workspace_manager,
                current_workspace_id=self.current_workspace_id  # Убедитесь, что передается актуальный
            )

            # ДОБАВЬТЕ ОТЛАДКУ
            print(f"🔧 Создание WorkspacesWidget с workspace_id: {self.current_workspace_id}")

            # Подключаем сигнал изменения workspace
            workspaces_widget.workspaceChanged.connect(self.on_workspace_changed)

            self.set_content_widget(workspaces_widget)
            self.reset_other_buttons(self.btnWorkspaces)
        except Exception as e:
            print(f"Ошибка при создании виджета рабочих пространств: {e}")
            import traceback
            traceback.print_exc()
            self.show_placeholder("Виджет рабочих пространств")

    def on_workspace_changed(self, workspace_id):
        """Обрабатывает изменение рабочего пространства"""
        print(f"🔄 Изменение workspace: {self.current_workspace_id} -> {workspace_id}")

        # Сохраняем новый workspace в настройках сразу при изменении
        self.settings_manager.set_last_workspace(workspace_id)

        # Обновляем текущий workspace
        self.current_workspace_id = workspace_id

        # ДОБАВЬТЕ ПРОВЕРКУ
        print(f"🔧 Текущий workspace после изменения: {self.current_workspace_id}")

        # ОБНОВЛЯЕМ SettingsWidget если он активен
        if (self.current_widget and
                hasattr(self.current_widget, '__class__') and
                self.current_widget.__class__.__name__ == 'SettingsWidget'):
            self.current_widget.update_workspace_id(workspace_id)
            print(f"✅ SettingsWidget обновлен с новым workspace_id: {workspace_id}")

        # Обновляем текущий виджет, если он поддерживает обновление workspace
        if self.current_widget and hasattr(self.current_widget, 'set_workspace'):
            self.current_widget.set_workspace(workspace_id)
            print(f"✅ Текущий виджет обновлен для workspace {workspace_id}")

    def setup_settings_tab(self):
        """Создает и настраивает вкладку настроек"""
        from widgets.settings_widget import SettingsWidget

        # Создаем виджет настроек
        self.settings_widget = SettingsWidget(self.note_manager, self.current_workspace_id, self)

        # Подключаем сигналы
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        self.settings_widget.data_imported.connect(self.on_data_imported)
        self.settings_widget.theme_changed.connect(self.on_theme_changed)

        # Добавляем вкладку настроек (если используется QTabWidget)
        if hasattr(self, 'main_tabs'):
            self.main_tabs.addTab(self.settings_widget, "⚙️ Настройки")

        # Или добавляем в stacked widget (если используется QStackedWidget)
        elif hasattr(self, 'content_stack'):
            self.content_stack.addWidget(self.settings_widget)

    def on_settings_changed(self):
        """Обработчик изменения настроек"""
        print("✅ Настройки изменены")
        # Можно обновить что-то в интерфейсе

    def on_data_imported(self):
        """Обработчик импорта данных"""
        print("✅ Данные импортированы")
        self.refresh_all_widgets()  # Обновляем интерфейс

    def on_theme_changed(self, theme_name):
        """Обработчик изменения темы"""
        print(f"🎨 Тема изменена на: {theme_name}")
        # Применяем новую тему через ThemeManager
        self.theme_manager.set_theme(theme_name)
        # ПЕРЕЗАГРУЖАЕМ ИКОНКИ после смены темы
        self.apply_styles()
        self.setup_icons(theme_name)

    def apply_theme(self, theme_name):
        """Устаревший метод - используйте theme_manager вместо этого"""
        print(f"⚠️  Используется устаревший метод apply_theme, используйте theme_manager")
        self.theme_manager.set_theme(theme_name)

    def show_settings(self):
        """Переключает на вкладку настроек"""
        if hasattr(self, 'main_tabs'):
            # Находим индекс вкладки настроек
            for i in range(self.main_tabs.count()):
                if self.main_tabs.tabText(i) == "⚙️ Настройки":
                    self.main_tabs.setCurrentIndex(i)
                    break
        elif hasattr(self, 'content_stack'):
            # Переключаем на виджет настроек в stacked widget
            self.content_stack.setCurrentWidget(self.settings_widget)

    def show_settings_widget(self):
        """Показать виджет настроек"""
        try:
            # ИСПРАВЛЕНИЕ: передаем АКТУАЛЬНЫЙ workspace_id
            settings_widget = SettingsWidget(
                note_manager=self.note_manager,
                current_workspace_id=self.current_workspace_id,  # Используем текущий workspace
                parent=self
            )

            # ДОБАВЬТЕ ОТЛАДКУ
            print(f"🔧 Создание SettingsWidget с workspace_id: {self.current_workspace_id}")

            # ПОДКЛЮЧАЕМ СИГНАЛ ИЗМЕНЕНИЯ ТЕМЫ
            settings_widget.theme_changed.connect(self.on_theme_changed)

            self.set_content_widget(settings_widget)
            self.reset_other_buttons(self.btnSettings)
        except Exception as e:
            print(f"Ошибка при создании виджета настроек: {e}")
            import traceback
            traceback.print_exc()
            self.show_placeholder("Виджет настроек")

    def show_placeholder(self, text):
        """Показать заглушку если виджет не реализован"""
        placeholder = QtWidgets.QLabel(f"<h2>{text}</h2><p>Этот раздел в разработке</p>")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_content_widget(placeholder)

    def reset_other_buttons(self, active_button):
        """Сбросить стили других кнопок"""
        buttons = [
            self.btnNotes,
            self.btnTasks,
            self.btnBookmarks,
            self.btnWorkspaces,
            self.btnSettings
        ]

        # Сначала устанавливаем всем неактивный стиль
        for button in buttons:
            button.setStyleSheet(self.inactive_style)

        # Затем устанавливаем активный стиль для выбранной кнопки
        active_button.setStyleSheet(self.active_style)

    def on_workspace_deleted(self, deleted_workspace_id: int):
        """Обрабатывает удаление рабочего пространства"""
        print(f"🗑️ Workspace {deleted_workspace_id} был удален")

        # Если удалили текущий workspace, переключаемся на default
        if deleted_workspace_id == self.current_workspace_id:
            default_workspace = self.workspace_manager.get_default_workspace()
            if default_workspace:
                self.current_workspace_id = default_workspace.id
                print(f"🔄 Переключение на workspace по умолчанию: {self.current_workspace_id}")

                # Сохраняем новый workspace в настройках
                self.settings_manager.set_last_workspace(self.current_workspace_id)

                # Обновляем текущий виджет
                if self.current_widget and hasattr(self.current_widget, 'set_workspace'):
                    self.current_widget.set_workspace(self.current_workspace_id)

        # ОСОБОЕ ОБНОВЛЕНИЕ: если текущий виджет - WorkspacesWidget, перезагружаем его
        if (self.current_widget and
                hasattr(self.current_widget, '__class__') and
                self.current_widget.__class__.__name__ == 'WorkspacesWidget'):
            print("🔄 Перезагружаем виджет рабочих пространств...")
            self.current_widget.load_workspaces()

        # Обновляем все виджеты которые могут показывать workspace-зависимые данные
        self.refresh_all_widgets()

    def refresh_all_widgets(self):
        """Обновляет все виджеты которые зависят от workspace"""
        print("🔄 ОБНОВЛЕНИЕ ВСЕХ ВИДЖЕТОВ...")

        # Если текущий виджет поддерживает обновление - обновляем его
        if self.current_widget and hasattr(self.current_widget, 'refresh'):
            print(f"🔄 Обновляем текущий виджет: {self.current_widget.__class__.__name__}")
            self.current_widget.refresh()

        # Также обновляем другие виджеты которые могут быть открыты
        # Например, если открыт виджет заметок, обновляем его данные
        if hasattr(self, 'notes_widget') and self.notes_widget:
            if hasattr(self.notes_widget, 'refresh'):
                self.notes_widget.refresh()

        if hasattr(self, 'bookmarks_widget') and self.bookmarks_widget:
            if hasattr(self.bookmarks_widget, 'refresh'):
                self.bookmarks_widget.refresh()

        if hasattr(self, 'tasks_widget') and self.tasks_widget:
            if hasattr(self.tasks_widget, 'refresh'):
                self.tasks_widget.refresh()

        print("✅ Все виджеты обновлены")

    def restore_window_state(self):
        """Восстанавливает состояние окна"""
        geometry = self.settings_manager.get_window_geometry()
        state = self.settings_manager.get_window_state()

        if geometry:
            self.restoreGeometry(geometry)
            print("✅ Геометрия окна восстановлена")
        if state:
            self.restoreState(state)
            print("✅ Состояние окна восстановлено")
