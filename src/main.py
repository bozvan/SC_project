import os
import sys
import traceback
from pathlib import Path


def setup_paths():
    """Настройка путей для импорта модулей"""
    if getattr(sys, 'frozen', False):
        # Запуск из собранного приложения
        base_path = Path(sys.executable).parent
    else:
        # Запуск из исходного кода
        base_path = Path(__file__).parent

    # Добавляем пути для импорта
    paths_to_add = [
        str(base_path),
        str(base_path / 'core'),
        str(base_path / 'gui'),
        str(base_path / 'widgets')
    ]

    for path in paths_to_add:
        if path not in sys.path and os.path.exists(path):
            sys.path.insert(0, path)

    return base_path


def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальный обработчик исключений"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    print("❌ Критическая ошибка:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

    # В собранном приложении ждем ввод перед закрытием
    if getattr(sys, 'frozen', False):
        input("Нажмите Enter для выхода...")

    sys.exit(1)


sys.excepthook = handle_exception

# Инициализация путей ДО всех импортов
app_base_path = setup_paths()


def main():
    try:
        print("🚀 Запуск приложения...")
        print(f"✅ Base path: {app_base_path}")
        print(f"✅ Sys.path: {sys.path}")

        # Импорты PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QTimer, Qt

        print("✅ PyQt6 модули импортированы")

        # Пробуем импортировать свои модули
        try:
            # Импортируем по одному модулю для отладки
            from core import database_manager
            print("✅ database_manager импортирован")

            from core import settings_manager
            print("✅ settings_manager импортирован")

            # Добавьте остальные по одному
        except ImportError as e:
            print(f"⚠️ Ошибка импорта core: {e}")

        try:
            from gui import main_window
            print("✅ main_window импортирован")
        except ImportError as e:
            print(f"⚠️ Ошибка импорта gui: {e}")

        try:
            from widgets import bookmarks_widget
            print("✅ bookmarks_widget импортирован")
        except ImportError as e:
            print(f"⚠️ Ошибка импорта widgets: {e}")

        # Пересоздаем QApplication если нужно
        app = QApplication.instance()
        if app is not None:
            print("⚠️ Принудительное закрытие предыдущего экземпляра QApplication")
            app.quit()
            QTimer.singleShot(100, lambda: None)

        # Создаем новое приложение
        app = QApplication(sys.argv)
        app.setApplicationName("Smart Organizer")
        app.setApplicationVersion("1.0")
        print("✅ QApplication создан")

        # 👇 ИСПРАВЛЕННЫЙ ИМПОРТ - без src.
        from gui.main_window import MainWindow

        # Проверяем путь к иконке
        icon_path = app_base_path / "assets" / "icons" / "app_icon.png"
        print(f"🔍 Ищем иконку по пути: {icon_path}")
        print(f"📁 Существует: {icon_path.exists()}")

        window = MainWindow()

        if icon_path.exists():
            window.setWindowIcon(QIcon(str(icon_path)))
            print("✅ Иконка установлена")
        else:
            print("⚠️ Иконка не найдена, используется стандартная")

        print("✅ MainWindow создан")

        # Восстанавливаем состояние окна
        try:
            window.restore_window_state()
            print("✅ Состояние окна восстановлено")
        except Exception as e:
            print(f"⚠️ Ошибка восстановления состояния: {e}")

        window.show()
        print("✅ Окно показано")

        app.setQuitOnLastWindowClosed(True)
        return_code = app.exec()
        print(f"📱 Приложение завершено с кодом: {return_code}")
        sys.exit(return_code)

    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        traceback.print_exc()

        # В собранном приложении ждем ввод перед закрытием
        if getattr(sys, 'frozen', False):
            input("Нажмите Enter для выхода...")

        sys.exit(1)


if __name__ == "__main__":
    main()