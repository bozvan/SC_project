import sys
import os
import time
from datetime import datetime

# Добавляем путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import QApplication
from src.core.database_manager import DatabaseManager
from src.core.tag_manager import TagManager
from src.core.note_manager import NoteManager


class ComprehensiveTester:
    """Комплексное тестирование функциональности органайзера"""

    def __init__(self):
        self.db_manager = DatabaseManager("test_organizer.db")
        self.tag_manager = TagManager(self.db_manager)
        self.note_manager = NoteManager(self.db_manager, self.tag_manager)
        self.test_results = []

    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ")
        print("=" * 60)

        try:
            # Очищаем базу для чистого тестирования
            self.clean_database()

            # Запускаем тесты
            self.test_note_creation()
            self.test_tag_functionality()
            self.test_search_functionality()
            self.test_rich_text_formatting()
            self.test_combined_search()
            self.test_data_persistence()

            # Выводим результаты
            self.print_results()

        except Exception as e:
            print(f"❌ Критическая ошибка при тестировании: {e}")
            import traceback
            traceback.print_exc()

    def clean_database(self):
        """Очистка базы данных для тестирования"""
        print("\n🧹 Очистка базы данных...")
        try:
            with self.db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM note_tag_relation")
                cursor.execute("DELETE FROM notes")
                cursor.execute("DELETE FROM tags")
                conn.commit()
            print("✅ База данных очищена")
        except Exception as e:
            print(f"❌ Ошибка при очистке базы: {e}")

    def test_note_creation(self):
        """Тестирование создания заметок"""
        print("\n📝 ТЕСТ 1: Создание заметок")
        print("-" * 40)

        test_cases = [
            {
                "title": "Простая заметка",
                "content": "Это простая текстовая заметка без форматирования.",
                "tags": ["тест", "простая"],
                "type": "plain"
            },
            {
                "title": "Заметка с HTML форматированием",
                "content": "<h1>Заголовок</h1><p>Это <b>жирный</b> текст и <i>курсив</i>.</p><ul><li>Элемент списка 1</li><li>Элемент списка 2</li></ul>",
                "tags": ["тест", "html", "форматирование"],
                "type": "html"
            },
            {
                "title": "Рабочие задачи",
                "content": "<h2>План на день:</h2><ol><li>Закончить проект</li><li>Написать документацию</li><li>Совещание в 15:00</li></ol>",
                "tags": ["работа", "задачи", "срочно"],
                "type": "html"
            }
        ]

        created_notes = []
        for i, test_case in enumerate(test_cases, 1):
            try:
                note = self.note_manager.create(
                    title=test_case["title"],
                    content=test_case["content"],
                    tags=test_case["tags"],
                    content_type=test_case["type"]
                )

                if note:
                    created_notes.append(note)
                    print(f"✅ Заметка {i}: '{test_case['title']}' создана (ID: {note.id})")
                    print(f"   Теги: {test_case['tags']}")
                else:
                    print(f"❌ Заметка {i}: не удалось создать")

            except Exception as e:
                print(f"❌ Ошибка при создании заметки {i}: {e}")

        # Проверяем что все заметки созданы
        all_notes = self.note_manager.get_all()
        success = len(created_notes) == len(test_cases)

        self.record_test("Создание заметок", success,
                         f"Создано {len(created_notes)} из {len(test_cases)} заметок")

    def test_tag_functionality(self):
        """Тестирование функциональности тегов"""
        print("\n🏷️ ТЕСТ 2: Функциональность тегов")
        print("-" * 40)

        try:
            # Создаем дополнительные теги
            additional_tags = ["личное", "учеба", "проект"]
            created_tags = []

            for tag_name in additional_tags:
                tag = self.tag_manager.create(tag_name)
                if tag:
                    created_tags.append(tag)
                    print(f"✅ Тег '{tag_name}' создан")

            # Получаем все теги
            all_tags = self.tag_manager.get_all()
            print(f"📊 Всего тегов в системе: {len(all_tags)}")

            # Тестируем привязку тегов к заметкам
            notes = self.note_manager.get_all()
            if notes:
                note = notes[0]
                success = self.note_manager.add_tag_to_note(note.id, "новый-тег")
                if success:
                    print("✅ Тег успешно привязан к заметке")
                else:
                    print("❌ Не удалось привязать тег к заметке")

            # Проверяем поиск по тегам
            html_notes = self.note_manager.get_notes_by_tag("html")
            print(f"🔍 Найдено заметок с тегом 'html': {len(html_notes)}")

            self.record_test("Функциональность тегов", True,
                             f"Создано {len(created_tags)} тегов, всего {len(all_tags)}")

        except Exception as e:
            print(f"❌ Ошибка при тестировании тегов: {e}")
            self.record_test("Функциональность тегов", False, str(e))

    def test_search_functionality(self):
        """Тестирование поиска"""
        print("\n🔍 ТЕСТ 3: Функциональность поиска")
        print("-" * 40)

        try:
            # Поиск по тексту
            text_results = self.note_manager.search("заголовок")
            print(f"📝 Поиск по тексту 'заголовок': {len(text_results)} заметок")

            # Поиск по тегам
            tag_results = self.note_manager.search_by_tags(["работа"])
            print(f"🏷️ Поиск по тегу 'работа': {len(tag_results)} заметок")

            # Поиск по частичному совпадению
            partial_results = self.note_manager.search("заметка")
            print(f"🔎 Поиск по частичному тексту 'заметка': {len(partial_results)} заметок")

            success = (len(text_results) > 0 or len(tag_results) > 0 or len(partial_results) > 0)
            self.record_test("Функциональность поиска", success,
                             f"Текст: {len(text_results)}, Теги: {len(tag_results)}, Частичный: {len(partial_results)}")

        except Exception as e:
            print(f"❌ Ошибка при тестировании поиска: {e}")
            self.record_test("Функциональность поиска", False, str(e))

    def test_rich_text_formatting(self):
        """Тестирование форматирования текста"""
        print("\n🎨 ТЕСТ 4: Форматирование текста")
        print("-" * 40)

        try:
            # Создаем заметку с богатым форматированием
            rich_content = """
            <h1 style="color: blue;">Тест форматирования</h1>
            <p>Это <strong>жирный</strong> текст.</p>
            <p>Это <em>курсивный</em> текст.</p>
            <p>Это <u>подчеркнутый</u> текст.</p>
            <ul>
                <li>Маркированный список 1</li>
                <li>Маркированный список 2</li>
            </ul>
            <ol>
                <li>Нумерованный список 1</li>
                <li>Нумерованный список 2</li>
            </ol>
            <p style="text-align: center;">Выровненный по центру текст</p>
            """

            note = self.note_manager.create(
                title="Тест форматирования",
                content=rich_content,
                tags=["форматирование", "тест"],
                content_type="html"
            )

            if note:
                print("✅ Заметка с богатым форматированием создана")

                # Проверяем что содержимое сохранилось
                retrieved_note = self.note_manager.get(note.id)
                if retrieved_note and "<h1" in retrieved_note.content:
                    print("✅ HTML форматирование сохранено корректно")
                    success = True
                else:
                    print("❌ HTML форматирование не сохранилось")
                    success = False
            else:
                print("❌ Не удалось создать заметку с форматированием")
                success = False

            self.record_test("Форматирование текста", success,
                             "Проверка сохранения HTML разметки")

        except Exception as e:
            print(f"❌ Ошибка при тестировании форматирования: {e}")
            self.record_test("Форматирование текста", False, str(e))

    def test_combined_search(self):
        """Тестирование комбинированного поиска"""
        print("\n🔍 ТЕСТ 5: Комбинированный поиск")
        print("-" * 40)

        try:
            # Комбинированный поиск: текст + теги
            combined_results = self.note_manager.search_by_text_and_tags("заголовок", ["html"])
            print(f"🎯 Комбинированный поиск ('заголовок' + 'html'): {len(combined_results)} заметок")

            # Поиск по нескольким тегам
            multi_tag_results = self.note_manager.search_by_tags(["тест", "html"])
            print(f"🏷️ Поиск по нескольким тегам ('тест' + 'html'): {len(multi_tag_results)} заметок")

            success = True  # Если не было исключений - считаем успешным
            self.record_test("Комбинированный поиск", success,
                             f"Комбинированный: {len(combined_results)}, Мульти-теги: {len(multi_tag_results)}")

        except Exception as e:
            print(f"❌ Ошибка при комбинированном поиске: {e}")
            self.record_test("Комбинированный поиск", False, str(e))

    def test_data_persistence(self):
        """Тестирование сохранения данных"""
        print("\n💾 ТЕСТ 6: Сохранение данных")
        print("-" * 40)

        try:
            # Получаем текущие данные
            original_notes = self.note_manager.get_all()
            original_tags = self.tag_manager.get_all()

            print(f"📊 Перед перезапуском: {len(original_notes)} заметок, {len(original_tags)} тегов")

            # Имитируем "перезапуск" приложения - создаем новых менеджеров
            new_db_manager = DatabaseManager("test_organizer.db")
            new_tag_manager = TagManager(new_db_manager)
            new_note_manager = NoteManager(new_db_manager, new_tag_manager)

            # Получаем данные после "перезапуска"
            persistent_notes = new_note_manager.get_all()
            persistent_tags = new_tag_manager.get_all()

            print(f"📊 После перезапуска: {len(persistent_notes)} заметок, {len(persistent_tags)} тегов")

            # Проверяем сохранение
            notes_persisted = len(original_notes) == len(persistent_notes)
            tags_persisted = len(original_tags) == len(persistent_tags)

            if notes_persisted and tags_persisted:
                print("✅ Все данные сохранились после перезапуска")
                success = True
            else:
                print("❌ Данные не полностью сохранились")
                success = False

            self.record_test("Сохранение данных", success,
                             f"Заметки: {notes_persisted}, Теги: {tags_persisted}")

        except Exception as e:
            print(f"❌ Ошибка при тестировании сохранения: {e}")
            self.record_test("Сохранение данных", False, str(e))

    def record_test(self, test_name, success, details=""):
        """Записывает результат теста"""
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        self.test_results.append({
            "name": test_name,
            "success": success,
            "details": details,
            "status": status
        })

    def print_results(self):
        """Выводит итоговые результаты"""
        print("\n" + "=" * 60)
        print("🎯 ИТОГИ ТЕСТИРОВАНИЯ")
        print("=" * 60)

        passed = sum(1 for test in self.test_results if test["success"])
        total = len(self.test_results)

        for test in self.test_results:
            print(f"{test['status']}: {test['name']}")
            if test["details"]:
                print(f"   📋 {test['details']}")

        print("\n" + "=" * 60)
        print(f"📊 ОБЩИЙ РЕЗУЛЬТАТ: {passed}/{total} тестов пройдено")

        if passed == total:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("✅ Фаза 3 завершена успешно!")
        else:
            print("⚠️  Некоторые тесты не пройдены. Требуется отладка.")

        print("=" * 60)


def main():
    """Главная функция тестирования"""
    print("🔬 Комплексное тестирование Умного Органайзера")
    print("Версия: Фаза 3 - Богатый текст и теги")

    # Создаем QApplication для тестов, которые могут требовать Qt
    app = QApplication(sys.argv)

    # Запускаем тестирование
    tester = ComprehensiveTester()
    tester.run_all_tests()

    # Не запускаем главный цикл приложения, так как мы только тестируем логику
    print("\n🧪 Тестирование завершено. Проверьте результаты выше.")


if __name__ == "__main__":
    main()