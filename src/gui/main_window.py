import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt

from core.settings_manager import QtSettingsManager
from src.gui.ui_main_window import Ui_MainWindow
from src.widgets.notes_widget import NotesWidget
from src.widgets.bookmarks_widget import BookmarksWidget
from src.widgets.upcoming_tasks_widget import UpcomingTasksWidget
from src.widgets.settings_widget import SettingsWidget
from src.widgets.workspaces_widget import WorkspacesWidget
from src.core.task_manager import TaskManager
from src.core.bookmark_manager import BookmarkManager
from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager
from src.core.workspace_manager import WorkspaceManager


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.workspace_manager = None
        self.bookmark_manager = None
        self.task_manager = None
        self.note_manager = None
        self.tag_manager = None
        self.db_manager = None

        # Инициализация менеджера настроек ПЕРВЫМ делом
        self.settings_manager = QtSettingsManager()

        # Загружаем последний workspace из настроек
        self.current_workspace_id = self.settings_manager.get_last_workspace()

        self.setupUi(self)
        self.current_widget = None

        self.setup_ui()
        self.setup_managers()
        self.connect_signals()

        # Применяем стили ДО показа виджета заметок
        self.apply_styles()
        self.show_notes_widget()

    def setup_ui(self):
        """Настройка дополнительных параметров UI"""
        self.setWindowTitle("Умный Органайзер")
        self.setMinimumSize(1100, 600)
        self.splitter.setSizes([100, 600])

        if self.widgetConteiner.layout() is None:
            layout = QtWidgets.QVBoxLayout(self.widgetConteiner)
            layout.setContentsMargins(0, 0, 0, 0)
            print("✅ Layout контейнера создан")
        else:
            print("✅ Layout контейнера уже существует")

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

    def apply_styles(self):
        """Принудительное применение стилей"""
        # Базовый стиль для неактивных кнопок
        self.inactive_style = """
            QPushButton {
                margin: 0px;
                padding: 12px 8px;
                border: none;
                border-top: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 0px;
                text-align: left;
                background-color: #8E8E8E;
            }
            QPushButton:hover {
                background-color: #FFAA00;
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
                background-color: #FFAA00;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFBB33;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """

        # Изначально все кнопки неактивны
        buttons = [
            self.btnTasks,
            self.btnNotes,
            self.btnBookmarks,
            self.btnWorkspaces,
            self.btnSettings,
            self.btnChangetheme
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
        self.btnChangetheme.clicked.connect(self.toggle_theme)

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
                current_workspace_id=self.current_workspace_id
            )

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

        # Обновляем текущий виджет, если он поддерживает обновление workspace
        if self.current_widget and hasattr(self.current_widget, 'set_workspace'):
            self.current_widget.set_workspace(workspace_id)
            print(f"✅ Текущий виджет обновлен для workspace {workspace_id}")

    def show_settings_widget(self):
        """Показать виджет настроек"""
        try:
            settings_widget = SettingsWidget()
            self.set_content_widget(settings_widget)
            self.reset_other_buttons(self.btnSettings)
        except Exception as e:
            print(f"Ошибка при создании виджета настроек: {e}")
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
            self.btnSettings,
            self.btnChangetheme
        ]

        # Сначала устанавливаем всем неактивный стиль
        for button in buttons:
            button.setStyleSheet(self.inactive_style)

        # Затем устанавливаем активный стиль для выбранной кнопки
        active_button.setStyleSheet(self.active_style)

    def toggle_theme(self):
        """Переключение темы (заглушка)"""
        QtWidgets.QMessageBox.information(
            self,
            "Смена темы",
            "Функция смены темы будет реализована в будущем"
        )

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
        # Если текущий виджет поддерживает обновление - обновляем его
        if self.current_widget and hasattr(self.current_widget, 'refresh'):
            self.current_widget.refresh()
            print("✅ Текущий виджет обновлен")

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        print("🔴 Закрытие приложения...")

        # Сохраняем текущий workspace (на всякий случай, хотя он уже сохраняется при изменении)
        if hasattr(self, 'current_workspace_id'):
            self.settings_manager.set_last_workspace(self.current_workspace_id)
            print(f"💾 Сохранен workspace {self.current_workspace_id}")

        # Сохраняем состояние окна
        self.settings_manager.set_window_geometry(self.saveGeometry())
        self.settings_manager.set_window_state(self.saveState())

        print("💾 Настройки сохранены")

        event.accept()

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


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
