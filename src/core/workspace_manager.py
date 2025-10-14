from typing import List, Optional
from datetime import datetime
from .models import Workspace, Note, Task, WebBookmark
from .database_manager import DatabaseManager


class WorkspaceManager:
    """Менеджер для работы с рабочими пространствами"""

    def __init__(self, db_manager: DatabaseManager):
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
        """Удаляет рабочее пространство"""
        # Нельзя удалить рабочее пространство по умолчанию
        workspace = self.get_workspace(workspace_id)
        if workspace and workspace.is_default:
            print("❌ Нельзя удалить рабочее пространство по умолчанию")
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Удаляем все связанные данные (благодаря CASCADE в БД это должно происходить автоматически)
                # Но для безопасности можно добавить явное удаление

                # Удаляем само рабочее пространство
                cursor.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
                conn.commit()

                success = cursor.rowcount > 0
                if success:
                    print(f"✅ Рабочее пространство {workspace_id} удалено")
                else:
                    print(f"❌ Рабочее пространство {workspace_id} не найдено")
                return success

        except Exception as e:
            print(f"❌ Ошибка при удалении рабочего пространства: {e}")
            return False

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
