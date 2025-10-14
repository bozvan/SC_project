#!/usr/bin/env python3
"""
Тестовый скрипт для проверки модуля рабочих пространств
"""

import sys
import os
import tempfile

# Добавляем путь к корню проекта для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database_manager import DatabaseManager
from src.core.workspace_manager import WorkspaceManager
from src.core.note_manager import NoteManager
from src.core.task_manager import TaskManager
from src.core.bookmark_manager import BookmarkManager
from src.core.tag_manager import TagManager


def test_workspace_functionality():
    """Тестирует функциональность рабочих пространств"""
    print("🧪 ТЕСТИРОВАНИЕ РАБОЧИХ ПРОСТРАНСТВ")
    print("=" * 50)

    # Создаем временную БД
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        db_path = temp_db.name

    try:
        # Инициализируем менеджеры
        db_manager = DatabaseManager(db_path)
        tag_manager = TagManager(db_manager)
        workspace_manager = WorkspaceManager(db_manager)
        note_manager = NoteManager(db_manager, tag_manager)
        task_manager = TaskManager(db_manager)
        bookmark_manager = BookmarkManager(db_manager)

        print("✅ Менеджеры инициализированы")

        # Тест 1: Получение workspace по умолчанию
        print("\n1. 📁 Тест получения workspace по умолчанию")
        default_workspace = workspace_manager.get_default_workspace()
        if default_workspace:
            print(f"   ✅ Workspace по умолчанию: {default_workspace}")
        else:
            print("   ❌ Не удалось получить workspace по умолчанию")
            return False

        # Тест 2: Создание нового workspace
        print("\n2. 📁 Тест создания нового workspace")
        new_workspace = workspace_manager.create_workspace("Проект X", "Рабочее пространство для проекта X")
        if new_workspace:
            print(f"   ✅ Создан новый workspace: {new_workspace}")
        else:
            print("   ❌ Не удалось создать новый workspace")
            return False

        # Тест 3: Получение всех workspace
        print("\n3. 📁 Тест получения всех workspace")
        all_workspaces = workspace_manager.get_all_workspaces()
        print(f"   ✅ Всего workspace: {len(all_workspaces)}")
        for ws in all_workspaces:
            print(f"      - {ws}")

        # Тест 4: Создание заметки в конкретном workspace
        print("\n4. 📝 Тест создания заметки в workspace")
        note_in_workspace = note_manager.create(
            "Заметка в проекте X",
            "Содержимое заметки",
            workspace_id=new_workspace.id
        )
        if note_in_workspace:
            print(f"   ✅ Создана заметка в workspace {new_workspace.id}: {note_in_workspace}")
        else:
            print("   ❌ Не удалось создать заметку в workspace")

        # Тест 5: Создание задачи в workspace
        print("\n5. ✅ Тест создания задачи в workspace")
        task_in_workspace = task_manager.create_task(
            note_id=note_in_workspace.id if note_in_workspace else 1,
            description="Задача в проекте X",
            workspace_id=new_workspace.id
        )
        if task_in_workspace:
            print(f"   ✅ Создана задача в workspace {new_workspace.id}: {task_in_workspace}")
        else:
            print("   ❌ Не удалось создать задачу в workspace")

        # Тест 6: Статистика workspace
        print("\n6. 📊 Тест статистики workspace")
        stats = workspace_manager.get_workspace_stats(new_workspace.id)
        print(f"   ✅ Статистика workspace {new_workspace.id}:")
        print(f"      - Заметок: {stats['notes_count']}")
        print(f"      - Задач: {stats['tasks_count']}")
        print(f"      - Активных задач: {stats['active_tasks_count']}")
        print(f"      - Всего элементов: {stats['total_items']}")

        # Тест 7: Получение заметок по workspace
        print("\n7. 📝 Тест получения заметок по workspace")
        notes_in_workspace = note_manager.get_notes_by_workspace(new_workspace.id)
        print(f"   ✅ Заметок в workspace {new_workspace.id}: {len(notes_in_workspace)}")
        for note in notes_in_workspace:
            print(f"      - {note}")

        # Тест 8: Обновление workspace
        print("\n8. 📁 Тест обновления workspace")
        success = workspace_manager.update_workspace(
            new_workspace.id,
            "Проект X - Обновленный",
            "Обновленное описание"
        )
        if success:
            print(f"   ✅ Workspace {new_workspace.id} обновлен")
            updated_workspace = workspace_manager.get_workspace(new_workspace.id)
            print(f"      Обновленное имя: {updated_workspace.name}")
        else:
            print("   ❌ Не удалось обновить workspace")

        # Тест 9: Попытка удаления workspace по умолчанию
        print("\n9. 📁 Тест попытки удаления workspace по умолчанию")
        delete_default_success = workspace_manager.delete_workspace(default_workspace.id)
        if not delete_default_success:
            print("   ✅ Корректно запрещено удаление workspace по умолчанию")
        else:
            print("   ❌ Ошибка: удален workspace по умолчанию")

        # Тест 10: Удаление созданного workspace
        print("\n10. 📁 Тест удаления workspace")
        delete_success = workspace_manager.delete_workspace(new_workspace.id)
        if delete_success:
            print(f"   ✅ Workspace {new_workspace.id} удален")

            # Проверяем, что workspace действительно удален
            deleted_workspace = workspace_manager.get_workspace(new_workspace.id)
            if deleted_workspace is None:
                print("   ✅ Workspace действительно удален из БД")
            else:
                print("   ❌ Workspace все еще существует в БД")
        else:
            print("   ❌ Не удалось удалить workspace")

        print("\n" + "=" * 50)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Удаляем временную БД
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
                print(f"✅ Временная БД удалена: {db_path}")
        except:
            pass


if __name__ == "__main__":
    success = test_workspace_functionality()
    sys.exit(0 if success else 1)
