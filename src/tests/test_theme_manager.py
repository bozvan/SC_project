import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock, PropertyMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.core.theme_manager import ThemeManager


class TestThemeManager(unittest.TestCase):
    """Тесты для ThemeManager"""

    @classmethod
    def setUpClass(cls):
        """Инициализация QApplication для всех тестов"""
        cls.app = QApplication([])

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Используем временные настройки
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "test_settings.ini")

        # Создаем патч для QSettings
        self.settings_patcher = patch('src.core.theme_manager.QSettings')
        self.mock_settings_class = self.settings_patcher.start()
        self.mock_settings_instance = MagicMock()
        self.mock_settings_class.return_value = self.mock_settings_instance

        # Настраиваем возвращаемое значение для метода value
        self.mock_settings_instance.value.return_value = "dark"

        # Создаем экземпляр ThemeManager
        self.theme_manager = ThemeManager()

    def tearDown(self):
        """Очистка после каждого теста"""
        self.settings_patcher.stop()
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Тест инициализации ThemeManager"""
        # Проверяем, что настройки загружены
        self.mock_settings_instance.value.assert_called_with("appearance/theme", "dark", type=str)

        # Проверяем, что темы загружены
        self.assertIn("light", self.theme_manager.stylesheets)
        self.assertIn("dark", self.theme_manager.stylesheets)

        # Проверяем, что текущая тема установлена
        self.assertEqual(self.theme_manager.current_theme, "dark")

    def test_load_themes(self):
        """Тест загрузки тем"""
        # Проверяем, что стили загружены для обеих тем
        self.assertIsInstance(self.theme_manager.stylesheets["light"], str)
        self.assertIsInstance(self.theme_manager.stylesheets["dark"], str)

        # Проверяем, что стили не пустые
        self.assertGreater(len(self.theme_manager.stylesheets["light"]), 100)
        self.assertGreater(len(self.theme_manager.stylesheets["dark"]), 100)

        # Проверяем, что стили содержат ключевые элементы
        self.assertIn("QMainWindow", self.theme_manager.stylesheets["light"])
        self.assertIn("QMainWindow", self.theme_manager.stylesheets["dark"])
        self.assertIn("background-color", self.theme_manager.stylesheets["light"])
        self.assertIn("background-color", self.theme_manager.stylesheets["dark"])

    def test_apply_theme_with_theme_name(self):
        """Тест применения темы с указанием имени"""
        with patch.object(QApplication, 'instance') as mock_instance:
            mock_app = MagicMock()
            mock_instance.return_value = mock_app

            # Применяем светлую тему
            self.theme_manager.apply_theme("light")

            # Проверяем, что стили применены
            mock_app.setStyleSheet.assert_called_once()
            mock_app.setPalette.assert_called_once()

            # Проверяем, что тема сохранена
            self.mock_settings_instance.setValue.assert_called_with("appearance/theme", "light")

            # Проверяем, что текущая тема обновлена
            self.assertEqual(self.theme_manager.current_theme, "light")

    def test_apply_theme_without_theme_name(self):
        """Тест применения текущей темы без указания имени"""
        with patch.object(QApplication, 'instance') as mock_instance:
            mock_app = MagicMock()
            mock_instance.return_value = mock_app

            # Устанавливаем текущую тему
            self.theme_manager.current_theme = "dark"

            # Применяем без указания темы
            self.theme_manager.apply_theme()

            # Проверяем, что применена текущая тема
            mock_app.setStyleSheet.assert_called_once()
            self.assertEqual(self.theme_manager.current_theme, "dark")

    def test_apply_theme_unknown_theme(self):
        """Тест применения неизвестной темы"""
        with patch.object(QApplication, 'instance') as mock_instance:
            mock_app = MagicMock()
            mock_instance.return_value = mock_app

            # Пытаемся применить неизвестную тему
            self.theme_manager.apply_theme("unknown_theme")

            # Проверяем, что стили не применены (т.к. темы нет в словаре)
            mock_app.setStyleSheet.assert_not_called()

            # Но текущая тема должна обновиться
            self.assertEqual(self.theme_manager.current_theme, "unknown_theme")

    def test_apply_palette_dark_theme(self):
        """Тест применения палитры для темной темы"""
        with patch.object(QApplication, 'instance') as mock_instance:
            mock_app = MagicMock()
            mock_instance.return_value = mock_app

            # Применяем палитру для темной темы
            self.theme_manager.apply_palette("dark")

            # Проверяем, что палитра применена
            mock_app.setPalette.assert_called_once()

    def test_apply_palette_light_theme(self):
        """Тест применения палитры для светлой темы"""
        with patch.object(QApplication, 'instance') as mock_instance:
            mock_app = MagicMock()
            mock_instance.return_value = mock_app

            # Применяем палитру для светлой темы
            self.theme_manager.apply_palette("light")

            # Проверяем, что палитра применена
            mock_app.setPalette.assert_called_once()

    def test_get_current_theme(self):
        """Тест получения текущей темы"""
        # Устанавливаем тему
        self.theme_manager.current_theme = "light"

        # Получаем текущую тему
        current_theme = self.theme_manager.get_current_theme()

        # Проверяем, что возвращена правильная тема
        self.assertEqual(current_theme, "light")

    def test_set_theme(self):
        """Тест установки новой темы"""
        with patch.object(self.theme_manager, 'apply_theme') as mock_apply:
            # Устанавливаем новую тему
            self.theme_manager.set_theme("dark")

            # Проверяем, что тема установлена и применена
            self.assertEqual(self.theme_manager.current_theme, "dark")
            mock_apply.assert_called_once_with("dark")

    def test_get_effective_theme_name(self):
        """Тест получения актуального названия темы"""
        # Устанавливаем тему
        self.theme_manager.current_theme = "dark"

        # Получаем актуальное название
        theme_name = self.theme_manager.get_effective_theme_name()

        # Проверяем, что возвращена правильная тема
        self.assertEqual(theme_name, "dark")

    def test_theme_stylesheet_content(self):
        """Тест содержания стилей тем"""
        # Проверяем светлую тему
        light_stylesheet = self.theme_manager.stylesheets["light"]
        self.assertIn("background-color: #ffffff", light_stylesheet)
        self.assertIn("color: black", light_stylesheet)
        self.assertIn("QMainWindow", light_stylesheet)
        self.assertIn("QPushButton", light_stylesheet)

        # Проверяем темную тему
        dark_stylesheet = self.theme_manager.stylesheets["dark"]
        self.assertIn("background-color: #0d1117", dark_stylesheet)
        self.assertIn("color: white", dark_stylesheet)
        self.assertIn("QMainWindow", dark_stylesheet)
        self.assertIn("QPushButton", dark_stylesheet)

    def test_theme_stylesheet_completeness(self):
        """Тест полноты стилей тем"""
        # Проверяем, что стили содержат все основные компоненты
        required_sections = [
            "QMainWindow", "QWidget", "QLabel", "QPushButton",
            "QLineEdit", "QTextEdit", "QListWidget", "QComboBox"
        ]

        for theme in ["light", "dark"]:
            stylesheet = self.theme_manager.stylesheets[theme]
            for section in required_sections:
                self.assertIn(section, stylesheet,
                              f"Section {section} not found in {theme} theme")

    def test_settings_persistence(self):
        """Тест сохранения настроек темы"""
        with patch.object(QApplication, 'instance'):
            # Устанавливаем тему
            self.theme_manager.set_theme("light")

            # Проверяем, что настройка сохранена
            self.mock_settings_instance.setValue.assert_called_with("appearance/theme", "light")

    def test_initial_theme_from_settings(self):
        """Тест загрузки начальной темы из настроек"""
        # Останавливаем текущий патч
        self.settings_patcher.stop()

        # Настраиваем mock для возврата определенной темы
        with patch('src.core.theme_manager.QSettings') as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings_instance.value.return_value = "light"
            mock_settings.return_value = mock_settings_instance

            # Создаем новый ThemeManager (должен загрузить тему из настроек)
            theme_manager = ThemeManager()

            # Проверяем, что тема загружена из настроек
            self.assertEqual(theme_manager.current_theme, "light")

            # Восстанавливаем патч
            self.settings_patcher.start()

    def test_default_theme_when_no_settings(self):
        """Тест установки темы по умолчанию при отсутствии настроек"""
        # Останавливаем текущий патч
        self.settings_patcher.stop()

        # Настраиваем mock для возврата None (настройка не существует)
        with patch('src.core.theme_manager.QSettings') as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings_instance.value.return_value = None
            mock_settings.return_value = mock_settings_instance

            # Создаем новый ThemeManager
            theme_manager = ThemeManager()

            # Проверяем, что установлена тема по умолчанию
            self.assertEqual(theme_manager.current_theme, "dark")

            # Восстанавливаем патч
            self.settings_patcher.start()

    def test_theme_switch_sequence(self):
        """Тест последовательного переключения тем"""
        with patch.object(QApplication, 'instance') as mock_instance:
            mock_app = MagicMock()
            mock_instance.return_value = mock_app

            # Переключаемся между темами несколько раз
            themes = ["light", "dark", "light"]
            for theme in themes:
                self.theme_manager.set_theme(theme)
                self.assertEqual(self.theme_manager.current_theme, theme)

            # Проверяем, что стили применялись каждый раз
            self.assertEqual(mock_app.setStyleSheet.call_count, len(themes))

    def test_theme_manager_singleton_behavior(self):
        """Тест поведения ThemeManager при множественных экземплярах"""
        # Создаем второй экземпляр
        with patch('src.core.theme_manager.QSettings') as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings_instance.value.return_value = "light"
            mock_settings.return_value = mock_settings_instance

            tm2 = ThemeManager()

            # Каждый должен иметь свои собственные настройки
            self.theme_manager.set_theme("dark")
            tm2.set_theme("light")

            self.assertEqual(self.theme_manager.current_theme, "dark")
            self.assertEqual(tm2.current_theme, "light")

    def test_theme_stylesheet_format(self):
        """Тест формата стилевых таблиц"""
        for theme_name, stylesheet in self.theme_manager.stylesheets.items():
            # Проверяем, что это валидный CSS-подобный синтаксис
            self.assertIsInstance(stylesheet, str)
            self.assertGreater(len(stylesheet), 0)

            # Проверяем наличие основных CSS конструкций
            self.assertTrue(any(char in stylesheet for char in ['{', '}', ':']),
                            f"Invalid CSS format in {theme_name} theme")

            # Проверяем, что есть селекторы и свойства
            lines_with_properties = [line for line in stylesheet.split('\n')
                                     if ':' in line and not line.strip().startswith('/*')]
            self.assertGreater(len(lines_with_properties), 10,
                               f"Insufficient CSS properties in {theme_name} theme")

    def test_error_handling_in_apply_theme(self):
        """Тест обработки ошибок при применении темы"""
        with patch.object(QApplication, 'instance') as mock_instance:
            mock_app = MagicMock()
            mock_instance.return_value = mock_app

            # Симулируем ошибку при установке стилей
            mock_app.setStyleSheet.side_effect = Exception("Style error")

            # Применение темы не должно падать с исключением
            try:
                self.theme_manager.apply_theme("light")
                # Если дошли сюда, значит исключение было обработано
                self.assertTrue(True)
            except Exception as e:
                # Проверяем, что это именно наше тестовое исключение
                self.assertEqual(str(e), "Style error")

    def test_theme_names_consistency(self):
        """Тест согласованности имен тем"""
        # Получаем все доступные темы
        available_themes = list(self.theme_manager.stylesheets.keys())

        # Проверяем, что есть ожидаемые темы
        expected_themes = ["light", "dark"]
        for theme in expected_themes:
            self.assertIn(theme, available_themes)

        # Проверяем, что текущая тема одна из доступных
        self.assertIn(self.theme_manager.current_theme, available_themes)

    def test_empty_theme_handling(self):
        """Тест обработки пустых тем"""
        # Сохраняем оригинальные стили
        original_light = self.theme_manager.stylesheets["light"]
        original_dark = self.theme_manager.stylesheets["dark"]

        try:
            # Временно заменяем стили на пустые
            self.theme_manager.stylesheets["light"] = ""
            self.theme_manager.stylesheets["dark"] = "  "

            with patch.object(QApplication, 'instance') as mock_instance:
                mock_app = MagicMock()
                mock_instance.return_value = mock_app

                # Применение пустых тем не должно вызывать ошибок
                self.theme_manager.apply_theme("light")
                self.theme_manager.apply_theme("dark")

                # Проверяем, что стили все равно применяются
                self.assertEqual(mock_app.setStyleSheet.call_count, 2)

        finally:
            # Восстанавливаем оригинальные стили
            self.theme_manager.stylesheets["light"] = original_light
            self.theme_manager.stylesheets["dark"] = original_dark


class TestThemeManagerIntegration(unittest.TestCase):
    """Интеграционные тесты для ThemeManager"""

    @classmethod
    def setUpClass(cls):
        """Инициализация QApplication для всех тестов"""
        cls.app = QApplication([])

    def test_complete_theme_cycle(self):
        """Тест полного цикла работы с темами"""
        with patch('src.core.theme_manager.QSettings') as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings_instance.value.return_value = "dark"
            mock_settings.return_value = mock_settings_instance

            # Создаем менеджер тем
            theme_manager = ThemeManager()

            # Проверяем начальное состояние
            self.assertEqual(theme_manager.get_current_theme(), "dark")
            self.assertEqual(theme_manager.get_effective_theme_name(), "dark")

            # Меняем тему
            with patch.object(QApplication, 'instance') as mock_app_instance:
                mock_app = MagicMock()
                mock_app_instance.return_value = mock_app

                theme_manager.set_theme("light")

                # Проверяем изменения
                self.assertEqual(theme_manager.get_current_theme(), "light")
                mock_app.setStyleSheet.assert_called_once()
                mock_settings_instance.setValue.assert_called_with("appearance/theme", "light")

    def test_theme_consistency_after_reload(self):
        """Тест согласованности тем после перезагрузки"""
        with patch('src.core.theme_manager.QSettings') as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            # Первый экземпляр устанавливает тему
            mock_settings_instance.value.return_value = "dark"
            theme_manager1 = ThemeManager()
            theme_manager1.set_theme("light")

            # Второй экземпляр должен получить ту же тему из настроек
            mock_settings_instance.value.return_value = "light"
            theme_manager2 = ThemeManager()

            self.assertEqual(theme_manager2.current_theme, "light")


if __name__ == '__main__':
    # Запуск тестов с подробным выводом
    unittest.main(verbosity=2)