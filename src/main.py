# main.py
import os
import sys
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon

# Глобальная переменная для доступа к сплеш-скрину
splash_screen = None


def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальный обработчик исключений"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    print("❌ Критическая ошибка:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

    global splash_screen
    if splash_screen:
        splash_screen.close()

    sys.exit(1)


sys.excepthook = handle_exception
icon_path = "assets/icons/icon3.png"


def update_progress(value, message=""):
    """Обновляет прогресс сплеш-скрина"""
    global splash_screen
    if splash_screen:
        splash_screen.set_progress(value)
        if message:
            splash_screen.loading_text.setText(message)
            print(f"🔄 {message}")


def initialize_application():
    """Инициализирует приложение с прогрессом"""
    try:
        # Этап 1: Инициализация базы данных (0-30%)
        update_progress(30, "Инициализация базы данных...")
        from src.core.database_manager import DatabaseManager
        db = DatabaseManager("smart_organizer.db")
        db.migrate_database()

        # Этап 2: Инициализация менеджеров (30-60%)
        update_progress(60, "Загрузка менеджеров...")
        from src.core.tag_manager import TagManager
        from src.core.note_manager import NoteManager
        from src.core.task_manager import TaskManager
        from src.core.bookmark_manager import BookmarkManager

        tag_manager = TagManager(db)
        note_manager = NoteManager(db, tag_manager)
        task_manager = TaskManager(db)
        bookmark_manager = BookmarkManager(db)

        # Этап 3: Импорт GUI компонентов (60-90%)
        update_progress(90, "Настройка интерфейса...")
        from src.gui.main_window import MainWindow

        # Создаем главное окно
        main_window = MainWindow()
        main_window.setWindowIcon(QIcon(icon_path))

        update_progress(100, "Завершено!")
        return main_window

    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        traceback.print_exc()
        raise


def main():
    try:
        print("🚀 Запуск приложения...")

        # Принудительно закрываем существующие соединения
        app = QApplication.instance()
        if app is not None:
            print("⚠️ Принудительное закрытие предыдущего экземпляра QApplication")
            app.quit()
            QTimer.singleShot(1000, lambda: None)

        # Создаем новый экземпляр
        app = QApplication(sys.argv)
        app.setApplicationName("Smart Organizer")
        app.setApplicationVersion("1.0")

        # Устанавливаем прозрачность для всего приложения
        app.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)

        print("✅ QApplication создан")

        # Импортируем и создаем сплеш-скрин
        from src.gui.splash_screen import AnimatedSplashScreen, create_splash_pixmap

        global splash_screen
        pixmap = create_splash_pixmap()
        splash_screen = AnimatedSplashScreen(pixmap, QIcon(icon_path))

        # ⭐ ЦЕНТРИРОВАНИЕ ОКНА ЗАГРУЗКИ:
        # Получаем размеры экрана
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Получаем размеры сплеш-скрина
        splash_width = splash_screen.width()
        splash_height = splash_screen.height()

        # Вычисляем координаты для центрирования
        x = (screen_geometry.width() - splash_width) // 2
        y = (screen_geometry.height() - splash_height) // 2

        # Устанавливаем позицию
        splash_screen.move(x, y)

        splash_screen.show()

        # Имитируем загрузку с плавным прогрессом
        def update_progress_animation():
            current = splash_screen.progress + 1
            if current <= 100:
                splash_screen.set_progress(current)

                # Обновляем текст в зависимости от прогресса
                if current < 20:
                    splash_screen.loading_text.setText("Подготовка...")
                elif current < 40:
                    splash_screen.loading_text.setText("Загрузка модулей...")
                elif current < 70:
                    splash_screen.loading_text.setText("Инициализация данных...")
                elif current < 90:
                    splash_screen.loading_text.setText("Настройка интерфейса...")
                else:
                    splash_screen.loading_text.setText("Завершение...")

                # Разное время для разных этапов загрузки
                delay = 20 if current < 30 else 30 if current < 70 else 50
                QTimer.singleShot(delay, update_progress_animation)
            else:
                # Когда прогресс достиг 100%, запускаем реальную инициализацию
                start_real_initialization()

        def start_real_initialization():
            """Запускает реальную инициализацию после завершения анимации"""
            try:
                main_window = initialize_application()

                # ⭐ ЦЕНТРИРОВАНИЕ ГЛАВНОГО ОКНА (опционально):
                # Получаем размеры главного окна
                window_width = main_window.width()
                window_height = main_window.height()

                # Вычисляем координаты для центрирования
                x = (screen_geometry.width() - window_width) // 2
                y = (screen_geometry.height() - window_height) // 2

                # Устанавливаем позицию главного окна
                main_window.move(x, y)

                # Короткая задержка перед показом главного окна
                QTimer.singleShot(300, lambda: show_main_window(main_window))

            except Exception as e:
                print(f"❌ Ошибка при инициализации: {e}")
                traceback.print_exc()
                splash_screen.close()
                sys.exit(1)

        def show_main_window(main_window):
            """Показывает главное окно и закрывает сплеш-скрин"""
            # Устанавливаем иконку для главного окна
            try:
                if os.path.exists(icon_path):
                    main_window.setWindowIcon(QIcon(icon_path))
            except Exception as e:
                print(f"⚠️ Не удалось установить иконку окна: {e}")

            main_window.show()
            splash_screen.finish(main_window)
            print("✅ Главное окно показано")

        # Запускаем загрузку
        QTimer.singleShot(300, update_progress_animation)

        # Принудительный выход при закрытии окна
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
