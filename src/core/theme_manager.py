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
                background-color: rgba(225, 100, 40, 0.1);
            }
            QPushButton#btnCreate:pressed {
                background-color: #ffffff;
            }
            #workspace_card {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #ffffff;
                padding: 0px;
            }
            
            /* Стили для кнопок выбора workspace в светлой теме */
            WorkspaceCard QPushButton[class="select-button"] {
                background-color: #A1A1A1;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: normal;
                min-height: 15px;
                max-height: 15px;
            }
            
            WorkspaceCard QPushButton[class="select-button"]:hover {
                background-color: #616161;
            }
            
            WorkspaceCard QPushButton[class="select-button"]:pressed {
                background-color: #545454;
            }
            
            WorkspaceCard QPushButton[class="select-button"][current="true"] {
                background-color: #E16428;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            WorkspaceCard QPushButton[class="select-button"][current="true"]:hover {
                background-color: #ad420f;
            }
            
            WorkspaceCard QPushButton[class="select-button"][current="true"]:pressed {
                background-color: #8a350c;
            }
            
            
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

/*======================================= QInputDialog =======================================*/

QInputDialog QLineEdit {
    border: none;
    border-bottom: 2px solid #E16428;
    min-height: 10px;
    max-height: 30px;
    padding: 5px;
    background-color: transparent;
    selection-background-color: #E16428;
}

QInputDialog QLineEdit:hover {
    border-bottom: 2px solid #E16428;
    background-color: rgba(225, 100, 40, 0.1);
}

QInputDialog QLineEdit:focus {
    border-bottom: 2px solid #E16428;
    background-color: rgba(225, 100, 40, 0.05);
}

QInputDialog QPushButton[text="OK"] {
    background-color: transparent;
    color: #E16428;
    border: 2px solid #E16428;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
    min-width: 80px;
}

QInputDialog QPushButton[text="OK"]:hover {
    background-color: #E16428;
    color: white;
}

QInputDialog QPushButton[text="OK"]:pressed {
    background-color: #c8531f;
    border-color: #c8531f;
    color: white;
}

QInputDialog QPushButton[text="OK"]:disabled {
    background-color: transparent;
    color: #cccccc;
    border: 2px solid #cccccc;
}

QInputDialog QPushButton[text="Cancel"],
QInputDialog QPushButton[text="Отмена"] {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 6px 12px;
    min-width: 80px;
}

QInputDialog QPushButton[text="Cancel"]:hover,
QInputDialog QPushButton[text="Отмена"]:hover {
    background-color: #666666;
    color: white;
}

QInputDialog QPushButton[text="Cancel"]:pressed,
QInputDialog QPushButton[text="Отмена"]:pressed {
    background-color: #555555;
    border-color: #555555;
    color: white;
}


/*======================================= QMessageBox =======================================*/

QMessageBox QPushButton[text="No"] {
    background-color: white;
    color: white;
    border: 1px solid #E16428;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
    min-width: 80px;
}

QMessageBox QPushButton[text="No"]:hover {
    background-color: #c8531f;
    border-color: #c8531f;
}

QMessageBox QPushButton[text="No"]:pressed {
    background-color: #ad420f;
    border-color: #ad420f;
}

QMessageBox QPushButton[text="Yes"] {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 6px 12px;
    min-width: 80px;
}

QMessageBox QPushButton[text="Yes"]:hover {
    background-color: #666666;
    color: white;
}

QMessageBox QPushButton[text="Yes"]:pressed {
    background-color: #555555;
    border-color: #555555;
    color: white;
}

/* Для русского текста */
QMessageBox QPushButton[text="Нет"] {
    background-color: white;
    color: #E16428;
    border: 1px solid #E16428;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
    min-width: 80px;
}

QMessageBox QPushButton[text="Нет"]:hover {
    color: white;
    background-color: #c8531f;
    border-color: #c8531f;
}

QMessageBox QPushButton[text="Нет"]:pressed {
    color: white;
    background-color: #ad420f;
    border-color: #ad420f;
}

QMessageBox QPushButton[text="Да"] {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 6px 12px;
    min-width: 80px;
}

QMessageBox QPushButton[text="Да"]:hover {
    background-color: #666666;
    color: white;
}

QMessageBox QPushButton[text="Да"]:pressed {
    background-color: #555555;
    border-color: #555555;
    color: white;
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
#workspace_card {
    border: 1px solid #444444;
    border-radius: 6px;
    background-color: #0d1117;
    padding: 0px;
}

/* Стили для кнопок выбора workspace в темной теме */
WorkspaceCard QPushButton[class="select-button"] {
    background-color: #2d2d2d;
    color: white;
    border: none;
    padding: 8px;
    border-radius: 4px;
    font-weight: normal;
}

WorkspaceCard QPushButton[class="select-button"]:hover {
    background-color: #3a3a3a;
}

WorkspaceCard QPushButton[class="select-button"]:pressed {
    background-color: #4a4a4a;
}

WorkspaceCard QPushButton[class="select-button"][current="true"] {
    background-color: #E16428;
    color: white;
    border: none;
    padding: 8px;
    border-radius: 4px;
    font-weight: bold;
}

WorkspaceCard QPushButton[class="select-button"][current="true"]:hover {
    background-color: #ad420f;
}

WorkspaceCard QPushButton[class="select-button"][current="true"]:pressed {
    background-color: #8a350c;
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

/*======================================= QInputDialog =======================================*/

QInputDialog QLineEdit {
    border: none;
    border-bottom: 2px solid #E16428;
    min-height: 10px;
    max-height: 30px;
    padding: 5px;
    background-color: transparent;
    selection-background-color: #E16428;
}

QInputDialog QLineEdit:hover {
    border-bottom: 2px solid #E16428;
    background-color: rgba(225, 100, 40, 0.1);
}

QInputDialog QLineEdit:focus {
    border-bottom: 2px solid #E16428;
    background-color: rgba(225, 100, 40, 0.05);
}

QInputDialog QPushButton[text="OK"] {
    background-color: transparent;
    color: #E16428;
    border: 2px solid #E16428;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
    min-width: 80px;
}

QInputDialog QPushButton[text="OK"]:hover {
    background-color: #E16428;
    color: white;
}

QInputDialog QPushButton[text="OK"]:pressed {
    background-color: #c8531f;
    border-color: #c8531f;
    color: white;
}

QInputDialog QPushButton[text="OK"]:disabled {
    background-color: transparent;
    color: #cccccc;
    border: 2px solid #cccccc;
}

QInputDialog QPushButton[text="Cancel"],
QInputDialog QPushButton[text="Отмена"] {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 6px 12px;
    min-width: 80px;
}

QInputDialog QPushButton[text="Cancel"]:hover,
QInputDialog QPushButton[text="Отмена"]:hover {
    background-color: #666666;
    color: white;
}

QInputDialog QPushButton[text="Cancel"]:pressed,
QInputDialog QPushButton[text="Отмена"]:pressed {
    background-color: #555555;
    border-color: #555555;
    color: white;
}


/*======================================= QMessageBox =======================================*/

/* Основной стиль QMessageBox */
QMessageBox {
    background-color: #0D1117;
    color: white;
    font-family: "Segoe UI", "Arial", sans-serif;
    border: 1px solid #444444;
    border-radius: 8px;
}

/* Заголовок окна */
QMessageBox QLabel#qt_msgbox_label {
    color: white;
    font-size: 16px;
    font-weight: bold;
    background-color: transparent;
    padding: 10px;
}

/* Текст сообщения */
QMessageBox QLabel#qt_msgboxex_label {
    color: #cccccc;
    font-size: 14px;
    background-color: transparent;
    line-height: 1.5;
    padding: 10px;
}

/* Иконка сообщения */
QMessageBox QLabel#qt_msgboxex_icon_label {
    background-color: transparent;
}

/* ОБЩИЕ СТИЛИ КНОПОК */
QMessageBox QPushButton {
    background-color: transparent;
    color: #cccccc;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 12px;
    min-width: 80px;
    margin: 2px;
}

QMessageBox QPushButton:hover {
    background-color: #1a1f29;
    border-color: #888888;
}

QMessageBox QPushButton:pressed {
    background-color: #2a3140;
    border-color: #999999;
}

QMessageBox QPushButton:focus {
    border: 2px solid #E16428;
    outline: none;
}

/* === СИСТЕМА КНОПОК === */

/* 1. ПРИЗЫВАЮЩИЕ К ДЕЙСТВИЮ (ОСНОВНЫЕ) - ОРАНЖЕВАЯ ЗАЛИВКА */
/* Подтверждение, сохранение, повторить */
QMessageBox QPushButton[text="Yes"],
QMessageBox QPushButton[text="Да"],
QMessageBox QPushButton[text="OK"],
QMessageBox QPushButton[text="ОК"],
QMessageBox QPushButton[text="Save"], 
QMessageBox QPushButton[text="Сохранить"],
QMessageBox QPushButton[text="Retry"],
QMessageBox QPushButton[text="Повторить"] {
    background-color: #E16428;
    color: white;
    border: 1px solid #E16428;
    font-weight: bold;
}

QMessageBox QPushButton[text="Yes"]:hover,
QMessageBox QPushButton[text="Да"]:hover,
QMessageBox QPushButton[text="OK"]:hover,
QMessageBox QPushButton[text="ОК"]:hover,
QMessageBox QPushButton[text="Save"]:hover,
QMessageBox QPushButton[text="Сохранить"]:hover,
QMessageBox QPushButton[text="Retry"]:hover,
QMessageBox QPushButton[text="Повторить"]:hover {
    background-color: #f17337;
    border-color: #f17337;
}

QMessageBox QPushButton[text="Yes"]:pressed,
QMessageBox QPushButton[text="Да"]:pressed,
QMessageBox QPushButton[text="OK"]:pressed,
QMessageBox QPushButton[text="ОК"]:pressed,
QMessageBox QPushButton[text="Save"]:pressed,
QMessageBox QPushButton[text="Сохранить"]:pressed,
QMessageBox QPushButton[text="Retry"]:pressed,
QMessageBox QPushButton[text="Повторить"]:pressed {
    background-color: #c8531f;
    border-color: #c8531f;
}

/* 2. ОТМЕНА ДЕЙСТВИЯ (ВТОРИЧНЫЕ) - БЕЗ ЗАЛИВКИ */
/* Отмена, закрыть, нет, игнорировать */
QMessageBox QPushButton[text="No"],
QMessageBox QPushButton[text="Нет"], 
QMessageBox QPushButton[text="Cancel"],
QMessageBox QPushButton[text="Отмена"],
QMessageBox QPushButton[text="Close"],
QMessageBox QPushButton[text="Закрыть"],
QMessageBox QPushButton[text="Ignore"],
QMessageBox QPushButton[text="Игнорировать"],
QMessageBox QPushButton[text="Discard"],
QMessageBox QPushButton[text="Не сохранять"] {
    background-color: transparent;
    color: #cccccc;
    border: 1px solid #666666;
    font-weight: normal;
}

QMessageBox QPushButton[text="No"]:hover,
QMessageBox QPushButton[text="Нет"]:hover,
QMessageBox QPushButton[text="Cancel"]:hover,
QMessageBox QPushButton[text="Отмена"]:hover,
QMessageBox QPushButton[text="Close"]:hover,
QMessageBox QPushButton[text="Закрыть"]:hover,
QMessageBox QPushButton[text="Ignore"]:hover,
QMessageBox QPushButton[text="Игнорировать"]:hover,
QMessageBox QPushButton[text="Discard"]:hover,
QMessageBox QPushButton[text="Не сохранять"]:hover {
    background-color: #1a1f29;
    border-color: #888888;
}

QMessageBox QPushButton[text="No"]:pressed,
QMessageBox QPushButton[text="Нет"]:pressed,
QMessageBox QPushButton[text="Cancel"]:pressed,
QMessageBox QPushButton[text="Отмена"]:pressed,
QMessageBox QPushButton[text="Close"]:pressed,
QMessageBox QPushButton[text="Закрыть"]:pressed,
QMessageBox QPushButton[text="Ignore"]:pressed,
QMessageBox QPushButton[text="Игнорировать"]:pressed,
QMessageBox QPushButton[text="Discard"]:pressed,
QMessageBox QPushButton[text="Не сохранять"]:pressed {
    background-color: #2a3140;
    border-color: #999999;
}

/* 3. ОПАСНЫЕ ДЕЙСТВИЯ (КРАСНАЯ ЗАЛИВКА) */
QMessageBox QPushButton[text="Delete"],
QMessageBox QPushButton[text="Удалить"],
QMessageBox QPushButton[text="Remove"],
QMessageBox QPushButton[text="Удалить навсегда"] {
    background-color: #dc3545;
    color: white;
    border: 1px solid #dc3545;
    font-weight: bold;
}

QMessageBox QPushButton[text="Delete"]:hover,
QMessageBox QPushButton[text="Удалить"]:hover,
QMessageBox QPushButton[text="Remove"]:hover,
QMessageBox QPushButton[text="Удалить навсегда"]:hover {
    background-color: #e74c5c;
    border-color: #e74c5c;
}

QMessageBox QPushButton[text="Delete"]:pressed,
QMessageBox QPushButton[text="Удалить"]:pressed,
QMessageBox QPushButton[text="Remove"]:pressed,
QMessageBox QPushButton[text="Удалить навсегда"]:pressed {
    background-color: #c82333;
    border-color: #c82333;
}

/* Область кнопок */
QMessageBox QDialogButtonBox {
    background-color: transparent;
    border-top: 1px solid #444444;
    padding: 10px;
}


/*======================================= NOTE EDITOR WINDOW =======================================*/

NoteEditorWindow {
    background-color: #0d1117;
}

/* Базовые стили для всех QLineEdit в окне */
 QLineEdit {
    background-color: transparent;
    color: white;
    border: none;
    border-bottom: 2px solid #E16428;
    padding: 8px 5px;
    font-size: 14px;
    font-family: "Segoe UI", "Arial", sans-serif;
    selection-background-color: #E16428;
}

 QLineEdit:hover {
    border-bottom: 2px solid #E16428;
    background-color: rgba(225, 100, 40, 0.1);
}

 QLineEdit:focus {
    border-bottom: 2px solid #E16428;
    background-color: rgba(225, 100, 40, 0.05);
}



/* Убираем inline стили и применяем наши */
 QLabel {
    color: white;
    font-family: "Segoe UI", "Arial", sans-serif;
}

 QLabel#title_label {
    font-weight: bold;
    font-size: 14px;
    color: white;
}

 QLabel#content_label {
    font-weight: bold;
    font-size: 14px;
    color: white;
}

 QLabel#tags_label {
    font-weight: bold;
    font-size: 14px;
    color: white;
}

/* Текстовый редактор */
 QTextEdit#content_editor {
    background-color: #1a1f29;
    color: white;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 8px;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
    selection-background-color: #E16428;
}

 QTextEdit#content_editor:focus {
    border: 1px solid #E16428;
}

/* Статус бар с классами для разных состояний */
 QLabel#status_label {
    color: #888888;
    font-size: 11px;
    font-family: "Segoe UI", "Arial", sans-serif;
    background-color: transparent;
    padding: 2px 5px;
}

/* Классы для разных состояний статуса */
 QLabel#status_label[status="success"] {
    color: #4CAF50;
}

 QLabel#status_label[status="error"] {
    color: #F44336;
}

 QLabel#status_label[status="warning"] {
    color: #FF9800;
}

 QLabel#status_label[status="info"] {
    color: #2196F3;
}

/* Кнопка сохранения */
 QPushButton#save_btn {
    background-color: #E16428;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
    min-width: 80px;
}

 QPushButton#save_btn:hover {
    background-color: #c8531f;
}

 QPushButton#save_btn:pressed {
    background-color: #ad420f;
}

/* Кнопка отмены */
 QPushButton#cancel_btn {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
    min-width: 80px;
}

 QPushButton#cancel_btn:hover {
    background-color: #666666;
    color: white;
}

 QPushButton#cancel_btn:pressed {
    background-color: #555555;
    border-color: #555555;
    color: white;
}

/*======================================= TASK WIDGET =======================================*/

TaskWidget {
    background-color: transparent;
}

TaskWidget QCheckBox {
    background-color: transparent;
    color: white;
    spacing: 5px;
}

TaskWidget QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #666666;
    border-radius: 3px;
    background-color: #0d1117;
}

TaskWidget QCheckBox::indicator:hover {
    border: 1px solid #E16428;
    background-color: #1a1f29;
}

TaskWidget QCheckBox::indicator:checked {
    background-color: #E16428;
    border: 1px solid #E16428;
}

TaskWidget QCheckBox::indicator:checked:hover {
    background-color: #c8531f;
    border: 1px solid #c8531f;
}

TaskWidget QLineEdit {
    background-color: transparent;
    color: white;
    border: none;
    border-bottom: 1px solid #444444;
    padding: 5px 2px;
    font-size: 13px;
    font-family: "Segoe UI", "Arial", sans-serif;
    selection-background-color: #E16428;
}

TaskWidget QLineEdit:hover {
    border-bottom: 1px solid #666666;
    background-color: rgba(255, 255, 255, 0.05);
}

TaskWidget QLineEdit:focus {
    border-bottom: 1px solid #E16428;
    background-color: rgba(225, 100, 40, 0.05);
}

TaskWidget QLineEdit[style*="line-through"] {
    color: #888888;
    border-bottom: 1px solid #666666;
}

/*======================================= TAGS WIDGET =======================================*/

TagsWidget {
    background-color: transparent;
}

TagsWidget QLabel {
    color: white;
    font-weight: bold;
    font-size: 14px;
    font-family: "Segoe UI", "Arial", sans-serif;
    background-color: transparent;
}

TagsWidget QLineEdit {
    background-color: transparent;
    color: white;
    border: none;
    border-bottom: 1px solid #666666;
    padding: 6px 5px;
    font-size: 13px;
    font-family: "Segoe UI", "Arial", sans-serif;
    selection-background-color: #E16428;
}

TagsWidget QLineEdit:hover {
    border-bottom: 1px solid #888888;
    background-color: rgba(255, 255, 255, 0.05);
}

TagsWidget QLineEdit:focus {
    border-bottom: 1px solid #E16428;
    background-color: rgba(225, 100, 40, 0.05);
}

TagsWidget QPushButton {
    background-color: transparent;
    color: #E16428;
    border: 1px solid #E16428;
    border-radius: 4px;
    padding: 2px;
    font-size: 12px;
    font-weight: bold;
}

TagsWidget QPushButton:hover {
    background-color: #E16428;
    color: white;
}

TagsWidget QPushButton:pressed {
    background-color: #c8531f;
    border-color: #c8531f;
    color: white;
}

TagsWidget QPushButton:disabled {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
}

/* Основной стиль списка тегов - как у заметок */
TagsWidget QListWidget {
    background-color: #1a1f29;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
    margin: 0px 2px;
}

/* Элемент списка тегов с серым border снизу */
TagsWidget QListWidget::item {
    background-color: transparent;
    color: #cccccc;
    border: none;
    border-bottom: 1px solid #2d3746;
    border-radius: 0px;
    padding: 8px 10px;
    margin: 0px;
    min-height: 20px;
}

/* Убираем border у последнего элемента */
TagsWidget QListWidget::item:last {
    border-bottom: none;
}

/* Выделенный элемент - как активная кнопка */
TagsWidget QListWidget::item:selected {
    background-color: #E16428;
    color: white;
    border-bottom: 1px solid #E16428;
}

/* Hover эффект ТОЛЬКО для невыделенных элементов */
TagsWidget QListWidget::item:hover:!selected {
    background-color: rgba(225, 100, 40, 0.2);
    color: white;
    border-bottom: 1px solid #2d3746;
}

/* Активный тег НЕ меняется при наведении */
TagsWidget QListWidget::item:selected:hover {
    background-color: #E16428;
    color: white;
    border-bottom: 1px solid #E16428;
}

/* Эффект нажатия только для невыделенных */
TagsWidget QListWidget::item:pressed:!selected {
    background-color: rgba(225, 100, 40, 0.3);
    color: white;
    border-bottom: 1px solid #2d3746;
}

/* Активный тег при нажатии */
TagsWidget QListWidget::item:selected:pressed {
    background-color: #c8531f;
    color: white;
    
}

/* Полоса прокрутки */
TagsWidget QListWidget QScrollBar:vertical {
    background-color: #1a1f29;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

TagsWidget QListWidget QScrollBar::handle:vertical {
    background-color: #444444;
    border-radius: 4px;
    min-height: 20px;
}

TagsWidget QListWidget QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

TagsWidget QListWidget QScrollBar::handle:vertical:pressed {
    background-color: #E16428;
}

TagsWidget QListWidget QScrollBar::add-line:vertical,
TagsWidget QListWidget QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Убираем границу фокуса */
TagsWidget QListWidget:focus {
    border: 1px solid #444444;  /* Оставляем обычный серый border */
}

/* Стиль для пустого списка */
TagsWidget QListWidget:empty {
    color: #666666;
    font-style: italic;
    border-bottom: none;
}

/* Контекстное меню тегов */
TagsWidget QMenu {
    background-color: #1a1f29;
    border: 1px solid #444444;
    border-radius: 4px;
    color: white;
}

TagsWidget QMenu::item {
    background-color: transparent;
    padding: 6px 16px;
    color: white;
}

TagsWidget QMenu::item:selected {
    background-color: #E16428;
    color: white;
}

TagsWidget QMenu::item:disabled {
    color: #666666;
}
/*======================================= RICH TEXT EDITOR =======================================*/

RichTextEditor {
    background-color: transparent;
}

RichTextEditor QTextEdit {
    background-color: #1a1f29;
    color: white;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 8px;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
    selection-background-color: #E16428;
    selection-color: white;
}

RichTextEditor QTextEdit:focus {
    border: 1px solid #E16428;
}

/* Панель инструментов Rich Text Editor */
RichTextEditor QToolBar {
    background-color: #1a1f29;
    border: 1px solid #444444;
    border-radius: 4px;
    spacing: 6px;
    padding: 4px;
    margin: 0px;
}

/* Выравнивание всех элементов панели инструментов по высоте */
RichTextEditor QToolBar QComboBox {
    background-color: #0d1117;
    color: white;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 4px 6px;
    min-width: 120px;
    height: 24px;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 12px;
}

RichTextEditor QToolBar QComboBox:hover {
    border: 1px solid #666666;
}

RichTextEditor QToolBar QComboBox:focus {
    border: 1px solid #E16428;
}

RichTextEditor QToolBar QComboBox::drop-down {
    border-left: 1px solid #444444;
    width: 20px;
}

RichTextEditor QToolBar QComboBox QAbstractItemView {
    background-color: #0d1117;
    border: 1px solid #444444;
    color: white;
    min-height: 24px;
}

/* Стили для QSpinBox с темными кнопками */
RichTextEditor QToolBar QSpinBox {
    background-color: #0d1117;
    color: white;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 4px 8px;
    min-width: 70px;
    width: 70px;
    height: 24px;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 12px;
    margin-right: 8px;
}

RichTextEditor QToolBar QSpinBox:hover {
    border: 1px solid #666666;
}

RichTextEditor QToolBar QSpinBox:focus {
    border: 1px solid #E16428;
}

/* Самый выразительный вариант */
RichTextEditor QToolBar QSpinBox::up-button,
RichTextEditor QToolBar QSpinBox::down-button {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #4d5766, stop:1 #2d3746);
    border: 1px solid #5d6776;
    border-radius: 2px;
    width: 16px;
    height: 11px;
    margin: 0px;
    subcontrol-origin: border;
}

RichTextEditor QToolBar QSpinBox::up-button {
    border-bottom: 1px solid #1a1f29;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
}

RichTextEditor QToolBar QSpinBox::down-button {
    border-top: 1px solid #1a1f29;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}

RichTextEditor QToolBar QSpinBox::up-button:hover,
RichTextEditor QToolBar QSpinBox::down-button:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #5d6776, stop:1 #3d4756);
    border-color: #6d7786;
}

RichTextEditor QToolBar QSpinBox::up-button:pressed,
RichTextEditor QToolBar QSpinBox::down-button:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #E16428, stop:1 #c8531f);
    border-color: #E16428;
}

/* Крупные яркие стрелки */
RichTextEditor QToolBar QSpinBox::up-arrow {
    width: 9px;
    height: 9px;
    border-left: 4.5px solid transparent;
    border-right: 4.5px solid transparent;
    border-bottom: 9px solid #e0e0e0;
}

RichTextEditor QToolBar QSpinBox::down-arrow {
    width: 9px;
    height: 9px;
    border-left: 4.5px solid transparent;
    border-right: 4.5px solid transparent;
    border-top: 9px solid #e0e0e0;
}

RichTextEditor QToolBar QSpinBox::up-button:hover::up-arrow {
    border-bottom-color: white;
}

RichTextEditor QToolBar QSpinBox::down-button:hover::down-arrow {
    border-top-color: white;
}

RichTextEditor QToolBar QSpinBox::up-button:pressed::up-arrow {
    border-bottom-color: white;
}

RichTextEditor QToolBar QSpinBox::down-button:pressed::down-arrow {
    border-top-color: white;
}

/* Кнопки действий - одинаковый размер */
RichTextEditor QToolBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    min-width: 28px;
    min-height: 24px;
    max-height: 24px;
    padding: 0px;
    margin: 0px 1px;
}

RichTextEditor QToolBar QToolButton:hover {
    background-color: rgba(225, 100, 40, 0.2);
    border: 1px solid #E16428;
}

RichTextEditor QToolBar QToolButton:pressed {
    background-color: rgba(225, 100, 40, 0.3);
}

RichTextEditor QToolBar QToolButton:checked {
    background-color: #E16428;
    color: white;
    border: 1px solid #E16428;
}

RichTextEditor QToolBar QToolButton:checked:hover {
    background-color: #c8531f;
    border: 1px solid #c8531f;
}

/* Стили для разделителей */
RichTextEditor QToolBar QWidget[objectName="qt_toolbar_ext_button"],
RichTextEditor QToolBar QWidget[objectName="qt_toolbar_separator"] {
    background-color: #444444;
    width: 1px;
    margin: 2px 8px;
}

/* QColorDialog для выбора цвета текста */
QColorDialog {
    background-color: #1a1f29;
    color: white;
}

QColorDialog QWidget {
    background-color: #1a1f29;
    color: white;
}

QColorDialog QLabel {
    color: white;
}

/* Scrollbars для Rich Text Editor */
RichTextEditor QScrollBar:vertical {
    background-color: #1a1f29;
    width: 12px;
    margin: 0px;
}

RichTextEditor QScrollBar::handle:vertical {
    background-color: #444444;
    border-radius: 6px;
    min-height: 20px;
}

RichTextEditor QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

RichTextEditor QScrollBar::handle:vertical:pressed {
    background-color: #E16428;
}

RichTextEditor QScrollBar:horizontal {
    background-color: #1a1f29;
    height: 12px;
    margin: 0px;
}

RichTextEditor QScrollBar::handle:horizontal {
    background-color: #444444;
    border-radius: 6px;
    min-width: 20px;
}

RichTextEditor QScrollBar::handle:horizontal:hover {
    background-color: #666666;
}

RichTextEditor QScrollBar::handle:horizontal:pressed {
    background-color: #E16428;
}


/*======================================= NOTES LIST =======================================*/

/* Основной стиль списка заметок - уже */
NotesWidget QListWidget#notes_list {
    background-color: #1a1f29;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
    margin: 0px 2px; /* Добавляем небольшие боковые отступы */
}

/* Элемент списка заметок с серым border снизу */
NotesWidget QListWidget#notes_list::item {
    background-color: transparent;
    color: #cccccc;
    border: none;
    border-bottom: 1px solid #2d3746; /* Серый разделитель */
    border-radius: 0px; /* Убираем скругления для разделителей */
    padding: 8px 10px;
    margin: 0px;
    min-height: 20px;
}

/* Убираем border у последнего элемента */
NotesWidget QListWidget#notes_list::item:last {
    border-bottom: none;
}

/* Выделенный элемент - как активная кнопка */
NotesWidget QListWidget#notes_list::item:selected {
    background-color: #E16428;
    color: white;
    border-bottom: 1px solid #E16428; /* Оранжевый разделитель для выделенного */
}

/* Hover эффект ТОЛЬКО для невыделенных элементов */
NotesWidget QListWidget#notes_list::item:hover:!selected {
    background-color: rgba(225, 100, 40, 0.2);
    color: white;
    border-bottom: 1px solid #2d3746; /* Сохраняем серый разделитель */
}

/* Активная заметка НЕ меняется при наведении */
NotesWidget QListWidget#notes_list::item:selected:hover {
    background-color: #E16428; /* Остается оранжевой */
    color: white;
    border-bottom: 1px solid #E16428; /* Оранжевый разделитель */
}

/* Эффект нажатия только для невыделенных */
NotesWidget QListWidget#notes_list::item:pressed:!selected {
    background-color: rgba(225, 100, 40, 0.3);
    color: white;
    border-bottom: 1px solid #2d3746;
}

/* Активная заметка при нажатии */
NotesWidget QListWidget#notes_list::item:selected:pressed {
    background-color: #c8531f; /* Темнее при нажатии */
    color: white;
    border-bottom: 1px solid #c8531f; /* Темный оранжевый разделитель */
}

/* Полоса прокрутки */
NotesWidget QListWidget#notes_list QScrollBar:vertical {
    background-color: #1a1f29;
    width: 8px; /* Уже */
    margin: 0px;
    border-radius: 4px;
}

NotesWidget QListWidget#notes_list QScrollBar::handle:vertical {
    background-color: #444444;
    border-radius: 4px;
    min-height: 20px;
}

NotesWidget QListWidget#notes_list QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

NotesWidget QListWidget#notes_list QScrollBar::handle:vertical:pressed {
    background-color: #E16428;
}

NotesWidget QListWidget#notes_list QScrollBar::add-line:vertical,
NotesWidget QListWidget#notes_list QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Убираем границу фокуса */
NotesWidget QListWidget#notes_list:focus {
    border: 1px solid #E16428;
}

/* Стиль для пустого списка */
NotesWidget QListWidget#notes_list:empty {
    color: #666666;
    font-style: italic;
    border-bottom: none; /* Убираем border для пустого списка */
}

/*======================================= EDIT BOOKMARK DIALOG =======================================*/

EditBookmarkDialog {
    background-color: #0d1117;
}

EditBookmarkDialog QLabel {
    color: white;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
    background-color: transparent;
}

/* Стили для конкретных лейблов */
EditBookmarkDialog QLabel#title_label,
EditBookmarkDialog QLabel#url_label, 
EditBookmarkDialog QLabel#description_label,
EditBookmarkDialog QLabel#tags_label {
    font-weight: bold;
    font-size: 14px;
    color: white;
    padding: 2px 0px;
}

/* Стили для полей ввода */
EditBookmarkDialog QLineEdit {
    background-color: transparent;
    color: white;
    border: none;
    border-bottom: 2px solid #E16428;
    padding: 8px 5px;
    font-size: 14px;
    font-family: "Segoe UI", "Arial", sans-serif;
    selection-background-color: #E16428;
}

EditBookmarkDialog QLineEdit:hover {
    border-bottom: 2px solid #E16428;
    background-color: rgba(225, 100, 40, 0.1);
}

EditBookmarkDialog QLineEdit:focus {
    border-bottom: 2px solid #E16428;
    background-color: rgba(225, 100, 40, 0.05);
}

/* Стили для текстового поля описания */
EditBookmarkDialog QTextEdit {
    background-color: #1a1f29;
    color: white;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 8px;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
    selection-background-color: #E16428;
}

EditBookmarkDialog QTextEdit:focus {
    border: 1px solid #E16428;
}

/* Кнопки */
EditBookmarkDialog QPushButton#save_btn {
    background-color: #E16428;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
    min-width: 80px;
}

EditBookmarkDialog QPushButton#save_btn:hover {
    background-color: #c8531f;
}

EditBookmarkDialog QPushButton#save_btn:pressed {
    background-color: #ad420f;
}

EditBookmarkDialog QPushButton#cancel_btn {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
    min-width: 80px;
}

EditBookmarkDialog QPushButton#cancel_btn:hover {
    background-color: #666666;
    color: white;
}

EditBookmarkDialog QPushButton#cancel_btn:pressed {
    background-color: #555555;
    border-color: #555555;
    color: white;
}


/*======================================= NOTES PAGE BUTTONS =======================================*/

/* Кнопка создания новой заметки */
QWidget#NotesPage QPushButton#new_note_btn {
    background-color: #E16428;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: bold;
    padding: 0px;
    margin: 0px;
    min-height: 35px;
    max-height: 35px;
    min-width: 35px;
    max-width: 35px;
}

QWidget#NotesPage QPushButton#new_note_btn:hover {
    background-color: #f17337;
}

QWidget#NotesPage QPushButton#new_note_btn:pressed {
    background-color: #c8531f;
}

/* Кнопка удаления заметки */
QWidget#NotesPage QPushButton#delete_note_btn {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 4px;
    font-size: 12px;
    padding: 0px;
    margin: 0px;
    min-height: 35px;
    max-height: 35px;
    min-width: 30px;
    max-width: 30px;
}

QWidget#NotesPage QPushButton#delete_note_btn:hover {
    background-color: #666666;
    color: white;
}

QWidget#NotesPage QPushButton#delete_note_btn:pressed {
    background-color: #555555;
    border-color: #555555;
    color: white;
}

QWidget#NotesPage QPushButton#delete_note_btn:disabled {
    background-color: transparent;
    color: #444444;
    border: 1px solid #444444;
}

/* Кнопка открепления заметки - ТАКАЯ ЖЕ ВЫСОТА */
QPushButton#detach_btn {
    background-color: transparent;
    color: #E16428;
    border: 1px solid #E16428;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: bold;
    min-height: 22px;
    max-height: 23px;
}

QPushButton#detach_btn:hover {
    background-color: #E16428;
    color: white;
}

QPushButton#detach_btn:pressed {
    background-color: #c8531f;
    border-color: #c8531f;
    color: white;
}

/*======================================= TASK FORM STYLES =======================================*/

/* Кнопка добавления задачи - общий селектор */
QPushButton[text="Добавить"] {
    background-color: #E16428;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
    min-height: 25px;
    max-height: 25px;
    min-width: 80px;
}

QPushButton[text="Добавить"]:hover {
    background-color: #f17337;
}

QPushButton[text="Добавить"]:pressed {
    background-color: #c8531f;
}

QPushButton[text="Добавить"]:disabled {
    background-color: #444444;
    color: #888888;
}

/* Кнопка переключения расширенных опций */
QPushButton[text="⚙️ Дополнительно"],
QPushButton[text="⚙️ Скрыть"] {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 11px;
    min-height: 20px;
    max-height: 20px;
}

QPushButton[text="⚙️ Дополнительно"]:hover,
QPushButton[text="⚙️ Скрыть"]:hover {
    background-color: #1a1f29;
    border-color: #888888;
}

QPushButton[text="⚙️ Дополнительно"]:pressed,
QPushButton[text="⚙️ Скрыть"]:pressed {
    background-color: #2a3140;
    border-color: #999999;
}

/* Поле выбора даты - общий селектор */
QDateEdit {
    background-color: #0d1117;
    color: white;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 12px;
    min-height: 18px;
    max-height: 18px;
    min-width: 120px;
}

QDateEdit:hover {
    border: 1px solid #666666;
}

QDateEdit:focus {
    border: 1px solid #E16428;
}

/* Кнопка очистки даты - по тексту */
QPushButton[text="×"] {
    background-color: transparent;
    color: #666666;
    border: 1px solid #666666;
    border-radius: 3px;
    font-size: 10px;
    font-weight: bold;
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
    padding: 0px;
    margin: 0px;
}

QPushButton[text="×"]:hover {
    background-color: #666666;
    color: white;
}

QPushButton[text="×"]:pressed {
    background-color: #555555;
    border-color: #555555;
    color: white;
}

/* Стили для выпадающего календаря */
QCalendarWidget {
    background-color: #0d1117;
    color: white;
    border: 1px solid #444444;
    border-radius: 4px;
}

QCalendarWidget QToolButton {
    background-color: #1a1f29;
    color: white;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 4px 8px;
}

QCalendarWidget QToolButton:hover {
    background-color: #2a3140;
    border-color: #666666;
}

QCalendarWidget QMenu {
    background-color: #1a1f29;
    border: 1px solid #444444;
    color: white;
}

QCalendarWidget QSpinBox {
    background-color: #0d1117;
    color: white;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 4px;
}

/* Заголовки в layout с датой */
QLabel {
    color: #cccccc;
    font-size: 12px;
    padding: 0px 5px;
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
