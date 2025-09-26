# debug_console.py
import sys
import os
from datetime import datetime

# Добавляем путь для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.database_manager import DatabaseManager
from core.tag_manager import TagManager
from core.note_manager import NoteManager
from core.models import Note, Tag


class DebugConsole:
    """Консольный интерфейс для тестирования функциональности органайзера"""

    def __init__(self, db_path="smart_organizer_debug.db"):
        """Инициализация консоли с менеджерами"""
        self.db = DatabaseManager(db_path)
        self.tag_manager = TagManager(self.db)
        self.note_manager = NoteManager(self.db, self.tag_manager)
        self.is_running = True

    def display_menu(self):
        """Отображает главное меню"""
        print("\n" + "=" * 50)
        print("          УМНЫЙ ОРГАНАЙЗЕР - DEBUG CONSOLE")
        print("=" * 50)
        print("1. Создать заметку")
        print("2. Показать все заметки")
        print("3. Найти заметки")
        print("4. Показать заметку по ID")
        print("5. Обновить заметку")
        print("6. Удалить заметку")
        print("7. Управление тегами")
        print("8. Статистика")
        print("9. Выход")
        print("-" * 50)

    def clear_screen(self):
        """Очищает экран консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def wait_for_enter(self):
        """Ждет нажатия Enter для продолжения"""
        input("\nНажмите Enter для продолжения...")

    def safe_input(self, prompt):
        """Безопасный ввод с обработкой EOFError"""
        try:
            return input(prompt).strip()
        except EOFError:
            return ""
        except KeyboardInterrupt:
            raise KeyboardInterrupt

    def safe_multiline_input(self, prompt):
        """Безопасный ввод многострочного текста"""
        print(prompt)
        content_lines = []

        try:
            line_number = 1
            while True:
                try:
                    line = input(f"{line_number:2d}| ").strip()
                    line_number += 1
                    if line == "" and not content_lines:
                        # Пропускаем первую пустую строку
                        continue
                    if line.lower() == ':q':
                        print("Ввод завершен.")
                        break
                    content_lines.append(line)
                except EOFError:
                    print("\nВвод завершен (Ctrl+D).")
                    break
                except KeyboardInterrupt:
                    print("\nВвод прерван пользователем.")
                    return None
        except KeyboardInterrupt:
            print("\nВвод прерван пользователем.")
            return None

        return "\n".join(content_lines) if content_lines else ""

    def print_note_details(self, note: Note, show_content=True):
        """Выводит детальную информацию о заметке"""
        print(f"\n📝 ЗАМЕТКА #{note.id}")
        print(f"   Заголовок: {note.title}")
        if show_content:
            # Показываем содержимое с отступами
            content_lines = note.content.split('\n')
            if len(content_lines) == 1:
                print(f"   Содержимое: {note.content}")
            else:
                print("   Содержимое:")
                for line in content_lines:
                    print(f"     {line}")
        print(f"   Дата создания: {note.created_date.strftime('%d.%m.%Y %H:%M')}")
        print(f"   Дата изменения: {note.modified_date.strftime('%d.%m.%Y %H:%M')}")
        if note.tags:
            tags_str = ", ".join([tag.name for tag in note.tags])
            print(f"   Теги: {tags_str}")
        else:
            print("   Теги: нет")

    def create_note(self):
        """Создание новой заметки"""
        print("\n🗒️  СОЗДАНИЕ НОВОЙ ЗАМЕТКИ")
        print("-" * 30)

        try:
            title = self.safe_input("Введите заголовок: ")
            if not title:
                print("❌ Заголовок не может быть пустым!")
                return

            content = self.safe_multiline_input(
                "Введите содержимое (пустая строка + Enter для завершения, :q для выхода):"
            )
            if content is None:  # Пользователь прервал ввод
                return

            tags_input = self.safe_input("Введите теги (через запятую, пусто - без тегов): ")
            tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
            tags = [tag for tag in tags if tag]  # Убираем пустые

            note = self.note_manager.create(title, content, tags)
            if note:
                print(f"✅ Заметка создана успешно! ID: {note.id}")
                self.print_note_details(note)
            else:
                print("❌ Ошибка при создании заметки!")

        except KeyboardInterrupt:
            print("\n❌ Создание заметки отменено пользователем")

    def show_all_notes(self):
        """Показывает все заметки"""
        print("\n📚 ВСЕ ЗАМЕТКИ")
        print("-" * 30)

        notes = self.note_manager.get_all()
        if not notes:
            print("📭 Заметок пока нет")
            return

        # print(f"Найдено заметок: {len(notes)}\n")

        for i, note in enumerate(notes, 1):
            print(f"{i}. [{note.id}] {note.title}")
            tags_str = ", ".join([tag.name for tag in note.tags]) if note.tags else "нет тегов"
            print(f"   Теги: {tags_str}")
            print(f"   Обновлена: {note.modified_date.strftime('%d.%m.%Y %H:%M')}")
            print()

    def search_notes(self):
        """Поиск заметок"""
        print("\n🔍 ПОИСК ЗАМЕТОК")
        print("-" * 30)

        try:
            search_text = self.safe_input("Текст для поиска (пусто - пропустить): ")

            tags_input = self.safe_input("Теги для поиска (через запятую, пусто - пропустить): ")
            tag_names = [tag.strip() for tag in tags_input.split(",")] if tags_input else None
            if tag_names:
                tag_names = [tag for tag in tag_names if tag]  # Убираем пустые

            if not search_text and not tag_names:
                print("⚠️  Укажите текст для поиска или теги!")
                return

            notes = self.note_manager.search(search_text, tag_names)

            if not notes:
                print("📭 Заметки не найдены")
                return

            print(f"\n🎯 Найдено заметок: {len(notes)}\n")

            for i, note in enumerate(notes, 1):
                print(f"{i}. [{note.id}] {note.title}")
                if search_text and search_text.lower() in note.content.lower():
                    # Показываем preview содержимого с подсветкой
                    preview = note.content[:100] + "..." if len(note.content) > 100 else note.content
                    print(f"   Содержимое: {preview}")

                tags_str = ", ".join([tag.name for tag in note.tags]) if note.tags else "нет тегов"
                print(f"   Теги: {tags_str}")
                print()

        except KeyboardInterrupt:
            print("\n❌ Поиск отменен пользователем")

    def show_note_by_id(self):
        """Показывает заметку по ID"""
        print("\n🔎 ПОИСК ЗАМЕТКИ ПО ID")
        print("-" * 30)

        try:
            note_id_input = self.safe_input("Введите ID заметки: ")
            if not note_id_input:
                print("❌ ID не может быть пустым!")
                return

            note_id = int(note_id_input)
        except ValueError:
            print("❌ Неверный формат ID!")
            return
        except KeyboardInterrupt:
            print("\n❌ Ввод отменен пользователем")
            return

        note = self.note_manager.get(note_id)
        if note:
            self.print_note_details(note, show_content=True)
        else:
            print(f"❌ Заметка с ID {note_id} не найдена!")

    def update_note(self):
        """Обновление существующей заметки"""
        print("\n✏️  ОБНОВЛЕНИЕ ЗАМЕТКИ")
        print("-" * 30)

        try:
            note_id_input = self.safe_input("Введите ID заметки для обновления: ")
            if not note_id_input:
                print("❌ ID не может быть пустым!")
                return

            note_id = int(note_id_input)
        except ValueError:
            print("❌ Неверный формат ID!")
            return
        except KeyboardInterrupt:
            print("\n❌ Ввод отменен пользователем")
            return

        note = self.note_manager.get(note_id)
        if not note:
            print(f"❌ Заметка с ID {note_id} не найдена!")
            return

        print("\nТекущие данные заметки:")
        self.print_note_details(note)

        print("\nВведите новые данные (оставьте пустым чтобы не изменять):")

        try:
            new_title = self.safe_input(f"Новый заголовок [{note.title}]: ")
            if not new_title:
                new_title = None

            print("Новое содержимое (пустая строка + Enter для завершения, :q для выхода):")
            new_content = self.safe_multiline_input("")
            if new_content is None:  # Пользователь прервал ввод
                return
            if new_content == "":
                new_content = None

            current_tags = ", ".join([tag.name for tag in note.tags]) if note.tags else ""
            new_tags_input = self.safe_input(f"Новые теги (через запятую) [{current_tags}]: ")
            new_tags = [tag.strip() for tag in new_tags_input.split(",")] if new_tags_input else None
            if new_tags:
                new_tags = [tag for tag in new_tags if tag]  # Убираем пустые

            success = self.note_manager.update(note_id, new_title, new_content, new_tags)
            if success:
                print("✅ Заметка успешно обновлена!")
                updated_note = self.note_manager.get(note_id)
                self.print_note_details(updated_note)
            else:
                print("❌ Ошибка при обновлении заметки!")

        except KeyboardInterrupt:
            print("\n❌ Обновление отменено пользователем")

    def delete_note(self):
        """Удаление заметки"""
        print("\n🗑️  УДАЛЕНИЕ ЗАМЕТКИ")
        print("-" * 30)

        try:
            note_id_input = self.safe_input("Введите ID заметки для удаления: ")
            if not note_id_input:
                print("❌ ID не может быть пустым!")
                return

            note_id = int(note_id_input)
        except ValueError:
            print("❌ Неверный формат ID!")
            return
        except KeyboardInterrupt:
            print("\n❌ Ввод отменен пользователем")
            return

        note = self.note_manager.get(note_id)
        if not note:
            print(f"❌ Заметка с ID {note_id} не найдена!")
            return

        print("Вы уверены, что хотите удалить заметку?")
        self.print_note_details(note)

        try:
            confirm = self.safe_input("Введите 'ДА' для подтверждения удаления: ")
            if confirm.upper() == 'ДА':
                success = self.note_manager.delete(note_id)
                if success:
                    print("✅ Заметка успешно удалена!")
                else:
                    print("❌ Ошибка при удалении заметки!")
            else:
                print("❌ Удаление отменено")
        except KeyboardInterrupt:
            print("\n❌ Удаление отменено пользователем")

    def manage_tags(self):
        """Меню управления тегами"""
        while True:
            print("\n🏷️  УПРАВЛЕНИЕ ТЕГАМИ")
            print("-" * 30)
            print("1. Показать все теги")
            print("2. Создать тег")
            print("3. Удалить тег")
            print("4. Назад в главное меню")

            try:
                choice = self.safe_input("Выберите действие: ")

                if choice == "1":
                    self.show_all_tags()
                elif choice == "2":
                    self.create_tag()
                elif choice == "3":
                    self.delete_tag()
                elif choice == "4":
                    break
                else:
                    print("❌ Неверный выбор!")
            except KeyboardInterrupt:
                print("\n❌ Возврат в главное меню")
                break

    def show_all_tags(self):
        """Показывает все теги"""
        print("\n🏷️  ВСЕ ТЕГИ")
        print("-" * 30)

        tags = self.tag_manager.get_all()
        if not tags:
            print("📭 Тегов пока нет")
            return

        print(f"Всего тегов: {len(tags)}\n")

        for i, tag in enumerate(tags, 1):
            # Получаем количество заметок для каждого тега
            notes_with_tag = self.note_manager.get_notes_by_tag(tag.name)
            print(f"{i}. [{tag.id}] {tag.name} ({len(notes_with_tag)} заметок)")

    def create_tag(self):
        """Создание нового тега"""
        print("\n🏷️  СОЗДАНИЕ ТЕГА")
        print("-" * 30)

        try:
            name = self.safe_input("Введите название тега: ")
            if not name:
                print("❌ Название тега не может быть пустым!")
                return

            tag = self.tag_manager.create(name)
            if tag:
                print(f"✅ Тег '{tag.name}' создан успешно! ID: {tag.id}")
            else:
                print("❌ Ошибка при создании тега!")
        except KeyboardInterrupt:
            print("\n❌ Создание тега отменено")

    def delete_tag(self):
        """Удаление тега"""
        print("\n🏷️  УДАЛЕНИЕ ТЕГА")
        print("-" * 30)

        try:
            tag_id_input = self.safe_input("Введите ID тега для удаления: ")
            if not tag_id_input:
                print("❌ ID не может быть пустым!")
                return

            tag_id = int(tag_id_input)
        except ValueError:
            print("❌ Неверный формат ID!")
            return
        except KeyboardInterrupt:
            print("\n❌ Ввод отменен пользователем")
            return

        tag = self.tag_manager.get(tag_id)
        if not tag:
            print(f"❌ Тег с ID {tag_id} не найден!")
            return

        # Показываем заметки с этим тегом
        notes_with_tag = self.note_manager.get_notes_by_tag(tag.name)

        print(f"Тег: {tag.name}")
        print(f"Используется в {len(notes_with_tag)} заметках")

        if notes_with_tag:
            print("Заметки с этим тегом:")
            for note in notes_with_tag[:5]:  # Показываем первые 5
                print(f"  - {note.title}")
            if len(notes_with_tag) > 5:
                print(f"  ... и еще {len(notes_with_tag) - 5} заметок")

        try:
            confirm = self.safe_input("Введите 'ДА' для подтверждения удаления: ")
            if confirm.upper() == 'ДА':
                success = self.tag_manager.delete(tag_id)
                if success:
                    print("✅ Тег успешно удален!")
                else:
                    print("❌ Ошибка при удалении тега!")
            else:
                print("❌ Удаление отменено")
        except KeyboardInterrupt:
            print("\n❌ Удаление отменено пользователем")

    def show_statistics(self):
        """Показывает статистику"""
        print("\n📊 СТАТИСТИКА")
        print("-" * 30)

        notes = self.note_manager.get_all()
        tags = self.tag_manager.get_all()

        print(f"📝 Всего заметок: {len(notes)}")
        print(f"🏷️  Всего тегов: {len(tags)}")

        if notes:
            # Самая старая и новая заметка
            oldest_note = min(notes, key=lambda x: x.created_date)
            newest_note = max(notes, key=lambda x: x.modified_date)

            print(f"📅 Самая старая заметка: {oldest_note.created_date.strftime('%d.%m.%Y')}")
            print(f"🆕 Самая новая заметка: {newest_note.modified_date.strftime('%d.%m.%Y')}")

            # Распределение по тегам
            tagged_notes = [note for note in notes if note.tags]
            print(f"🏷️  Заметок с тегами: {len(tagged_notes)} ({len(tagged_notes) / len(notes) * 100:.1f}%)")

        if tags:
            # Самые популярные теги
            tag_stats = []
            for tag in tags:
                notes_count = len(self.note_manager.get_notes_by_tag(tag.name))
                tag_stats.append((tag.name, notes_count))

            tag_stats.sort(key=lambda x: x[1], reverse=True)
            print("\n🔥 Самые популярные теги:")
            for tag_name, count in tag_stats[:5]:
                print(f"  {tag_name}: {count} заметок")

    def run(self):
        """Запускает главный цикл приложения"""
        print("🚀 Запуск Debug Console...")
        print("База данных инициализирована!")

        while self.is_running:
            self.clear_screen()
            self.display_menu()

            try:
                choice = self.safe_input("Выберите действие (1-9): ")

                if choice == "1":
                    self.create_note()
                elif choice == "2":
                    self.show_all_notes()
                elif choice == "3":
                    self.search_notes()
                elif choice == "4":
                    self.show_note_by_id()
                elif choice == "5":
                    self.update_note()
                elif choice == "6":
                    self.delete_note()
                elif choice == "7":
                    self.manage_tags()
                elif choice == "8":
                    self.show_statistics()
                elif choice == "9":
                    print("👋 До свидания!")
                    self.is_running = False
                    break
                else:
                    print("❌ Неверный выбор! Попробуйте снова.")
                    self.wait_for_enter()
                    continue

                self.wait_for_enter()

            except KeyboardInterrupt:
                print("\n\n❌ Операция прервана пользователем")
                self.wait_for_enter()
            except Exception as e:
                print(f"\n❌ Произошла ошибка: {e}")
                self.wait_for_enter()

        # Закрываем соединения при выходе
        self.db.close()


def main():
    """Главная функция"""
    try:
        console = DebugConsole()
        console.run()
    except KeyboardInterrupt:
        print("\n\n👋 Приложение завершено по запросу пользователя!")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()