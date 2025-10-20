"""
Главный файл запуска приложения
"""
import os
import sys
import traceback
from pathlib import Path


def setup_paths():
    """Настройка путей для импорта модулей"""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent

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

    if getattr(sys, 'frozen', False):
        input("Нажмите Enter для выхода...")

    sys.exit(1)


sys.excepthook = handle_exception
app_base_path = setup_paths()


def main():
    """Метод запуска приложения"""
    try:
        print("🚀 Запуск приложения...")
        print(f"✅ Base path: {app_base_path}")
        print(f"✅ Sys.path: {sys.path}")

        # pylint: disable=unused-import, no-name-in-module
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QTimer
        # pylint: enable=unused-import, no-name-in-module

        print("✅ PyQt6 модули импортированы")

        # Пересоздаем QApplication если нужно
        app = QApplication.instance()
        if app is not None:
            print("⚠️ Принудительное закрытие предыдущего экземпляра QApplication")
            app.quit()
            QTimer.singleShot(100, lambda: None)

        # Создаем новое приложение
        app = QApplication(sys.argv)
        app.setApplicationName("MINDSPACE")
        app.setApplicationVersion("1.0")
        print("✅ QApplication создан")

        # Проверяем путь к иконке
        icon_path = app_base_path / "assets" / "icons" / "app_icon.png"

        from gui.main_window import MainWindow
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

        if getattr(sys, 'frozen', False):
            input("Нажмите Enter для выхода...")

        sys.exit(1)


if __name__ == "__main__":
    main()
