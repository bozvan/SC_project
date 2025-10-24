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
            QToolTip {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 4px 6px;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 13px;
                font-weight: normal;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }

            /* Стили кнопок на главном виджете */

            QPushButton#btnTasks, QPushButton#btnNotes, QPushButton#btnBookmarks, 
            QPushButton#btnWorkspaces, QPushButton#btnSettings {
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

            QPushButton#btnTasks:hover, QPushButton#btnNotes:hover, QPushButton#btnBookmarks:hover, 
            QPushButton#btnWorkspaces:hover, QPushButton#btnSettings:hover {
                background-color: #E16428;
            }
            QPushButton#btnTasks:pressed, QPushButton#btnNotes:pressed, QPushButton#btnBookmarks:pressed, 
            QPushButton#btnWorkspaces:pressed, QPushButton#btnSettings:pressed {
                background-color: #E16428;
            }
            
            /* SETTING WIDGET */
            QLabel#theme_label,
            QLabel#theme_info_label, 
            QLabel#data_info_label, 
            QLabel#setting_title_label {
                color: black;
                font-size: 14px;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
            }
            
            QPushButton#import_btn, QPushButton#export_btn {
                color: #E16428;
                border: 1px solid #E16428;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
            }  

            QPushButton#import_btn:hover, QPushButton#export_btn:hover{
                background-color: #FFE1D2;
            }
            QPushButton#import_btn:pressed, QPushButton#export_btn:pressed {
                background-color: #ffffff;
            }
            
            
/*======================================= QComboBox =======================================*/


            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #E16428;
                border-radius: 4px;
                padding: 6px 10px;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 12px;
                font-weight: normal;
                min-width: 120px;
            }
            
            QComboBox:hover {
                border: 1px solid #999999;
            }
            
            QComboBox:focus {
                border: 1px solid #E16428;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #E16428;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #666666;
                width: 0px;
                height: 0px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 12px;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px 8px;
                border-radius: 2px;
                color: black;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #FFE1D2;
                color: black;
            }
            
            QComboBox QAbstractItemView::item:hover {
                color: black;
                background-color: #FF8851;
            }
            
            
/*======================================= QSplitter =======================================*/
            
            
            QSplitter#main_splitter {
                background-color: transparent;
            }
            
            QSplitter#main_splitter::handle {
                background-color: #e0e0e0;
                width: 1px;
                margin: 0px;
            }
            
            QSplitter#main_splitter::handle:hover {
                background-color: #E16428;
                width: 3px;
            }
            
            QSplitter#main_splitter::handle:pressed {
                background-color: #c8531f;
                width: 3px;
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
            QToolTip {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 4px 6px;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 13px;
                font-weight: normal;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            }

            /* Стили кнопок на главном виджете */

            QPushButton#btnTasks, QPushButton#btnNotes, QPushButton#btnBookmarks, 
            QPushButton#btnWorkspaces, QPushButton#btnSettings {
                margin: -1px;
                color: white;
                font-size: 18px;
                font-family: "Sans Serif", sans-serif;
                font-weight: bold;
                border: 1px solid #ffffff;
                border-radius: 5px;
            }

            QPushButton#btnTasks:hover, QPushButton#btnNotes:hover, QPushButton#btnBookmarks:hover {
                background-color: #E16428;
            }
            QPushButton#btnTasks:pressed, QPushButton#btnNotes:pressed {
                background-color: #E16428;
            }
            
            /* SETTING WIDGET */
            QLabel#theme_label,
            QLabel#theme_info_label, 
            QLabel#data_info_label, 
            QLabel#setting_title_label {
                color: white;
                font-size: 14px;
                font-family: "Segoe UI", "Arial", sans-serif; 
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
            }
            
            QPushButton#import_btn, QPushButton#export_btn {
                color: #E16428;
                border: 1px solid #E16428;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton#import_btn:hover, QPushButton#export_btn:hover {
                background-color: #201611;
            }
            QPushButton#import_btn:pressed, QPushButton#export_btn:pressed {
                background-color: #0d1117;
            }
            
            
/*======================================= QComboBox =======================================*/


            QComboBox {
                background-color: #0d1117;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 10px;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 12px;
                font-weight: normal;
                min-width: 120px;
            }
            
            QComboBox:hover {
                border: 1px solid #666666;
            }
            
            QComboBox:focus {
                border: 1px solid #E16428;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #404040;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #999999;
                width: 0px;
                height: 0px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #0d1117;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 12px;
                outline: none;
                color: #e0e0e0;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px 8px;
                border-radius: 2px;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #3a3a3a;
                color: white;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #E16428;
                color: white;
            }
            
            
/*======================================= QSplitter =======================================*/


            QSplitter#main_splitter {
                background-color: transparent;
            }
            
            QSplitter#main_splitter::handle {
                background-color: #404040;
                width: 1px;
                margin: 0px;
            }
            
            QSplitter#main_splitter::handle:hover {
                background-color: #E16428;
                width: 3px;
            }
            
            QSplitter#main_splitter::handle:pressed {
                background-color: #c8531f;
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
