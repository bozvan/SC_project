from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication
import json
import os
import platform


class ThemeManager:
    def __init__(self):
        self.settings = QSettings("SmartOrganizer", "SmartOrganizer")
        self.current_theme = self.settings.value("appearance/theme", "system", type=str)
        self.stylesheets = {}
        self.load_themes()

    def load_themes(self):
        """Загружает стили для всех тем"""
        # Светлая тема
        self.stylesheets["light"] = """
            /* Основные стили для светлой темы */
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }

            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px 16px;
                color: #333333;
            }

            QPushButton:hover {
                background-color: #e6e6e6;
                border-color: #adadad;
            }

            QPushButton:pressed {
                background-color: #d4d4d4;
            }

            QLineEdit, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 8px;
                color: #333333;
            }

            QListWidget, QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                color: #333333;
                outline: none;
            }

            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }

            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }

            QTabBar::tab {
                background-color: #e6e6e6;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #0078d4;
            }

            QMenuBar {
                background-color: #f0f0f0;
                color: #333333;
            }

            QMenuBar::item:selected {
                background-color: #e6e6e6;
            }

            QMenu {
                background-color: #ffffff;
                border: 1px solid #cccccc;
            }

            QMenu::item:selected {
                background-color: #0078d4;
                color: white;
            }

            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 15px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 7px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """

        # Темная тема
        self.stylesheets["dark"] = """
            /* Основные стили для темной темы */
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }

            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
            }

            QPushButton:hover {
                background-color: #505050;
                border-color: #666666;
            }

            QPushButton:pressed {
                background-color: #606060;
            }

            QLineEdit, QTextEdit {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
            }

            QListWidget, QTreeWidget {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #ffffff;
                outline: none;
            }

            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }

            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #404040;
            }

            QTabBar::tab {
                background-color: #353535;
                border: 1px solid #555555;
                padding: 8px 16px;
                margin-right: 2px;
                color: #ffffff;
            }

            QTabBar::tab:selected {
                background-color: #404040;
                border-bottom: 2px solid #0078d4;
            }

            QMenuBar {
                background-color: #353535;
                color: #ffffff;
            }

            QMenuBar::item:selected {
                background-color: #404040;
            }

            QMenu {
                background-color: #404040;
                border: 1px solid #555555;
                color: #ffffff;
            }

            QMenu::item:selected {
                background-color: #0078d4;
                color: white;
            }

            QScrollBar:vertical {
                background-color: #353535;
                width: 15px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 7px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """

        # Системная тема (определяется автоматически)
        self.stylesheets["system"] = ""

    def get_system_theme(self):
        """Определяет системную тему"""
        try:
            # Способ 1: через QApplication palette (наиболее надежный для Qt)
            app = QApplication.instance()
            if app:
                # Получаем цвет фона палитры
                background_color = app.palette().color(QPalette.ColorRole.Window)
                brightness = (background_color.red() * 0.299 +
                              background_color.green() * 0.587 +
                              background_color.blue() * 0.114)

                # Если яркость меньше 128 - считаем темной темой
                if brightness < 128:
                    print("🎨 Системная тема определена как: dark (по палитре Qt)")
                    return "dark"
                else:
                    print("🎨 Системная тема определена как: light (по палитре Qt)")
                    return "light"

        except Exception as e:
            print(f"⚠️ Не удалось определить тему через Qt: {e}")

        # Способ 2: через системные настройки (для разных ОС)
        try:
            system = platform.system().lower()

            if system == "windows":
                # Для Windows можно попробовать через реестр
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                         r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    if value == 0:
                        print("🎨 Системная тема определена как: dark (по реестру Windows)")
                        return "dark"
                    else:
                        print("🎨 Системная тема определена как: light (по реестру Windows)")
                        return "light"
                except:
                    pass

            elif system == "darwin":  # macOS
                # Для macOS можно использовать терминальные команды
                import subprocess
                try:
                    result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                                            capture_output=True, text=True)
                    if 'Dark' in result.stdout:
                        print("🎨 Системная тема определена как: dark (по настройкам macOS)")
                        return "dark"
                except:
                    pass

            elif system == "linux":
                # Для Linux можно попробовать через переменные окружения или gsettings
                import os
                gtk_theme = os.environ.get('GTK_THEME', '').lower()
                if 'dark' in gtk_theme:
                    print("🎨 Системная тема определена как: dark (по GTK_THEME)")
                    return "dark"

        except Exception as e:
            print(f"⚠️ Не удалось определить тему через системные настройки: {e}")

        # Способ 3: резервный - по умолчанию считаем светлой
        print("🎨 Системная тема не определена, используется по умолчанию: light")
        return "light"

    def apply_theme(self, theme_name=None):
        """Применяет указанную тему ко всему приложению"""
        if theme_name is None:
            theme_name = self.current_theme

        self.current_theme = theme_name
        self.settings.setValue("appearance/theme", theme_name)

        app = QApplication.instance()

        # Для системной темы определяем актуальную тему
        effective_theme = theme_name
        if theme_name == "system":
            effective_theme = self.get_system_theme()

        print(f"🎨 Применение темы: {theme_name} -> {effective_theme}")

        if effective_theme in self.stylesheets:
            stylesheet = self.stylesheets[effective_theme]
            app.setStyleSheet(stylesheet)

            # Также применяем палитру для лучшей совместимости
            self.apply_palette(effective_theme)

        print(f"✅ Применена тема: {theme_name} (эффективная: {effective_theme})")

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

    def get_effective_theme(self):
        """Возвращает эффективную тему (для системной темы определяет актуальную)"""
        if self.current_theme == "system":
            return self.get_system_theme()
        return self.current_theme
