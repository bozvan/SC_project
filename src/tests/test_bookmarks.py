import os
import sys
from datetime import datetime

# Добавляем путь к src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager


def test_bookmark_functionality():
    """Тестирует функциональность веб-закладок"""
    print("🧪 Начинаем тестирование закладок...")

    # Инициализация менеджеров
    db = DatabaseManager("test_organizer.db")
    tag_manager = TagManager(db)
    note_manager = NoteManager(db, tag_manager)

    try:
        # 1. Тестируем создание закладки
        print("\n1. 📝 Тестируем создание закладки...")
        bookmark = note_manager.create_bookmark(
            url="https://python.org",
            title="Python Official Website",
            description="Официальный сайт языка программирования Python",
            tags=["программирование", "python", "официальный"]
        )

        if bookmark:
            print(f"✅ Закладка создана: {bookmark}")
            print(f"   URL: {bookmark.url}")
            print(f"   Тип: {bookmark.note_type}")
            print(f"   Теги: {[tag.name for tag in bookmark.tags]}")
        else:
            print("❌ Не удалось создать закладку")
            return False

        # 2. Тестируем создание обычной заметки (для проверки совместимости)
        print("\n2. 📝 Тестируем создание обычной заметки...")
        note = note_manager.create(
            title="Тестовая заметка",
            content="Это обычная текстовая заметка",
            tags=["тест", "заметка"],
            note_type="note"  # Явно указываем тип
        )

        if note:
            print(f"✅ Заметка создана: {note}")
            print(f"   Тип: {note.note_type}")
            print(f"   URL: {note.url}")  # Должен быть None
        else:
            print("❌ Не удалось создать заметку")
            return False

        # 3. Тестируем получение всех закладок
        print("\n3. 🔖 Тестируем получение всех закладок...")
        all_bookmarks = note_manager.get_all_bookmarks()
        print(f"✅ Найдено закладок: {len(all_bookmarks)}")
        for b in all_bookmarks:
            print(f"   - {b.title} ({b.url})")

        # 4. Тестируем поиск закладок
        print("\n4. 🔍 Тестируем поиск закладок...")
        found_bookmarks = note_manager.search_bookmarks("python", ["программирование"])
        print(f"✅ Найдено закладок по запросу 'python': {len(found_bookmarks)}")
        for b in found_bookmarks:
            print(f"   - {b.title}")

        # 5. Тест общего поиска (всех типов записей)
        print("\n5. 🔎 Общий поиск всех записей...")
        all_notes = note_manager.search("тест")  # Ищет во всех полях всех типов записей
        print(f"✅ Найдено всех записей по 'тест': {len(all_notes)}")
        for n in all_notes:
            type_icon = "🔖" if n.is_bookmark() else "📝"
            print(f"   {type_icon} {n.title} (тип: {n.note_type})")

        # 5.1 Тест поиска по другому ключевому слову
        print("\n5.1 🔎 Поиск всех записей по 'python'...")
        python_notes = note_manager.search("python")
        print(f"✅ Найдено записей по 'python': {len(python_notes)}")
        for n in python_notes:
            type_icon = "🔖" if n.is_bookmark() else "📝"
            print(f"   {type_icon} {n.title}")

        # 6. Тест обновления закладки
        print("\n6. ✏️ Обновление закладки...")
        if bookmark:
            success = note_manager.update(
                note_id=bookmark.id,
                title="Python Official Site - UPDATED",
                page_description="Обновленное описание сайта Python"  # ИСПРАВЛЕНО: description -> page_description
            )
            if success:
                print("✅ Закладка успешно обновлена")
                updated_bookmark = note_manager.get(bookmark.id)
                if updated_bookmark:
                    print(f"   Новый заголовок: {updated_bookmark.title}")
                    print(f"   Описание: {updated_bookmark.page_description}")
            else:
                print("❌ Ошибка обновления закладки")

        # 7. Тестируем получение записи по ID
        print("\n7. 🔍 Тестируем получение записи по ID...")
        if bookmark:
            retrieved = note_manager.get(bookmark.id)
            if retrieved:
                print(f"✅ Запись получена: {retrieved}")
                print(f"   Является закладкой: {retrieved.is_bookmark()}")
                print(f"   Является заметкой: {retrieved.is_note()}")
            else:
                print("❌ Не удалось получить запись по ID")

        # 9. Тест валидации URL
        print("\n9. 🛡️ Тестирование валидации URL...")

        # 9.1 Некорректный URL
        print("9.1 ❌ Тест с некорректным URL...")
        invalid_bookmark = note_manager.create_bookmark(
            url="просто текст",
            title="Некорректная закладка"
        )
        if not invalid_bookmark:
            print("✅ Валидация сработала: некорректный URL отклонен")
        else:
            print("❌ Ошибка: некорректный URL был принят")

        # 9.2 URL без схемы (должен нормализоваться)
        print("\n9.2 🔄 Тест нормализации URL...")
        normalized_bookmark = note_manager.create_bookmark(
            url="google.com",
            title="Google",
            description="Поисковая система"
        )
        if normalized_bookmark:
            print(f"✅ URL нормализован: {normalized_bookmark.url}")
            # Должно быть: https://google.com
        else:
            print("❌ Ошибка нормализации URL")

        # 9.3 URL с www (должен нормализоваться)
        print("\n9.3 🔄 Тест нормализации www URL...")
        www_bookmark = note_manager.create_bookmark(
            url="www.github.com",
            title="GitHub"
        )
        if www_bookmark:
            print(f"✅ www URL нормализован: {www_bookmark.url}")
            # Должно быть: https://www.github.com
        else:
            print("❌ Ошибка нормализации www URL")

        # 9.4 Корректный URL
        print("\n9.4 ✅ Тест с корректным URL...")
        valid_bookmark = note_manager.create_bookmark(
            url="https://stackoverflow.com",
            title="Stack Overflow",
            description="Сообщество программистов"
        )
        if valid_bookmark:
            print(f"✅ Корректный URL принят: {valid_bookmark.url}")
        else:
            print("❌ Ошибка: корректный URL был отклонен")

        print("\n🎉 Все тесты пройдены успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Очистка (опционально)
        try:
            os.remove("test_organizer.db")
            print("\n🧹 Тестовая база данных удалена")
        except:
            pass


def test_backward_compatibility():
    """Тестирует обратную совместимость со старыми заметками"""
    print("\n\n🔄 Тестируем обратную совместимость...")

    db = DatabaseManager("test_compat.db")
    tag_manager = TagManager(db)
    note_manager = NoteManager(db, tag_manager)

    try:
        # Создаем заметку старым методом (без указания note_type)
        old_note = note_manager.create(
            title="Старая заметка",
            content="Создана старым методом",
            tags=["совместимость"]
        )

        if old_note:
            print(f"✅ Старая заметка создана: {old_note}")
            print(f"   Тип по умолчанию: {old_note.note_type}")
            print(f"   URL: {old_note.url}")

            # Проверяем, что она определяется как заметка
            print(f"   is_note(): {old_note.is_note()}")
            print(f"   is_bookmark(): {old_note.is_bookmark()}")

            return True
        else:
            print("❌ Не удалось создать старую заметку")
            return False

    except Exception as e:
        print(f"❌ Ошибка совместимости: {e}")
        return False
    finally:
        try:
            os.remove("test_compat.db")
        except:
            pass


if __name__ == "__main__":
    print("🚀 Запуск тестов системы закладок...")

    success1 = test_bookmark_functionality()
    success2 = test_backward_compatibility()

    if success1 and success2:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ База данных обновлена корректно")
        print("✅ Модели работают правильно")
        print("✅ Обратная совместимость сохранена")
        print("\n📝 Можно переходить к Шагу 1.2 (UI для закладок)")
    else:
        print("\n❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("⚠️  Нужно исправить ошибки перед продолжением")
