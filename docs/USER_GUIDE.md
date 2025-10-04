
# 2. 🛠️ **API Документация**

## 2.1 Core Modules

### DatabaseManager (`src/core/database_manager.py`)
```python
class DatabaseManager:
    def __init__(db_path: str = "smart_organizer.db")
    def create_note(title: str, content: str) -> Optional[int]
    def get_all_notes() -> List[Tuple]
    def get_note_by_id(note_id: int) -> Optional[Tuple]
    def search_notes(search_term: str) -> List[Tuple]
    def update_note(note_id: int, title: str, content: str) -> bool
    def delete_note(note_id: int) -> bool
```

### NoteManager (`src/core/note_manager.py`)
```python
class NoteManager:
    def create(title: str, content: str = "", tags: List[str] = None, content_type: str = "html") -> Optional[Note]
    def get(note_id: int) -> Optional[Note]
    def update(note_id: int, title: str = None, content: str = None, tags: List[str] = None, content_type: str = None) -> bool
    def delete(note_id: int) -> bool
    def search(search_text: str = "", tag_names: List[str] = None) -> List[Note]
    def get_all() -> List[Note]
    def search_by_tags(tag_names: List[str]) -> List[Note]
```

### TagManager (`src/core/tag_manager.py`)
```python
class TagManager:
    def create(name: str) -> Optional[Tag]
    def get(tag_id: int) -> Optional[Tag]
    def get_all() -> List[Tag]
    def get_by_name(name: str) -> Optional[Tag]
    def delete(tag_id: int) -> bool
    def get_tags_for_note(note_id: int) -> List[Tag]
```

### TaskManager (`src/core/task_manager.py`)
```python
class TaskManager:
    def create_task(note_id: int, description: str, is_completed: bool = False) -> Optional[Task]
    def get_task(task_id: int) -> Optional[Task]
    def get_tasks_for_note(note_id: int) -> List[Task]
    def update_task(task_id: int, description: str = None, is_completed: bool = None) -> bool
    def delete_task(task_id: int) -> bool
    def get_all_incomplete_tasks() -> List[Task]
    def toggle_task_completion(task_id: int) -> Optional[Task]
```

## 2.2 Widgets API

### RichTextEditor (`src/widgets/rich_text_editor.py`)
```python
class RichTextEditor(QWidget):
    def set_html(html_content: str)
    def to_html() -> str
    def set_plain_text(text: str)
    def to_plain_text() -> str
    def clear()
```

### TagsWidget (`src/widgets/tags_widget.py`)
```python
class TagsWidget(QWidget):
    # Signals
    tag_selected = pyqtSignal(str)    # При выборе тега
    tag_created = pyqtSignal(str)     # При создании тега  
    tag_deleted = pyqtSignal(str)     # При удалении тега
    
    def load_tags()
    def refresh()
    def get_selected_tag() -> str
```

### UpcomingTasksWidget (`src/widgets/upcoming_tasks_widget.py`)
```python
class UpcomingTasksWidget(QWidget):
    # Signals
    task_toggled = pyqtSignal(int, bool)     # task_id, is_completed
    navigate_to_note = pyqtSignal(int)       # note_id
    
    def load_tasks()
    def refresh()
```

### NotificationManager (`src/core/notification_manager.py`)
```python
class NotificationManager(QObject):
    def show_reminder(task_description: str, note_title: str = None)
    def show_custom_notification(title: str, message: str, timeout: int = 5000)
```

## 2.3 Data Models

### Note (`src/core/models.py`)
```python
class Note:
    id: Optional[int]
    title: str
    content: str
    created_date: datetime
    modified_date: datetime
    content_type: str  # "plain" или "html"
    tags: List[Tag]
```

### Tag (`src/core/models.py`)
```python
class Tag:
    id: Optional[int]
    name: str  # автоматически нормализуется в lower case
```

### Task (`src/core/models.py`)
```python
class Task:
    id: Optional[int]
    description: str
    is_completed: bool
    note_id: Optional[int]
    created_date: datetime
    updated_date: datetime
```

---
