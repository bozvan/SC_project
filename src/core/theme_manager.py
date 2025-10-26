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
            
            
/*======================================= SETTING WIDGET =======================================*/


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
            QGroupBox#appearance_group, QGroupBox#data_group {
                border-radius: 3px;
                border-color: black;
                border-style: solid;
                border-width: 1px;
                font-weight: bold;    
            }
            SettingsWidget {
                background-color: palette(window);
            }
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
                border: 1px solid palette(mid);
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: palette(text);
            }
            QLabel {
                font-weight: normal;
            }
            QCheckBox {
        font-weight: normal;
        color: black;
        spacing: 5px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #666666;
        border-radius: 3px;
        background-color: #ffffff;
    }
    QCheckBox::indicator:hover {
        border: 1px solid #E16428;
        background-color: #f0f0f0;
    }
    QCheckBox::indicator:checked {
        background-color: #E16428;
        border: 1px solid #E16428;
    }
    QCheckBox::indicator:checked:hover {
        background-color: #c8531f;
        border: 1px solid #c8531f;
    }
    QCheckBox::indicator:checked:disabled {
        background-color: #cccccc;
        border: 1px solid #999999;
    }
    QCheckBox::indicator:unchecked:disabled {
        background-color: #f0f0f0;
        border: 1px solid #cccccc;
    }

    /* Стиль для галочки внутри чекбокса */
    QCheckBox::indicator:checked {
        image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'><path fill='white' d='M13.485 3.429L6.354 10.56 3.171 7.377 2 8.548l4.354 4.354 7.667-7.667z'/></svg>");
    }
            QComboBox {
                font-weight: normal;
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
            
            
/*======================================= WORKSPACE WIDGET =======================================*/
            
            
            QGroupBox#groupBoxStats, QGroupBox#groupBoxManage, QGroupBox#groupBoxCurrent {
                border-radius: 3px;
                border-color: black;
                border-style: solid;
                border-width: 1px;
                font-weight: bold;    
            }
            
            
/*======================================= TASKS WIDGET =======================================*/

/*======================================= TASKS WIDGET =======================================*/

QListWidget#tasks_list {
    background-color: #ffffff;
    border: 1px solid black;
    border-radius: 3px;
    outline: none;
}

/* Убедитесь, что элементы списка занимают всю ширину */
QListWidget#tasks_list::item {
    border: none;
    padding: 0px;
    margin: 0px 0px 2px 0px;
    height: 50px;
}

QListWidget#tasks_list::item:selected {
    background-color: transparent;
}

QListWidget#tasks_list::item:alternate {
    background-color: #ffffff;
}

/* Базовые стили для кастомных виджетов */
#task_item_widget {
    background-color: #ffffff;
    border-bottom: 1px solid #E16428;
    min-height: 49px;
    max-height: 49px;
    font-weight: normal;
    font-size: 12px;
    width: 100%;
}

/* Прозрачные стили для внутренних элементов */
#task_item_widget QWidget,
#task_item_widget QLabel,
#task_item_widget QPushButton {
    background-color: transparent;
}


/* Стили для кнопки заметки - прозрачная с серой рамкой */
#task_item_widget QPushButton {
    background-color: transparent;
    border: 1px solid #666666;
    border-radius: 3px;
    font-size: 11px;
    color: black;
}

#task_item_widget QPushButton:hover {
    background-color: rgba(0, 0, 0, 0.1);
    border: 1px solid #888888;
}

#task_item_widget QPushButton:pressed {
    background-color: rgba(0, 0, 0, 0.2);
}

/* Стили для разных приоритетов */
#task_item_widget[priority="high"] {
    border-bottom: 1px solid #ff4444;
}

#task_item_widget[priority="medium"] {
    border-bottom: 1px solid #ffaa00;
}

#task_item_widget[priority="low"] {
    border-bottom: 1px solid #44ff44;
}

#task_item_widget[priority="none"] {
    border-bottom: 1px solid #cccccc;
}

/* При наведении меняем фон только родительского виджета */
#task_item_widget:hover {
    background-color: #f0f0f0;
}

/* Стили для выполненной задачи */
#task_item_widget[completed="true"] {
    border-bottom: 1px solid #cccccc;
}

#task_item_widget[completed="true"] QLabel {
    text-decoration: line-through;
    color: #888888;
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
            
            
/*======================================= SETTING WIDGET =======================================*/


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
            QGroupBox#appearance_group, QGroupBox#data_group {
                border-radius: 3px;
                border-color: white;
                border-style: solid;
                border-width: 1px;
                font-weight: bold;    
            }
            SettingsWidget {
                background-color: palette(window);
            }
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
                
                border: 1px solid palette(mid);
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: palette(text);
            }
            QLabel {
                font-weight: normal;
            }
            QCheckBox {
        font-weight: normal;
        color: white;
        spacing: 5px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #666666;
        border-radius: 3px;
        background-color: #0d1117;
    }
    QCheckBox::indicator:hover {
        border: 1px solid #E16428;
        background-color: #1a1f29;
    }
    QCheckBox::indicator:checked {
        background-color: #E16428;
        border: 1px solid #E16428;
    }
    QCheckBox::indicator:checked:hover {
        background-color: #c8531f;
        border: 1px solid #c8531f;
    }
    QCheckBox::indicator:checked:disabled {
        background-color: #444444;
        border: 1px solid #666666;
    }
    QCheckBox::indicator:unchecked:disabled {
        background-color: #1a1f29;
        border: 1px solid #444444;
    }

    /* Стиль для галочки внутри чекбокса */
    QCheckBox::indicator:checked {
        image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'><path fill='white' d='M13.485 3.429L6.354 10.56 3.171 7.377 2 8.548l4.354 4.354 7.667-7.667z'/></svg>");
    }
            QComboBox {
                font-weight: normal;
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
       
            
/*======================================= WORKSPACE WIDGET =======================================*/
        
            
            QGroupBox#groupBoxStats, QGroupBox#groupBoxManage, QGroupBox#groupBoxCurrent {
                border-radius: 3px;
                border-color: white;
                border-style: solid;
                border-width: 1px;
                font-weight: bold;    
            }
            QLineEdit#editSearch {
                border: none;
                border-bottom: 2px solid #E16428;
                min-height: 10px;
                max-height: 30px;
                padding: 5px;
                background-color: transparent;
                selection-background-color: #E16428;
            }
            QLineEdit#editSearch:hover {
                border-bottom: 2px solid #E16428;
                background-color: rgba(225, 100, 40, 0.1);
            }
            QPushButton#btnCreate {
                color: #E16428;
                border: 1px solid #E16428;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton#btnCreate:hover {
                background-color: #201611;
            }
            QPushButton#btnCreate:pressed {
                background-color: #0d1117;
            }
            
            
/*======================================= TASKS WIDGET =======================================*/


            QListWidget#tasks_list {
                background-color: #0D1117;
                border: 1px solid white;
                border-radius: 3px;
                outline: none;
            }
            
            /* Убедитесь, что элементы списка занимают всю ширину */
            QListWidget#tasks_list::item {
                border: none;
                padding: 0px;
                margin: 0px 0px 2px 0px;
                height: 50px;
            }
            
            QListWidget#tasks_list::item:selected {
                background-color: transparent;
            }
            
            QListWidget#tasks_list::item:alternate {
                background-color: #0D1117;
            }
            
            /* Базовые стили для кастомных виджетов */
            #task_item_widget {
                background-color: #0D1117;
                border-bottom: 1px solid orange;
                min-height: 49px;
                max-height: 49px;
                font-weight: normal;
                font-size: 12px;
                width: 100%;
            }
            
            /* Прозрачные стили для внутренних элементов */
            #task_item_widget QWidget,
            #task_item_widget QLabel,
            #task_item_widget QPushButton {
                background-color: transparent;
            }
            
            
            /* Стили для кнопки заметки - прозрачная с серой рамкой */
            #task_item_widget QPushButton {
                background-color: transparent;
                border: 1px solid #666666;
                border-radius: 3px;
                font-size: 11px;
                color: white;
            }
            
            #task_item_widget QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #888888;
            }
            
            #task_item_widget QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            /* Стили для разных приоритетов */
            #task_item_widget[priority="high"] {
                border-bottom: 1px solid #ff4444;
            }
            
            #task_item_widget[priority="medium"] {
                border-bottom: 1px solid #ffaa00;
            }
            
            #task_item_widget[priority="low"] {
                border-bottom: 1px solid #44ff44;
            }
            
            #task_item_widget[priority="none"] {
                border-bottom: 1px solid #666666;
            }
            
            /* При наведении меняем фон только родительского виджета */
            #task_item_widget:hover {
                background-color: #1a1f29;
            }
            
            /* Стили для выполненной задачи */
            #task_item_widget[completed="true"] {
                border-bottom: 1px solid #666666;
            }
            
            #task_item_widget[completed="true"] QLabel {
                text-decoration: line-through;
                color: #888888;
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
