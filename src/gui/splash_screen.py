# src/gui/splash_screen.py
import sys
import os
from PyQt6.QtWidgets import (QSplashScreen, QProgressBar, QLabel)
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, QRect
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QIcon


class SmoothProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(100)  # Продолжительность анимации
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # Плавное замедление

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
    def __init__(self, pixmap, icon=None):
        super().__init__(pixmap)
        self.progress = 0
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        if icon:
            self.setWindowIcon(icon)

        # Устанавливаем прозрачный фон для самого сплеш-скрина
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Создаем плавный прогресс бар
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

        # Добавляем текст загрузки
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


def create_splash_pixmap():
    """Создает полностью прозрачное изображение для сплеш-скрина"""
    width, height = 500, 400

    # Создаем полностью прозрачный pixmap
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)  # Прозрачный фон

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    try:
        # Пробуем загрузить PNG иконку
        logo_path = "assets/icons/icon3.png"
        if os.path.exists(logo_path):
            # Создаем QIcon и получаем pixmap
            app_icon = QIcon(logo_path)
            logo_pixmap = app_icon.pixmap(400, 400)

            # Центрируем логотип
            x = (width - pixmap.width()) // 2 + 50
            y = (height - pixmap.height()) // 2

            # Рисуем логотип на прозрачном фоне
            painter.drawPixmap(x, y, logo_pixmap)

        else:
            # Fallback: если файл не найден, рисуем простую иконку
            print("Файл логотипа не найден. Рисую простую иконку...")

            # Рисуем круглую иконку
            painter.setBrush(QColor(52, 152, 219, 200))  # Полупрозрачный синий
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(125, 50, 250, 250)

            # Добавляем текст
            painter.setPen(QColor(255, 255, 255, 200))  # Полупрозрачный белый
            font = QFont("Arial", 24, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(QRect(125, 50, 250, 250),
                             Qt.AlignmentFlag.AlignCenter, "📝")

    except Exception as e:
        print(f"Ошибка загрузки иконки: {e}")
        # Рисуем запасную иконку при ошибке
        painter.setBrush(QColor(52, 152, 219, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(125, 50, 250, 250)

        painter.setPen(QColor(255, 255, 255, 200))
        font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRect(125, 50, 250, 250),
                         Qt.AlignmentFlag.AlignCenter, "📝")

    painter.end()
    return pixmap