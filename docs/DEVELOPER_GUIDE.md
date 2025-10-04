
# 3. 📁 **Структура базы данных**

## 3.1 Таблицы

### notes
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    content_type TEXT DEFAULT 'plain',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### tags
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
```

### note_tag_relation
```sql
CREATE TABLE note_tag_relation (
    note_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (note_id, tag_id),
    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
)
```

### tasks
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
)
```

---

# 4. 🔧 **Расширение функциональности**

## 4.1 Добавление нового виджета

```python
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

class CustomWidget(QWidget):
    custom_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Настройка интерфейса
        pass
```

## 4.2 Интеграция в главное окно

```python
# В main_window.py
def setup_ui_simple(self):
    # Существующий код...
    
    # Добавление нового виджета
    self.custom_widget = CustomWidget()
    self.custom_widget.custom_signal.connect(self.handle_custom_signal)
    self.verticalLayout.addWidget(self.custom_widget)

def handle_custom_signal(self, data):
    # Обработка сигнала
    pass
```

---

# 5. ❓ **Часто задаваемые вопросы**

## Q: Как импортировать существующие заметки?
A: В текущей версии импорт не реализован. Можно расширить NoteManager для поддержки импорта.

## Q: Можно ли синхронизировать данные между устройствами?
A: Нет, приложение использует локальную SQLite базу данных.

## Q: Как сделать резервную копию данных?
A: Скопируйте файл `smart_organizer.db` из папки с приложением.

## Q: Поддерживаются ли вложения/файлы в заметках?
A: Нет, в текущей версии поддерживается только текстовое содержимое.

---

# 6. 📞 **Поддержка**

Для вопросов и предложений:
- Проверьте документацию по API
- Изучите структуру базы данных  
- Используйте существующие сигналы для расширения функциональности
- Следуйте паттернам существующего кода

**Приложение готово к использованию!** 🎉