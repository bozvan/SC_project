import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplashScreen,
                             QProgressBar, QLabel, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtProperty, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon

# Импортируем MainWindow из вашего модуля
try:
    from gui.main_window import MainWindow
except ImportError:
    # Если модуль не найден, используем локальный класс как запасной вариант
    print("Модуль gui.main_window не найден, используется локальный MainWindow")


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Main Application")
            self.setGeometry(300, 300, 800, 600)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            layout = QVBoxLayout()
            label = QLabel("Добро пожаловать в приложение!")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            central_widget.setLayout(layout)


class SmoothProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(int)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.setValue(value)

    def set_progress_animated(self, value):
        self.animation.setStartValue(self._progress)
        self.animation.setEndValue(value)
        self.animation.start()


class AnimatedSplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.progress = 0
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.progress_bar = SmoothProgressBar(self)
        self.progress_bar.setGeometry(40, pixmap.height() - 80,
                                      pixmap.width() - 80, 25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 12px;
                text-align: center;
                color: #2c3e50;
                font-weight: bold;
                background-color: rgba(236, 240, 241, 0.8);
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #9b59b6, stop:1 #e74c3c);
                border-radius: 10px;
                margin: 2px;
            }
        """)

        self.loading_text = QLabel("Загрузка...", self)
        self.loading_text.setGeometry(0, pixmap.height() - 40,
                                      pixmap.width(), 20)
        self.loading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_text.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 12px;
                background: transparent;
            }
        """)

    def set_progress(self, value):
        self.progress = value
        self.progress_bar.set_progress_animated(value)
        self.repaint()


def create_gradient_background(width, height):
    """Создает градиентный фон для сплеш-скрина"""
    pixmap = QPixmap(width, height)
    painter = QPainter(pixmap)

    from PyQt6.QtGui import QLinearGradient
    gradient = QLinearGradient(0, 0, width, height)
    gradient.setColorAt(0.0, QColor(102, 126, 234))
    gradient.setColorAt(1.0, QColor(118, 75, 162))

    painter.fillRect(0, 0, width, height, gradient)

    painter.setBrush(QColor(255, 255, 255, 180))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(20, 20, width - 40, height - 120, 15, 15)

    painter.end()
    return pixmap


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/icons/app_icon.png"))

    try:
        pixmap = QPixmap("assets/icons/app_icon.png")
        pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)

        if pixmap.isNull():
            print("Файл app_icon.png не найден. Создаю градиентный фон...")
            pixmap = create_gradient_background(500, 400)

            painter = QPainter(pixmap)
            painter.setBrush(QColor(52, 152, 219))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(150, 80, 200, 200)

            painter.setPen(QColor(255, 255, 255))
            font = QFont("Arial", 24, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(QRect(150, 80, 200, 200),
                             Qt.AlignmentFlag.AlignCenter, "LOGO")

            font.setPointSize(14)
            painter.setFont(font)
            painter.setPen(QColor(44, 62, 80))
            painter.drawText(QRect(50, 280, 400, 40),
                             Qt.AlignmentFlag.AlignCenter, "Мое Приложение")
            painter.end()
    except Exception as e:
        print(f"Ошибка загрузки иконки: {e}")
        pixmap = create_gradient_background(500, 400)

    splash = AnimatedSplashScreen(pixmap)
    splash.show()

    # Сохраняем ссылку на главное окно в глобальной переменной
    global main_window
    main_window = None

    def update_progress():
        current = splash.progress + 1
        if current <= 100:
            splash.set_progress(current)
            delay = 20 if current < 30 else 30 if current < 70 else 50
            QTimer.singleShot(delay, update_progress)
        else:
            # Создаем и показываем главное окно
            global main_window
            main_window = MainWindow()
            main_window.show()

            # Закрываем сплеш-скрин
            splash.close()

            print("✅ Главное окно успешно показано")

    # Запускаем загрузку
    QTimer.singleShot(500, update_progress)

    # Запускаем главный цикл приложения
    result = app.exec()
    print("Приложение завершено")
    sys.exit(result)


if __name__ == "__main__":
    main()
