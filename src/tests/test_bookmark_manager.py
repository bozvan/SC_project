import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager
from src.core.bookmark_manager import BookmarkManager


def test_bookmark_manager():
    """Тестирует BookmarkManager"""
    print("🧪 Тестирование BookmarkManager...")

    # Инициализируем менеджеры
    db = DatabaseManager("test_bookmark_manager.db")
    tag_manager = TagManager(db)
    note_manager = NoteManager(db, tag_manager)
    bookmark_manager = BookmarkManager(note_manager)

    try:
        # 1. Тест валидации URL
        print("\n1. 🛡️ Тест валидации URL...")
        test_urls = [
            "https://python.org",  # ✅ Должен пройти
            "python.org",  # ✅ Должен нормализоваться
            "www.python.org",  # ✅ Должен нормализоваться
            "github.com",  # ✅ Должен нормализоваться
            "http://example.com",  # ✅ Должен пройти
            "ftp://example.com",  # ❌ Должен быть отклонен
            "not-a-url",  # ❌ Должен быть отклонен
            "localhost",  # ✅ Должен пройти (специальный случай)
            "",  # ❌ Должен быть отклонен
        ]

        for url in test_urls:
            is_valid = bookmark_manager.validate_url(url)
            normalized = bookmark_manager.normalize_url(url)
            print(f"   '{url}' -> valid: {is_valid}, normalized: '{normalized}'")

        # 2. Тест получения метаданных (используем стабильный сайт)
        print("\n2. 🔍 Тест получения метаданных...")
        test_url = "https://example.com"  # Стабильный тестовый сайт
        metadata = bookmark_manager.parse_url_metadata(test_url)
        print(f"✅ Метаданные получены:")
        print(f"   Title: {metadata.get('title')}")
        print(f"   Description: {metadata.get('description')}")
        print(f"   Status: {metadata.get('status_code')}")

        # 3. Тест создания закладки
        print("\n3. 📝 Тест создания закладки...")
        bookmark = bookmark_manager.add_bookmark(
            url="https://example.com",
            tags=["тест", "пример"]
        )

        if bookmark:
            print(f"✅ Закладка создана: {bookmark}")
            print(f"   URL: {bookmark.url}")
            print(f"   Заголовок: {bookmark.page_title}")
            print(f"   Описание: {bookmark.page_description}")
            print(f"   Теги: {[tag.name for tag in bookmark.tags]}")
        else:
            print("❌ Не удалось создать закладку")

        # 4. Тест с недоступным URL
        print("\n4. 🚫 Тест с недоступным URL...")
        invalid_bookmark = bookmark_manager.add_bookmark(
            url="https://invalid-domain-that-does-not-exist-12345.com",
            tags=["недоступно"]
        )

        if invalid_bookmark:
            print(f"⚠️  Закладка создана (с fallback): {invalid_bookmark}")
            print(f"   Заголовок: {invalid_bookmark.page_title}")
        else:
            print("❌ Не удалось создать закладку для недоступного URL")

        print("\n🎉 Тестирование BookmarkManager завершено!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Правильно закрываем соединение с БД перед удалением
        db.close()
        # Небольшая задержка чтобы ОС освободила файл
        import time
        time.sleep(0.1)

        # Очистка
        if os.path.exists("test_bookmark_manager.db"):
            try:
                os.remove("test_bookmark_manager.db")
                print("🧹 Тестовая база удалена")
            except PermissionError:
                print("⚠️  Не удалось удалить тестовую базу (файл занят)")


if __name__ == "__main__":
    success = test_bookmark_manager()
    if success:
        print("\n✅ BookmarkManager готов к использованию!")
    else:
        print("\n❌ Обнаружены проблемы в BookmarkManager")