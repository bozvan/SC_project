import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.widgets.tags_widget import TagsWidget


class SimpleTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Простой тест виджета тегов")
        self.setGeometry(200, 200, 300, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Инициализация менеджеров
        try:
            db_manager = DatabaseManager()
            tag_manager = TagManager(db_manager)

            # Создаем виджет тегов
            self.tags_widget = TagsWidget(tag_manager)
            self.tags_widget.tag_selected.connect(self.on_tag_selected)
            self.tags_widget.tag_created.connect(self.on_tag_created)
            self.tags_widget.tag_deleted.connect(self.on_tag_deleted)

            layout.addWidget(self.tags_widget)

            print("✅ Виджет тегов создан успешно!")

        except Exception as e:
            print(f"❌ Ошибка при создании виджета тегов: {e}")
            import traceback
            traceback.print_exc()

    def on_tag_selected(self, tag_name):
        print(f"🏷️ Выбран тег: {tag_name}")

    def on_tag_created(self, tag_name):
        print(f"✅ Создан тег: {tag_name}")

    def on_tag_deleted(self, tag_name):
        print(f"🗑️ Удален тег: {tag_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SimpleTestWindow()
    window.show()

    print("🚀 Простой тест запущен")
    sys.exit(app.exec())