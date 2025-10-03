import sys
import os
import faulthandler
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

sys.path.append(os.path.dirname(__file__))
from gui.main_window import MainWindow


def main():
    """Главная функция приложения"""
    app = QApplication(sys.argv)
    app.setApplicationName("Умный Органайзер")
    app.setWindowIcon(QIcon("assets/icons/icon_copy.png"))
    app.setApplicationVersion("1.0")

    window = MainWindow()
    window.show()

    print("Умный Органайзер запущен!")
    print("Использовать debug_console.py для создания тестовых данных")

    sys.exit(app.exec())


if __name__ == "__main__":
    faulthandler.enable()  # start @ the beginning
    main()