import sys
import traceback
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer


def get_base_path():
    """Определяет базовый путь для ресурсов"""
    if getattr(sys, 'frozen', False):
        # Запуск из собранного приложения
        return Path(sys.executable).parent
    else:
        # Запуск из исходного кода
        return Path(__file__).parent


def setup_paths():
    """Настраивает пути импорта"""
    base_path = get_base_path()

    # Добавляем пути для импорта модулей
    if str(base_path) not in sys.path:
        sys.path.insert(0, str(base_path))

    # Добавляем подпапки
    for folder in ['core', 'gui', 'widgets']:
        folder_path = base_path / folder
        if folder_path.exists() and str(folder_path) not in sys.path:
            sys.path.insert(0, str(folder_path))

    return base_path


def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальный обработчик исключений"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    print("❌ Критическая ошибка:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    sys.exit(1)


sys.excepthook = handle_exception

# Инициализация путей
app_base_path = setup_paths()


def main():
    try:
        print("🚀 Запуск приложения...")
        app = QApplication.instance()
        if app is not None:
            print("⚠️  Принудительное закрытие предыдущего экземпляра QApplication")
            app.quit()
            QTimer.singleShot(1000, lambda: None)  # Даем время на завершение

        app = QApplication(sys.argv)
        # app.setStyle('Fusion')
        app.setApplicationName("Smart Organizer")
        app.setApplicationVersion("1.0")

        print("✅ QApplication создан")

        from src.gui.main_window import MainWindow

        window = MainWindow()
        window.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        print("✅ MainWindow создан")

        # Восстанавливаем состояние окна
        window.restore_window_state()

        window.show()
        print("✅ Окно показано")

        app.setQuitOnLastWindowClosed(True)
        return_code = app.exec()
        print(f"📱 Приложение завершено с кодом: {return_code}")
        sys.exit(return_code)

    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
