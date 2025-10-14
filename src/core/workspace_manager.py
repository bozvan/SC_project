from typing import List, Optional
from datetime import datetime

from PyQt6.QtCore import pyqtSignal, QObject

from .models import Workspace, Note, Task, WebBookmark
from .database_manager import DatabaseManager


class WorkspaceManager(QObject):
    """Менеджер для работы с рабочими пространствами"""
    workspaceDeleted = pyqtSignal(int)  # Сигнал при удалении workspace

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self._create_default_workspace()
        print("✅ Менеджер рабочих пространств инициализирован")

    def _create_default_workspace(self):
        """Создает рабочее пространство по умолчанию если его нет"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM workspaces WHERE is_default = TRUE")
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO workspaces (name, description, is_default) VALUES (?, ?, ?)",
                        ("all", "Все заметки и задачи", True)
                    )
                    conn.commit()
                    print("✅ Создано рабочее пространство по умолчанию 'all'")
        except Exception as e:
            print(f"❌ Ошибка при создании workspace по умолчанию: {e}")

    def create_workspace(self, name: str, description: str = "") -> Optional[Workspace]:
        """Создает новое рабочее пространство"""
        if not name or not name.strip():
            print("❌ Ошибка: название рабочего пространства не может быть пустым")
            return None

        name = name.strip()

        try:
            workspace_id = self.db.create_workspace(name, description)
            if workspace_id:
                workspace = Workspace(
                    name=name,
                    description=description,
                    workspace_id=workspace_id
                )
                print(f"✅ Создано рабочее пространство: {workspace}")
                return workspace
            return None
        except Exception as e:
            print(f"❌ Ошибка при создании рабочего пространства: {e}")
            return None

    def get_all_workspaces(self) -> List[Workspace]:
        """Возвращает все рабочие пространства"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, description, is_default, created_at FROM workspaces ORDER BY name")
                results = cursor.fetchall()

                workspaces = []
                for workspace_id, name, description, is_default, created_at in results:
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    workspace = Workspace(
                        name=name,
                        description=description or "",
                        workspace_id=workspace_id,
                        created_date=created_date,
                        is_default=bool(is_default)
                    )
                    workspaces.append(workspace)

                print(f"✅ Загружено рабочих пространств: {len(workspaces)}")
                return workspaces
        except Exception as e:
            print(f"❌ Ошибка при получении рабочих пространств: {e}")
            return []

    def get_workspace(self, workspace_id: int) -> Optional[Workspace]:
        """Возвращает рабочее пространство по ID"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, description, is_default, created_at FROM workspaces WHERE id = ?",
                    (workspace_id,)
                )
                result = cursor.fetchone()

                if result:
                    workspace_id, name, description, is_default, created_at = result
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    workspace = Workspace(
                        name=name,
                        description=description or "",
                        workspace_id=workspace_id,
                        created_date=created_date,
                        is_default=bool(is_default)
                    )
                    return workspace
                else:
                    print(f"❌ Рабочее пространство с ID {workspace_id} не найдено")
                    return None
        except Exception as e:
            print(f"❌ Ошибка при получении рабочего пространства: {e}")
            return None

    def get_default_workspace(self) -> Optional[Workspace]:
        """Возвращает рабочее пространство по умолчанию"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, description, is_default, created_at FROM workspaces WHERE is_default = TRUE")
                result = cursor.fetchone()

                if result:
                    workspace_id, name, description, is_default, created_at = result
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    workspace = Workspace(
                        name=name,
                        description=description or "",
                        workspace_id=workspace_id,
                        created_date=created_date,
                        is_default=bool(is_default)
                    )
                    return workspace
                else:
                    print("❌ Рабочее пространство по умолчанию не найдено")
                    return None
        except Exception as e:
            print(f"❌ Ошибка при получении рабочего пространства по умолчанию: {e}")
            return None

    def update_workspace(self, workspace_id: int, name: str, description: str = "") -> bool:
        """Обновляет рабочее пространство"""
        if not name or not name.strip():
            print("❌ Ошибка: название рабочего пространства не может быть пустым")
            return False

        name = name.strip()

        try:
            success = self.db.update_workspace(workspace_id, name, description)
            if success:
                print(f"✅ Рабочее пространство {workspace_id} обновлено: {name}")
            return success
        except Exception as e:
            print(f"❌ Ошибка при обновлении рабочего пространства: {e}")
            return False

    def delete_workspace(self, workspace_id: int) -> bool:
        """Удаляет рабочее пространство и все связанные данные"""
        # Нельзя удалить рабочее пространство по умолчанию
        workspace = self.get_workspace(workspace_id)
        if workspace and workspace.is_default:
            print("❌ Нельзя удалить рабочее пространство по умолчанию")
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # 1. Сначала получаем статистику для информации
                stats = self.get_workspace_stats(workspace_id)
                print(f"🗑️ Удаление workspace {workspace_id}: {stats['notes_count']} заметок, "
                      f"{stats['tasks_count']} задач, {stats['bookmarks_count']} закладок")

                # 2. Явно удаляем связанные данные (на случай если CASCADE не работает)

                # Удаляем теги, связанные с заметками этого workspace
                cursor.execute("""
                    DELETE FROM note_tag_relation 
                    WHERE note_id IN (SELECT id FROM notes WHERE workspace_id = ?)
                """, (workspace_id,))
                print(f"✅ Удалено связей тегов: {cursor.rowcount}")

                # Удаляем заметки
                cursor.execute("DELETE FROM notes WHERE workspace_id = ?", (workspace_id,))
                notes_deleted = cursor.rowcount
                print(f"✅ Удалено заметок: {notes_deleted}")

                # Удаляем задачи
                cursor.execute("DELETE FROM tasks WHERE workspace_id = ?", (workspace_id,))
                tasks_deleted = cursor.rowcount
                print(f"✅ Удалено задач: {tasks_deleted}")

                # Удаляем закладки
                cursor.execute("DELETE FROM bookmarks WHERE workspace_id = ?", (workspace_id,))
                bookmarks_deleted = cursor.rowcount
                print(f"✅ Удалено закладок: {bookmarks_deleted}")

                # 3. Удаляем само рабочее пространство
                cursor.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
                workspace_deleted = cursor.rowcount > 0

                if workspace_deleted:
                    conn.commit()
                    print(f"✅ Рабочее пространство {workspace_id} полностью удалено")
                    print(f"📊 Итог: {notes_deleted} заметок, {tasks_deleted} задач, "
                          f"{bookmarks_deleted} закладок удалено")

                    # Отправляем сигнал об удалении
                    self.workspaceDeleted.emit(workspace_id)

                    return True
                else:
                    conn.rollback()
                    print(f"❌ Рабочее пространство {workspace_id} не найдено")
                    return False

        except Exception as e:
            print(f"❌ Ошибка при удалении рабочего пространства: {e}")
            return False

    def _notify_workspace_deleted(self, deleted_workspace_id: int):
        """Уведомляет о удалении workspace (для обновления UI)"""
        # Этот метод будет вызываться из UI компонентов
        # В реальной реализации здесь может быть PyQt сигнал
        print(f"🔄 Workspace {deleted_workspace_id} удален, требуется обновление UI")

    def get_workspace_stats(self, workspace_id: int) -> dict:
        """Возвращает статистику по рабочему пространству"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Количество заметок
                cursor.execute("SELECT COUNT(*) FROM notes WHERE workspace_id = ?", (workspace_id,))
                notes_count = cursor.fetchone()[0]

                # Количество задач
                cursor.execute("SELECT COUNT(*) FROM tasks WHERE workspace_id = ?", (workspace_id,))
                tasks_count = cursor.fetchone()[0]

                # Количество активных задач
                cursor.execute("SELECT COUNT(*) FROM tasks WHERE workspace_id = ? AND is_completed = FALSE",
                               (workspace_id,))
                active_tasks_count = cursor.fetchone()[0]

                # Количество закладок
                cursor.execute("SELECT COUNT(*) FROM bookmarks WHERE workspace_id = ?", (workspace_id,))
                bookmarks_count = cursor.fetchone()[0]

                stats = {
                    'notes_count': notes_count,
                    'tasks_count': tasks_count,
                    'active_tasks_count': active_tasks_count,
                    'bookmarks_count': bookmarks_count,
                    'total_items': notes_count + tasks_count + bookmarks_count
                }

                print(f"📊 Статистика workspace {workspace_id}: {stats}")
                return stats

        except Exception as e:
            print(f"❌ Ошибка при получении статистики workspace: {e}")
            return {
                'notes_count': 0,
                'tasks_count': 0,
                'active_tasks_count': 0,
                'bookmarks_count': 0,
                'total_items': 0
            }
