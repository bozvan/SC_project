import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from src.gui.ui_main_window import Ui_MainWindow
from src.widgets.notes_widget import NotesWidget
from src.widgets.bookmarks_widget import BookmarksWidget
from src.widgets.task_widget import TaskWidget
from src.widgets.upcoming_tasks_widget import UpcomingTasksWidget
from src.widgets.settings_widget import SettingsWidget
from src.widgets.workspaces_widget import WorkspacesWidget
from src.core.task_manager import TaskManager
from src.core.bookmark_manager import BookmarkManager
from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.bookmark_manager = None
        self.task_manager = None
        self.note_manager = None
        self.tag_manager = None
        self.db_manager = None
        self.setupUi(self)
        self.current_widget = None
        self.setup_ui()
        self.setup_managers()
        self.connect_signals()
        self.show_notes_widget()

        self.apply_styles()

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
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        self.task_manager = TaskManager(self.db_manager)
        self.bookmark_manager = BookmarkManager(self.db_manager)

        print("✅ Все менеджеры инициализированы")

    def apply_styles(self):
        """Принудительное применение стилей"""
        button_style = """
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

        buttons = [
            self.btnTasks,
            self.btnNotes,
            self.btnBookmarks,
            self.btnWorkspaces,
            self.btnSettings,
            self.btnChangetheme
        ]

        for button in buttons:
            button.setStyleSheet(button_style)

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
            notes_widget = NotesWidget()
            self.set_content_widget(notes_widget)
            self.btnNotes.setStyleSheet("background-color: #8e8e8e;")
            self.reset_other_buttons(self.btnNotes)
        except Exception as e:
            print(f"Ошибка при создании виджета заметок: {e}")
            self.show_placeholder("Виджет заметок")

    def show_tasks_widget(self):
        """Показать виджет задач"""
        try:
            tasks_widget = UpcomingTasksWidget(self.task_manager, self.note_manager)
            self.set_content_widget(tasks_widget)
            self.btnNotes.setStyleSheet("background-color: #8e8e8e;")
            self.reset_other_buttons(self.btnTasks)
        except Exception as e:
            print(f"Ошибка при создании виджета задач: {e}")
            self.show_placeholder("Виджет задач")
        #self.btnTasks.setStyleSheet("background-color: #8e8e8e;")
        #self.reset_other_buttons(self.btnTasks)

    def show_bookmarks_widget(self):
        """Показать виджет закладок"""
        try:
            bookmarks_widget = BookmarksWidget()
            self.set_content_widget(bookmarks_widget)
            self.btnBookmarks.setStyleSheet("background-color: #8e8e8e;")
            self.reset_other_buttons(self.btnBookmarks)
        except Exception as e:
            print(f"Ошибка при создании виджета закладок: {e}")
            self.show_placeholder("Виджет закладок")

    def show_workspaces_widget(self):
        """Показать виджет рабочих пространств"""
        try:
            workspaces_widget = WorkspacesWidget()
            self.set_content_widget(workspaces_widget)
            self.btnWorkspaces.setStyleSheet("background-color: #8e8e8e;")
            self.reset_other_buttons(self.btnWorkspaces)
        except Exception as e:
            print(f"Ошибка при создании виджета рабочих пространств: {e}")
            self.show_placeholder("Виджет рабочих пространств")

    def show_settings_widget(self):
        """Показать виджет настроек"""
        try:
            settings_widget = SettingsWidget()
            self.set_content_widget(settings_widget)
            self.btnSettings.setStyleSheet("background-color: #8e8e8e;")
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

        for button in buttons:
            if button != active_button:
                button.setStyleSheet("")
        self.apply_styles()

    def toggle_theme(self):
        """Переключение темы (заглушка)"""
        QtWidgets.QMessageBox.information(
            self,
            "Смена темы",
            "Функция смены темы будет реализована в будущем"
        )


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
