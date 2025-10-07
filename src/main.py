import os
import sys
import traceback

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer


def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальный обработчик исключений"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    print("❌ Критическая ошибка:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    sys.exit(1)


sys.excepthook = handle_exception


def main():
    try:
        print("🚀 Запуск приложения...")

        # Принудительно закрываем существующие соединения
        app = QApplication.instance()
        if app is not None:
            print("⚠️  Принудительное закрытие предыдущего экземпляра QApplication")
            app.quit()
            QTimer.singleShot(1000, lambda: None)  # Даем время на завершение

        # Создаем новый экземпляр
        app = QApplication(sys.argv)
        app.setApplicationName("Smart Organizer")
        app.setApplicationVersion("1.0")

        print("✅ QApplication создан")

        # Импортируем здесь, чтобы избежать циклических импортов
        from src.gui.main_window import MainWindow

        window = MainWindow()
        window.setWindowIcon(QIcon("assets/icons/icon3.png"))
        print("✅ MainWindow создан")

        window.show()
        print("✅ Окно показано")

        # Принудительный выход при закрытии окна
        app.setQuitOnLastWindowClosed(True)

        return_code = app.exec()
        print(f"📱 Приложение завершено с кодом: {return_code}")

        # Принудительно закрываем приложение
        sys.exit(return_code)

    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()