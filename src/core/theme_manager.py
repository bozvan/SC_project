from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication
import json
import os
import platform


class ThemeManager:
    def __init__(self):
        self.settings = QSettings("SmartOrganizer", "SmartOrganizer")
        self.current_theme = self.settings.value("appearance/theme", "dark", type=str)  # По умолчанию тёмная
        self.stylesheets = {}
        self.load_themes()

    def load_themes(self):
        """Загружает стили для всех тем"""
        # Светлая тема
        self.stylesheets["light"] = """
            /* Основные стили для светлой темы */
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                background-color: #ffffff;
            }
            QLabel#titleLabel {
                color: black;
                font-size: 28px;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-weight: 900; 
                padding: 10px;
                border-radius: 8px;
                text-align: center;
            }

            /* Стили кнопок на главном виджете */

            QPushButton#btnTasks, #btnNotes, #btnBookmarks, #btnWorkspaces, #btnSettings {
                text-align: left;
                margin: -1px;
                color: black;
                font-size: 18px;
                font-family: "Sans Serif", sans-serif;
                font-weight: bold;
                border: 1px solid #000000;
                border-radius: 5px;
                background-color: #ffffff;
            }

            QPushButton#btnTasks:hover, #btnNotes:hover, #btnBookmarks:hover, 
            #btnWorkspaces:hover, #btnSettings:hover {
                background-color: #E16428;
            }
            QPushButton#btnTasks:pressed, #btnNotes:pressed, #btnBookmarks:pressed, 
            #btnWorkspaces:pressed, #btnSettings:pressed {
                background-color: #E16428;
            }
        """

        # Темная тема
        self.stylesheets["dark"] = """
            /* Основные стили для темной темы */
            QMainWindow {
                background-color: #0d1117;
            }
            QWidget {
                background-color: #0d1117;
            }

            QLabel#titleLabel {
                color: white;
                font-size: 28px;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-weight: 900; 
                padding: 10px;
                border-radius: 8px;
                text-align: center;
            }

            /* Стили кнопок на главном виджете */

            QPushButton#btnTasks, #btnNotes, #btnBookmarks, #btnWorkspaces, #btnSettings {
                margin: -1px;
                color: white;
                font-size: 18px;
                font-family: "Sans Serif", sans-serif;
                font-weight: bold;
                border: 1px solid #ffffff;
                border-radius: 5px;
            }

            QPushButton#btnTasks:hover, #btnNotes:hover, #btnBookmarks:hover, 
            #btnWorkspaces:hover, #btnSettings:hover {
                background-color: #E16428;
            }
            QPushButton#btnTasks:pressed, #btnNotes:pressed, #btnBookmarks:pressed, 
            #btnWorkspaces:pressed, #btnSettings:pressed {
                background-color: #E16428;
            }
        """

    def apply_theme(self, theme_name=None):
        """Применяет указанную тему ко всему приложению"""
        if theme_name is None:
            theme_name = self.current_theme

        self.current_theme = theme_name
        self.settings.setValue("appearance/theme", theme_name)
        app = QApplication.instance()

        print(f"🎨 Применение темы: {theme_name}")

        if theme_name in self.stylesheets:
            stylesheet = self.stylesheets[theme_name]
            app.setStyleSheet(stylesheet)

            # Также применяем палитру для лучшей совместимости
            self.apply_palette(theme_name)

        print(f"✅ Применена тема: {theme_name}")

    def apply_palette(self, theme_name):
        """Применяет цветовую палитру для темы"""
        app = QApplication.instance()
        palette = QPalette()

        if theme_name == "dark":
            # Темная палитра
            palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Base, QColor(64, 64, 64))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Button, QColor(64, 64, 64))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        else:
            # Светлая палитра
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 231, 227))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        app.setPalette(palette)

    def get_current_theme(self):
        """Возвращает текущую тему"""
        return self.current_theme

    def set_theme(self, theme_name):
        """Устанавливает новую тему"""
        self.current_theme = theme_name
        self.apply_theme(theme_name)

    def get_effective_theme_name(self):
        """Возвращает актуальное название темы"""
        return self.current_theme
