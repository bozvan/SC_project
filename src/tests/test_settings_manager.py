import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock, call
from PyQt6.QtCore import QSettings

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.core.settings_manager import QtSettingsManager


class TestQtSettingsManager(unittest.TestCase):
    """Тесты для QtSettingsManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Используем временные настройки
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "test_settings.ini")

        # Создаем патч для QSettings
        self.settings_patcher = patch('src.core.settings_manager.QSettings')
        self.mock_settings_class = self.settings_patcher.start()
        self.mock_settings_instance = MagicMock()
        self.mock_settings_class.return_value = self.mock_settings_instance

        # Настраиваем возвращаемые значения
        self.mock_settings_instance.value.return_value = 1  # Для get_last_workspace
        self.mock_settings_instance.fileName.return_value = self.settings_file

        # Создаем экземпляр QtSettingsManager
        self.settings_manager = QtSettingsManager()

    def tearDown(self):
        """Очистка после каждого теста"""
        self.settings_patcher.stop()
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Тест инициализации QtSettingsManager"""
        # Проверяем, что QSettings создан с правильными параметрами
        self.mock_settings_class.assert_called_once_with("SmartOrganizer", "SmartOrganizer")

        # Проверяем, что settings установлен
        self.assertEqual(self.settings_manager.settings, self.mock_settings_instance)

        # Проверяем вывод имени файла
        self.mock_settings_instance.fileName.assert_called_once()

    def test_initialization_custom_parameters(self):
        """Тест инициализации с пользовательскими параметрами"""
        # Останавливаем текущий патч
        self.settings_patcher.stop()

        with patch('src.core.settings_manager.QSettings') as mock_settings:
            mock_instance = MagicMock()
            mock_settings.return_value = mock_instance

            # Создаем менеджер с пользовательскими параметрами
            custom_manager = QtSettingsManager("TestOrg", "TestApp")

            # Проверяем, что QSettings создан с правильными параметрами
            mock_settings.assert_called_once_with("TestOrg", "TestApp")

            # Восстанавливаем патч
            self.settings_patcher.start()

    def test_get_last_workspace(self):
        """Тест получения последнего рабочего пространства"""
        # Настраиваем mock для возврата определенного значения
        self.mock_settings_instance.value.return_value = 5

        # Получаем workspace
        workspace_id = self.settings_manager.get_last_workspace()

        # Проверяем, что значение получено правильно
        self.assertEqual(workspace_id, 5)

        # Проверяем, что метод value вызван с правильными параметрами
        self.mock_settings_instance.value.assert_called_once_with("last_workspace_id", 1, type=int)

    def test_get_last_workspace_default_value(self):
        """Тест получения workspace с значением по умолчанию"""
        # Настраиваем mock для возврата None (имитируем отсутствие настройки)
        # Но QSettings с type=int вернет 0 или значение по умолчанию, а не None
        self.mock_settings_instance.value.return_value = 1  # Значение по умолчанию

        # Получаем workspace
        workspace_id = self.settings_manager.get_last_workspace()

        # Проверяем, что возвращено значение по умолчанию
        self.assertEqual(workspace_id, 1)

    def test_set_last_workspace(self):
        """Тест сохранения рабочего пространства"""
        # Сохраняем workspace
        self.settings_manager.set_last_workspace(10)

        # Проверяем, что значение установлено
        self.mock_settings_instance.setValue.assert_called_once_with("last_workspace_id", 10)

        # Проверяем, что настройки синхронизированы
        self.mock_settings_instance.sync.assert_called_once()

    def test_get_window_geometry(self):
        """Тест получения геометрии окна"""
        # Настраиваем mock для возврата тестовой геометрии
        test_geometry = b'test_geometry_data'
        self.mock_settings_instance.value.return_value = test_geometry

        # Получаем геометрию
        geometry = self.settings_manager.get_window_geometry()

        # Проверяем, что значение получено правильно
        self.assertEqual(geometry, test_geometry)

        # Проверяем, что метод value вызван с правильными параметрами
        self.mock_settings_instance.value.assert_called_once_with("window_geometry")

    def test_set_window_geometry(self):
        """Тест сохранения геометрии окна"""
        test_geometry = b'test_geometry_data'

        # Сохраняем геометрию
        self.settings_manager.set_window_geometry(test_geometry)

        # Проверяем, что значение установлено
        self.mock_settings_instance.setValue.assert_called_once_with("window_geometry", test_geometry)

    def test_get_window_state(self):
        """Тест получения состояния окна"""
        # Настраиваем mock для возврата тестового состояния
        test_state = b'test_state_data'
        self.mock_settings_instance.value.return_value = test_state

        # Получаем состояние
        state = self.settings_manager.get_window_state()

        # Проверяем, что значение получено правильно
        self.assertEqual(state, test_state)

        # Проверяем, что метод value вызван с правильными параметрами
        self.mock_settings_instance.value.assert_called_once_with("window_state")

    def test_set_window_state(self):
        """Тест сохранения состояния окна"""
        test_state = b'test_state_data'

        # Сохраняем состояние
        self.settings_manager.set_window_state(test_state)

        # Проверяем, что значение установлено
        self.mock_settings_instance.setValue.assert_called_once_with("window_state", test_state)

    def test_multiple_operations(self):
        """Тест множественных операций с настройками"""
        # Выполняем несколько операций
        self.settings_manager.set_last_workspace(3)
        workspace_id = self.settings_manager.get_last_workspace()
        self.settings_manager.set_window_geometry(b'geom')
        geometry = self.settings_manager.get_window_geometry()

        # Проверяем, что все методы вызваны
        expected_calls = [
            call.setValue("last_workspace_id", 3),
            call.sync(),
            call.value("last_workspace_id", 1, type=int),
            call.setValue("window_geometry", b'geom'),
            call.value("window_geometry")
        ]
        self.mock_settings_instance.assert_has_calls(expected_calls, any_order=False)

    def test_settings_persistence_simulation(self):
        """Тест симуляции сохранения настроек"""
        # Симулируем последовательность использования
        self.settings_manager.set_last_workspace(7)

        # "Пересоздаем" менеджер (симуляция перезапуска приложения)
        with patch('src.core.settings_manager.QSettings') as mock_settings:
            new_mock_instance = MagicMock()
            new_mock_instance.value.return_value = 7  # Возвращаем сохраненное значение
            mock_settings.return_value = new_mock_instance

            new_manager = QtSettingsManager()
            loaded_workspace = new_manager.get_last_workspace()

            # Проверяем, что значение сохранилось
            self.assertEqual(loaded_workspace, 7)

    def test_edge_cases_workspace_id(self):
        """Тест граничных случаев для workspace ID"""
        test_cases = [0, -1, 999999, 1]

        for workspace_id in test_cases:
            with self.subTest(workspace_id=workspace_id):
                # Сбрасываем mock
                self.mock_settings_instance.reset_mock()

                # Сохраняем и загружаем workspace
                self.settings_manager.set_last_workspace(workspace_id)
                self.mock_settings_instance.value.return_value = workspace_id
                loaded_id = self.settings_manager.get_last_workspace()

                # Проверяем корректность
                self.assertEqual(loaded_id, workspace_id)
                self.mock_settings_instance.setValue.assert_called_with("last_workspace_id", workspace_id)

    def test_none_values_handling(self):
        """Тест обработки None значений"""
        # Тестируем получение None значений для геометрии и состояния
        self.mock_settings_instance.value.return_value = None

        geometry = self.settings_manager.get_window_geometry()
        state = self.settings_manager.get_window_state()

        # Проверяем, что None значения корректно возвращаются
        self.assertIsNone(geometry)
        self.assertIsNone(state)

    def test_method_chaining(self):
        """Тест цепочки вызовов методов"""
        # Проверяем, что можно вызывать методы в цепочке (если бы они возвращали self)
        # Этот тест проверяет, что методы не падают при последовательном вызове
        try:
            self.settings_manager.set_last_workspace(1)
            self.settings_manager.get_last_workspace()
            self.settings_manager.set_window_geometry(b'geom')
            self.settings_manager.get_window_geometry()
            self.settings_manager.set_window_state(b'state')
            self.settings_manager.get_window_state()
        except Exception as e:
            self.fail(f"Method chaining failed with exception: {e}")

    def test_print_statements(self):
        """Тест наличия print statements (можно проверить через mock)"""
        with patch('builtins.print') as mock_print:
            # Пересоздаем менеджер для проверки print в __init__
            with patch('src.core.settings_manager.QSettings') as mock_settings:
                mock_instance = MagicMock()
                mock_instance.fileName.return_value = "/test/path/settings.ini"
                mock_settings.return_value = mock_instance

                manager = QtSettingsManager()

                # Проверяем print в __init__
                mock_print.assert_any_call("⚙️ Инициализирован QSettings: /test/path/settings.ini")

            # Проверяем print в get_last_workspace
            self.mock_settings_instance.value.return_value = 5
            self.settings_manager.get_last_workspace()
            mock_print.assert_any_call("📁 Загружен последний workspace из настроек: 5")

            # Проверяем print в set_last_workspace
            self.settings_manager.set_last_workspace(8)
            mock_print.assert_any_call("💾 Сохранен workspace в настройки: 8")

    def test_sync_called_only_for_workspace(self):
        """Тест что sync вызывается только для set_last_workspace"""
        # Устанавливаем workspace (должен вызвать sync)
        self.settings_manager.set_last_workspace(5)
        self.mock_settings_instance.sync.assert_called_once()

        # Сбрасываем mock
        self.mock_settings_instance.reset_mock()

        # Устанавливаем геометрию (не должен вызывать sync)
        self.settings_manager.set_window_geometry(b'geom')
        self.mock_settings_instance.sync.assert_not_called()

        # Устанавливаем состояние (не должен вызывать sync)
        self.settings_manager.set_window_state(b'state')
        self.mock_settings_instance.sync.assert_not_called()


class TestQtSettingsManagerIntegration(unittest.TestCase):
    """Интеграционные тесты для QtSettingsManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Очистка после каждого теста"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def test_real_qsettings_behavior(self):
        """Тест реального поведения с QSettings (использует временный файл)"""
        # Этот тест использует реальный QSettings с временным файлом
        import tempfile

        # Создаем временный файл для настроек
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            temp_settings_file = f.name

        try:
            # Создаем реальный QSettings для тестирования
            real_settings = QSettings(temp_settings_file, QSettings.Format.IniFormat)

            # Патчим QSettings чтобы он возвращал наш реальный объект
            with patch('src.core.settings_manager.QSettings') as mock_settings_class:
                mock_settings_class.return_value = real_settings

                # Создаем менеджер
                manager = QtSettingsManager("TestIntegration", "TestApp")

                # Тестируем сохранение и загрузку
                manager.set_last_workspace(42)

                # Создаем новый менеджер для проверки загрузки
                manager2 = QtSettingsManager("TestIntegration", "TestApp")
                loaded_workspace = manager2.get_last_workspace()

                # Проверяем, что значение сохранилось
                self.assertEqual(loaded_workspace, 42)

        finally:
            # Удаляем временный файл
            if os.path.exists(temp_settings_file):
                os.unlink(temp_settings_file)

    def test_settings_isolation(self):
        """Тест изоляции настроек между разными экземплярами"""
        with patch('src.core.settings_manager.QSettings') as mock_settings:
            # Создаем два мока для разных экземпляров
            mock_instance1 = MagicMock()
            mock_instance2 = MagicMock()

            # Первый вызов возвращает первый mock, второй - второй
            mock_settings.side_effect = [mock_instance1, mock_instance2]

            # Создаем два менеджера
            manager1 = QtSettingsManager("Org1", "App1")
            manager2 = QtSettingsManager("Org2", "App2")

            # Проверяем, что используются разные экземпляры QSettings
            self.assertEqual(manager1.settings, mock_instance1)
            self.assertEqual(manager2.settings, mock_instance2)

            # Проверяем, что QSettings создавался с разными параметрами
            calls = mock_settings.call_args_list
            self.assertEqual(calls[0], call("Org1", "App1"))
            self.assertEqual(calls[1], call("Org2", "App2"))


if __name__ == '__main__':
    # Запуск тестов с подробным выводом
    unittest.main(verbosity=2)