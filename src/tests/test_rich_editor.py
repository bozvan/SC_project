import sys
import os

# Добавляем путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from src.widgets.rich_text_editor import RichTextEditor


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест богатого текстового редактора")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Кнопки для тестирования
        button_layout = QHBoxLayout()

        test_html_btn = QPushButton("Тест HTML")
        test_html_btn.clicked.connect(self.test_html)
        button_layout.addWidget(test_html_btn)

        test_plain_btn = QPushButton("Тест Plain Text")
        test_plain_btn.clicked.connect(self.test_plain)
        button_layout.addWidget(test_plain_btn)

        show_content_btn = QPushButton("Показать контент")
        show_content_btn.clicked.connect(self.show_content)
        button_layout.addWidget(show_content_btn)

        layout.addLayout(button_layout)

        # Создаем наш редактор
        self.editor = RichTextEditor()
        layout.addWidget(self.editor)

        print("✅ Богатый текстовый редактор создан!")

    def test_html(self):
        """Тестирование HTML контента"""
        try:
            html_content = """
            <h1 style="color: blue;">Тест богатого редактора</h1>
            <p>Это <b>жирный</b> текст, а это <i>курсив</i>.</p>
            <ul>
                <li>Элемент списка 1</li>
                <li>Элемент списка 2</li>
            </ul>
            <p style="text-align: center;">Выровненный по центру текст</p>
            """
            self.editor.set_html(html_content)
            print("✅ HTML контент установлен")
        except Exception as e:
            print(f"❌ Ошибка при установке HTML: {e}")

    def test_plain(self):
        """Тестирование простого текста"""
        try:
            plain_text = """Это простой текст без форматирования.

            Просто несколько строк текста для тестирования.

            - Пункт 1
            - Пункт 2
            - Пункт 3"""
            self.editor.set_plain_text(plain_text)
            print("✅ Plain text установлен")
        except Exception as e:
            print(f"❌ Ошибка при установке plain text: {e}")

    def show_content(self):
        """Показать текущий контент"""
        try:
            html = self.editor.to_html()
            plain = self.editor.to_plain_text()

            print("\n" + "=" * 50)
            print("HTML контент:")
            print(html[:200] + "..." if len(html) > 200 else html)
            print("\nPlain text контент:")
            print(plain[:200] + "..." if len(plain) > 200 else plain)
            print("=" * 50)
        except Exception as e:
            print(f"❌ Ошибка при получении контента: {e}")


def main():
    try:
        app = QApplication(sys.argv)

        window = TestWindow()
        window.show()

        print("🚀 Тестовое окно запущено!")
        print("📝 Проверьте работу кнопок форматирования на панели инструментов")

        return app.exec()

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())