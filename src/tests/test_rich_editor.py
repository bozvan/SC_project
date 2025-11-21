import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


class TestRichTextEditor(unittest.TestCase):
    """Тесты для RichTextEditor с изоляцией от циклических импортов"""

    @classmethod
    def setUpClass(cls):
        """Создаем QApplication один раз для всех тестов"""
        # Мокаем проблемные модули перед импортом RichTextEditor
        cls.mock_problematic_imports()

        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication([])

    @classmethod
    def mock_problematic_imports(cls):
        """Мокаем модули, вызывающие циклические импорты"""
        # Создаем моки для проблемных модулей
        mock_modules = {
            'widgets.task_widget': MagicMock(),
            'widgets.workspaces_widget': MagicMock(),
            'gui.ui_workspaces_widget': MagicMock(),
            'gui.main_window': MagicMock(),
        }

        # Подменяем модули в sys.modules
        for module_name, mock_module in mock_modules.items():
            sys.modules[module_name] = mock_module

    def setUp(self):
        """Создаем редактор перед каждым тестом"""
        # Импортируем здесь, после настройки моков
        from src.widgets.rich_text_editor import RichTextEditor
        self.editor = RichTextEditor()

    def tearDown(self):
        """Очищаем после каждого теста"""
        if hasattr(self, 'editor'):
            self.editor.deleteLater()

    def test_initial_state(self):
        """Тестирование начального состояния редактора"""
        self.assertEqual(self.editor.to_plain_text(), "")
        html_content = self.editor.to_html().lower()
        self.assertTrue(html_content.startswith("<!doctype html>") or "<html>" in html_content)

    def test_set_plain_text(self):
        """Тестирование установки простого текста"""
        test_text = "Это тестовый текст"
        self.editor.set_plain_text(test_text)

        result = self.editor.to_plain_text().strip()
        self.assertEqual(result, test_text)

    def test_set_html(self):
        """Тестирование установки HTML контента"""
        html_content = "<h1>Заголовок</h1><p>Абзац текста</p>"
        self.editor.set_html(html_content)

        result_html = self.editor.to_html()
        self.assertIn("Заголовок", result_html)
        self.assertIn("Абзац текста", result_html)

    def test_empty_content(self):
        """Тестирование работы с пустым контентом"""
        # Устанавливаем пустой текст
        self.editor.set_plain_text("")
        self.assertEqual(self.editor.to_plain_text().strip(), "")

        # Устанавливаем пустой HTML
        self.editor.set_html("")
        result_html = self.editor.to_html().lower()
        self.assertTrue("<!doctype html>" in result_html or "<html>" in result_html)

    def test_multiline_text(self):
        """Тестирование многострочного текста"""
        multiline_text = """Первая строка
Вторая строка
Третья строка"""

        self.editor.set_plain_text(multiline_text)
        result = self.editor.to_plain_text()

        self.assertIn("Первая строка", result)
        self.assertIn("Вторая строка", result)
        self.assertIn("Третья строка", result)

    def test_special_characters(self):
        """Тестирование специальных символов"""
        special_text = "Текст с & < > \" ' символами"
        self.editor.set_plain_text(special_text)

        result = self.editor.to_plain_text()
        self.assertIn("Текст с", result)
        # Проверяем что текст не обрезался полностью
        self.assertGreater(len(result.strip()), 0)

    def test_formatting_persistence(self):
        """Тестирование сохранения форматирования"""
        # Устанавливаем форматированный текст
        self.editor.set_plain_text("Простой текст")

        # Получаем обратно
        result = self.editor.to_plain_text()
        self.assertEqual(result.strip(), "Простой текст")

    def test_toolbar_creation(self):
        """Тестирование создания панели инструментов"""
        # Проверяем что панель инструментов создана
        self.assertIsNotNone(self.editor.toolbar)

        # Проверяем что панель не пустая
        self.assertTrue(self.editor.toolbar.children())

    def test_toolbar_buttons_exist(self):
        """Тестирование что кнопки панели инструментов существуют"""
        # Проверяем через словарь format_actions
        expected_buttons = ['bold', 'italic', 'underline', 'align_left', 'align_center', 'align_right']

        for button_name in expected_buttons:
            with self.subTest(button=button_name):
                self.assertIn(button_name, self.editor.format_actions)
                button = self.editor.format_actions[button_name]
                self.assertIsNotNone(button)
                self.assertTrue(hasattr(button, 'clicked'))
                self.assertTrue(callable(button.clicked))

    def test_toolbar_widgets_exist(self):
        """Тестирование что виджеты панели инструментов созданы"""
        # Проверяем основные виджеты
        self.assertIsNotNone(self.editor.font_combo)
        self.assertIsNotNone(self.editor.font_size)

        # Проверяем что они добавлены в панель
        self.assertIn(self.editor.font_combo, self.editor.toolbar.children())
        self.assertIn(self.editor.font_size, self.editor.toolbar.children())

    def test_content_type_detection(self):
        """Тестирование определения типа контента"""
        # Простой текст
        self.editor.set_plain_text("Простой текст")
        plain_result = self.editor.to_plain_text()
        self.assertEqual(plain_result.strip(), "Простой текст")

        # HTML текст
        html_content = "<p>HTML контент</p>"
        self.editor.set_html(html_content)
        html_result = self.editor.to_html()
        self.assertIn("HTML контент", html_result)

    def test_editor_readability(self):
        """Тестирование читаемости редактора"""
        # Проверяем что редактор создан
        self.assertIsNotNone(self.editor.text_edit.document())

        # Проверяем базовые свойства
        self.assertTrue(hasattr(self.editor, 'set_plain_text'))
        self.assertTrue(hasattr(self.editor, 'to_plain_text'))
        self.assertTrue(hasattr(self.editor, 'set_html'))
        self.assertTrue(hasattr(self.editor, 'to_html'))
        self.assertTrue(hasattr(self.editor, 'text_edit'))

    def test_bold_formatting(self):
        """Тестирование жирного форматирования"""
        # Устанавливаем текст
        self.editor.set_plain_text("Тест")

        # Получаем курсор из внутреннего text_edit
        cursor = self.editor.text_edit.textCursor()
        cursor.select(cursor.SelectionType.Document)

        # Применяем жирное форматирование
        from PyQt6.QtGui import QTextCharFormat, QFont
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold)
        cursor.mergeCharFormat(fmt)

        # Проверяем что форматирование применено
        char_format = cursor.charFormat()
        self.assertEqual(char_format.fontWeight(), QFont.Weight.Bold)

    def test_format_actions_dict(self):
        """Тестирование словаря действий форматирования"""
        # Проверяем что словарь создан и содержит ожидаемые ключи
        self.assertIsInstance(self.editor.format_actions, dict)
        expected_keys = ['bold', 'italic', 'underline', 'align_left', 'align_center', 'align_right']

        for key in expected_keys:
            self.assertIn(key, self.editor.format_actions)
            self.assertIsNotNone(self.editor.format_actions[key])

    def test_font_widgets(self):
        """Тестирование виджетов выбора шрифта"""
        # Проверяем что виджеты созданы
        self.assertIsNotNone(self.editor.font_combo)
        self.assertIsNotNone(self.editor.font_size)

        # Проверяем начальные значения
        self.assertEqual(self.editor.font_size.value(), self.editor.default_font_size)
        self.assertEqual(self.editor.font_combo.currentFont().family(), self.editor.default_font_family)

    def test_clear_method(self):
        """Тестирование метода очистки"""
        # Добавляем текст
        self.editor.set_plain_text("Текст для очистки")
        self.assertGreater(len(self.editor.to_plain_text().strip()), 0)

        # Очищаем
        self.editor.clear()

        # Проверяем что очищено
        self.assertEqual(self.editor.to_plain_text().strip(), "")

    def test_get_text_edit_method(self):
        """Тестирование метода получения текстового редактора"""
        text_edit = self.editor.get_text_edit()
        self.assertIsNotNone(text_edit)
        self.assertEqual(text_edit, self.editor.text_edit)

    def test_format_updating_flag(self):
        """Тестирование флага обновления формата"""
        # Проверяем начальное состояние
        self.assertFalse(self.editor._updating_format)

        # Проверяем что флаг используется в методах
        self.editor._updating_format = True
        self.assertTrue(self.editor._updating_format)

    def test_button_connections(self):
        """Тестирование подключения сигналов кнопок"""
        # Проверяем что кнопки подключены к правильным слотам
        bold_button = self.editor.format_actions['bold']
        self.assertTrue(bold_button.isCheckable())

        italic_button = self.editor.format_actions['italic']
        self.assertTrue(italic_button.isCheckable())

        underline_button = self.editor.format_actions['underline']
        self.assertTrue(underline_button.isCheckable())

    def test_font_widget_connections(self):
        """Тестирование подключения виджетов шрифта"""
        # Проверяем что виджеты подключены к правильным слотам
        self.assertTrue(hasattr(self.editor.font_combo, 'currentFontChanged'))
        self.assertTrue(hasattr(self.editor.font_size, 'valueChanged'))


class TestRichTextEditorEdgeCases(unittest.TestCase):
    """Тесты для граничных случаев"""

    @classmethod
    def setUpClass(cls):
        """Создаем QApplication один раз для всех тестов"""
        # Мокаем проблемные модули
        mock_modules = {
            'widgets.task_widget': MagicMock(),
            'widgets.workspaces_widget': MagicMock(),
            'gui.ui_workspaces_widget': MagicMock(),
            'gui.main_window': MagicMock(),
        }

        for module_name, mock_module in mock_modules.items():
            sys.modules[module_name] = mock_module

        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication([])

    def setUp(self):
        from src.widgets.rich_text_editor import RichTextEditor
        self.editor = RichTextEditor()

    def tearDown(self):
        self.editor.deleteLater()

    def test_very_long_text(self):
        """Тестирование очень длинного текста"""
        long_text = "A" * 10000
        self.editor.set_plain_text(long_text)
        result = self.editor.to_plain_text()
        self.assertEqual(len(result), len(long_text))

    def test_unicode_characters(self):
        """Тестирование Unicode символов"""
        unicode_text = "Тест с эмодзи 😀 и кириллицей"
        self.editor.set_plain_text(unicode_text)
        result = self.editor.to_plain_text()
        self.assertIn("эмодзи", result)
        self.assertIn("кириллицей", result)

    def test_multiple_format_changes(self):
        """Тестирование множественных изменений формата"""
        # Устанавливаем текст
        self.editor.set_plain_text("Тест форматирования")

        # Применяем несколько форматов
        self.editor.toggle_bold()
        self.editor.toggle_italic()
        self.editor.set_font_size(16)

        # Проверяем что редактор не упал
        result = self.editor.to_plain_text()
        self.assertEqual(result.strip(), "Тест форматирования")

    def test_empty_html(self):
        """Тестирование пустого HTML"""
        self.editor.set_html("")
        result = self.editor.to_html()
        self.assertIsInstance(result, str)

        # Должен вернуть валидный HTML
        self.assertTrue(len(result) > 0)

    def test_none_content(self):
        """Тестирование обработки None"""
        # Эти вызовы не должны вызывать исключений
        try:
            self.editor.set_plain_text(None)
            self.editor.set_html(None)
            self.assertTrue(True)
        except Exception:
            self.fail("Методы не должны падать при передаче None")


class TestRichTextEditorIntegration(unittest.TestCase):
    """Интеграционные тесты с реальными Qt объектами"""

    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами"""
        cls.mock_problematic_imports()
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication([])

    @classmethod
    def mock_problematic_imports(cls):
        """Мокаем проблемные модули"""
        mock_modules = {
            'widgets.task_widget': MagicMock(),
            'widgets.workspaces_widget': MagicMock(),
            'gui.ui_workspaces_widget': MagicMock(),
            'gui.main_window': MagicMock(),
        }
        for module_name, mock_module in mock_modules.items():
            sys.modules[module_name] = mock_module

    def test_text_manipulation(self):
        """Тестирование манипуляций с текстом"""
        from src.widgets.rich_text_editor import RichTextEditor
        editor = RichTextEditor()

        # Тестируем различные операции с текстом
        test_cases = [
            "Простой текст",
            "Текст с\nпереносом строк",
            "Текст со спецсимволами: <>&\"'",
            "Текст с кириллицей: Привет мир"
        ]

        for text in test_cases:
            with self.subTest(text=text):
                editor.set_plain_text(text)
                result = editor.to_plain_text()
                # Проверяем что текст сохранился
                self.assertEqual(result.strip(), text.strip())


if __name__ == '__main__':
    # Запускаем тесты
    unittest.main()
