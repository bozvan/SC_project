# 📖 Справочник API MINDSPACE (кратко)

## 🗄️ DatabaseManager
Управляет подключением к SQLite и схемой данных.
```python
__init__(db_path="smart_organizer.db")
_get_connection() -> sqlite3.Connection
execute(sql, params=()) -> Cursor
execute_transaction(queries: List[Tuple[str, tuple]])
_init_db()
```
**Назначение:** централизованная работа с БД, транзакции, создание таблиц.

---

## 📝 NoteManager
Операции с заметками и закладками.
```python
create(title, content, tags, content_type, note_type, url, workspace_id) -> Note
get(note_id) -> Note
update(note_id, **kwargs) -> bool
delete(note_id) -> bool
search(search_text, tag_names, note_type, workspace_id) -> List[Note]
```
**Назначение:** управление заметками, HTML/plain контентом и тегами.

---

## ✅ TaskManager
Управляет задачами, связанными с заметками.
```python
create_task(note_id, description, due_date, priority, is_completed, workspace_id) -> Task
create_standalone_task(title, description, due_date, priority, tags, workspace_id) -> Task
get_tasks_for_note(note_id) -> List[Task]
update_task(task_id, **kwargs) -> bool
toggle_task_completion(task_id) -> bool
get_urgent_tasks(workspace_id) -> List[Task]
```
**Назначение:** приоритеты, сроки, статусы выполнения задач.

---

## 🔖 BookmarkManager
Работа с веб-закладками и метаданными.
```python
create(url, title, description, tags, favicon_url, workspace_id) -> WebBookmark
add_bookmark_with_metadata(url, tags, workspace_id) -> WebBookmark
parse_url_metadata(url) -> Dict
get_all(workspace_id) -> List[WebBookmark]
search(search_text, workspace_id) -> List[WebBookmark]
```
**Назначение:** сохранение ссылок с автоматическим извлечением данных.

---

## 📁 WorkspaceManager
Создание и управление рабочими пространствами.
```python
create_workspace(name, description) -> Workspace
get_all_workspaces() -> List[Workspace]
get_workspace(workspace_id) -> Workspace
delete_workspace(workspace_id) -> bool
get_workspace_stats(workspace_id) -> Dict
```
**Назначение:** изоляция данных по проектам и контекстам.

---

## 🏷️ TagManager
Работа с тегами.
```python
create(name, workspace_id) -> Tag
get_all(workspace_id) -> List[Tag]
get_tags_for_note(note_id) -> List[Tag]
get_popular_tags(workspace_id, limit) -> List[Tag]
```
**Назначение:** гибкое тегирование и быстрый поиск по ним.

---

## 🎨 ThemeManager
Настройки интерфейса и тем оформления.
```python
apply_theme(theme_name)
set_theme(theme_name)
get_current_theme() -> str
```
**Назначение:** переключение между светлой/тёмной темами.

---

## ⚙️ SettingsManager
Работа с пользовательскими настройками.
```python
get_last_workspace() -> int
set_last_workspace(workspace_id)
get_window_geometry()
set_window_geometry(geometry)
```
**Назначение:** сохранение интерфейсных параметров и последнего состояния.

---

## 🔄 Сигналы (PyQt)
```python
workspaceDeleted = pyqtSignal(int)
```
**Назначение:** уведомление об удалении рабочего пространства.
