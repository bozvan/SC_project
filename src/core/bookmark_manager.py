from datetime import datetime

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional, Dict, List
import time
from .models import WebBookmark, Tag, Note
from .database_manager import DatabaseManager


class BookmarkManager:
    """Менеджер для работы с веб-закладками"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def create(self, url: str, title: str = "", description: str = "",
               tags: Optional[List[str]] = None, favicon_url: Optional[str] = None) -> Optional[WebBookmark]:
        """
        Создает новую веб-закладку
        """
        if not url or not url.strip():
            print("❌ Ошибка: URL не может быть пустым")
            return None

        # Нормализуем URL
        normalized_url = self.normalize_url(url)

        # Валидируем URL
        if not self.validate_url(normalized_url):
            print(f"❌ Ошибка: некорректный URL '{url}'")
            return None

        # Если заголовок не указан, используем домен
        if not title.strip():
            title = self._extract_domain(normalized_url)

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Вставляем закладку
                cursor.execute(
                    """INSERT INTO bookmarks (url, title, description, favicon_url) 
                    VALUES (?, ?, ?, ?)""",
                    (normalized_url, title.strip(), description.strip(), favicon_url)
                )
                bookmark_id = cursor.lastrowid

                if not bookmark_id:
                    print("❌ Ошибка: не удалось получить ID созданной закладки")
                    return None

                # Обрабатываем теги
                tag_objects = []
                if tags:
                    for tag_name in tags:
                        tag = self._get_or_create_tag_with_connection(cursor, tag_name)
                        if tag:
                            cursor.execute(
                                "INSERT INTO bookmark_tag_relation (bookmark_id, tag_id) VALUES (?, ?)",
                                (bookmark_id, tag.id)
                            )
                            tag_objects.append(tag)

                conn.commit()

                # Создаем объект WebBookmark
                bookmark = WebBookmark(
                    url=normalized_url,
                    title=title,
                    description=description,
                    bookmark_id=bookmark_id,
                    favicon_url=favicon_url
                )
                bookmark.tags = tag_objects

                print(f"✅ Закладка создана: {bookmark}")
                if tag_objects:
                    print(f"   🏷️ Привязаны теги: {[tag.name for tag in tag_objects]}")

                return bookmark

        except Exception as e:
            print(f"❌ Ошибка при создании закладки: {e}")
            return None

    def update(self, bookmark_id: int, title: Optional[str] = None,
               description: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """
        Обновляет данные закладки
        """
        # Проверяем существование закладки
        existing_bookmark = self.get(bookmark_id)
        if not existing_bookmark:
            print(f"❌ Закладка с ID {bookmark_id} не существует")
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                update_fields = []
                update_values = []

                if title is not None and title.strip():
                    update_fields.append("title = ?")
                    update_values.append(title.strip())

                if description is not None:
                    update_fields.append("description = ?")
                    update_values.append(description.strip() if description else None)

                # Если нет изменений, выходим раньше
                if not update_fields and tags is None:
                    print("⚠️  Нет изменений для сохранения")
                    return True

                # Всегда обновляем updated_at
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(bookmark_id)

                if update_fields:
                    update_query = f"UPDATE bookmarks SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(update_query, update_values)

                # Обновляем теги если они переданы
                if tags is not None:
                    # Удаляем старые связи
                    cursor.execute("DELETE FROM bookmark_tag_relation WHERE bookmark_id = ?", (bookmark_id,))

                    # Добавляем новые связи
                    for tag_name in tags:
                        tag = self._get_or_create_tag_with_connection(cursor, tag_name)
                        if tag and tag.id:
                            cursor.execute(
                                "INSERT INTO bookmark_tag_relation (bookmark_id, tag_id) VALUES (?, ?)",
                                (bookmark_id, tag.id)
                            )

                conn.commit()
                print(f"✅ Закладка с ID {bookmark_id} обновлена")
                return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении закладки с ID {bookmark_id}: {e}")
            return False

    def _get_or_create_tag_with_connection(self, cursor, tag_name: str) -> Optional[Tag]:
        """Вспомогательный метод для работы с тегами"""
        if not tag_name or not tag_name.strip():
            return None

        normalized_name = tag_name.strip().lower()

        try:
            # Сначала ищем существующий тег
            cursor.execute("SELECT id, name FROM tags WHERE name = ?", (normalized_name,))
            result = cursor.fetchone()

            if result:
                tag_id, name = result
                return Tag(name=name, tag_id=tag_id)
            else:
                # Создаем новый тег
                cursor.execute("INSERT INTO tags (name) VALUES (?)", (normalized_name,))
                tag_id = cursor.lastrowid
                if tag_id:
                    return Tag(name=normalized_name, tag_id=tag_id)
                else:
                    return None

        except Exception as e:
            print(f"❌ Ошибка при работе с тегом '{tag_name}': {e}")
            return None

    def delete(self, bookmark_id: int) -> bool:
        """Удаляет закладку"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Закладка с ID {bookmark_id} удалена")
                    return True
                else:
                    print(f"❌ Закладка с ID {bookmark_id} не найдена")
                    return False

        except Exception as e:
            print(f"❌ Ошибка при удалении закладки с ID {bookmark_id}: {e}")
            return False

    def parse_url_metadata(self, url: str) -> Dict[str, Optional[str]]:
        """
        Извлекает метаданные из веб-страницы

        Args:
            url: URL для парсинга

        Returns:
            Dict с title, description и другими метаданными
        """
        try:
            print(f"🔍 Получение метаданных для: {url}")

            # Делаем запрос с таймаутом
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Проверяем статус ответа

            # Парсим HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Извлекаем заголовок
            title = self._extract_title(soup)

            # Извлекаем описание
            description = self._extract_description(soup)

            # Извлекаем другие полезные метаданные
            metadata = {
                'title': title,
                'description': description,
                'url': url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content)
            }

            print(f"✅ Метаданные получены: '{title}'")
            return metadata

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при получении страницы: {e}")
            return self._get_fallback_metadata(url, str(e))
        except Exception as e:
            print(f"❌ Неожиданная ошибка при парсинге: {e}")
            return self._get_fallback_metadata(url, str(e))

    def get(self, bookmark_id: int) -> Optional[WebBookmark]:
        """Возвращает закладку по ID"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """SELECT id, url, title, description, favicon_url, created_at, updated_at 
                    FROM bookmarks WHERE id = ?""",
                    (bookmark_id,)
                )
                result = cursor.fetchone()

                if not result:
                    print(f"❌ Закладка с ID {bookmark_id} не найдена")
                    return None

                (bookmark_id, url, title, description, favicon_url, created_at, updated_at) = result

                # Получаем теги для этой закладки
                tag_objects = self.get_tags_for_bookmark(bookmark_id)

                # Преобразуем даты
                created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                updated_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                bookmark = WebBookmark(
                    url=url,
                    title=title,
                    description=description,
                    bookmark_id=bookmark_id,
                    favicon_url=favicon_url,
                    created_date=created_date,
                    updated_date=updated_date
                )
                bookmark.tags = tag_objects

                return bookmark

        except Exception as e:
            print(f"❌ Ошибка при получении закладки с ID {bookmark_id}: {e}")
            return None

    def get_tags_for_bookmark(self, bookmark_id: int) -> List[Tag]:
        """Возвращает теги для закладки"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.id, t.name 
                    FROM tags t 
                    JOIN bookmark_tag_relation btr ON t.id = btr.tag_id 
                    WHERE btr.bookmark_id = ?
                """, (bookmark_id,))
                results = cursor.fetchall()

                tags = []
                for tag_id, name in results:
                    tags.append(Tag(name=name, tag_id=tag_id))

                return tags

        except Exception as e:
            print(f"❌ Ошибка при получении тегов для закладки {bookmark_id}: {e}")
            return []

    def get_all(self) -> List[WebBookmark]:
        """Возвращает все закладки"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """SELECT id, url, title, description, favicon_url, created_at, updated_at 
                    FROM bookmarks ORDER BY created_at DESC"""
                )
                results = cursor.fetchall()

                bookmarks = []
                for (bookmark_id, url, title, description, favicon_url, created_at, updated_at) in results:
                    # Получаем теги для каждой закладки
                    tag_objects = self.get_tags_for_bookmark(bookmark_id)

                    # Преобразуем даты
                    created_date = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    updated_date = datetime.fromisoformat(updated_at) if updated_at else datetime.now()

                    bookmark = WebBookmark(
                        url=url,
                        title=title,
                        description=description,
                        bookmark_id=bookmark_id,
                        favicon_url=favicon_url,
                        created_date=created_date,
                        updated_date=updated_date
                    )
                    bookmark.tags = tag_objects
                    bookmarks.append(bookmark)

                print(f"✅ Загружено закладок: {len(bookmarks)}")
                return bookmarks

        except Exception as e:
            print(f"❌ Ошибка при получении закладок: {e}")
            return []

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Извлекает заголовок страницы"""
        # Пробуем получить title
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        # Пробуем получить og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        # Пробуем получить h1
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.string:
            return h1_tag.string.strip()

        return "Без заголовка"

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлекает описание страницы"""
        # Пробуем получить meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()

        # Пробуем получить og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()

        # Пробуем получить первый параграф
        first_p = soup.find('p')
        if first_p and first_p.string:
            # Обрезаем длинное описание
            desc = first_p.string.strip()
            return desc[:200] + '...' if len(desc) > 200 else desc

        return None

    def _get_fallback_metadata(self, url: str, error: str) -> Dict[str, Optional[str]]:
        """Возвращает метаданные по умолчанию при ошибке"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        return {
            'title': f"{domain} (недоступен)",
            'description': f"Не удалось загрузить страницу: {error}",
            'url': url,
            'status_code': 0,
            'content_type': '',
            'content_length': 0
        }

    def add_bookmark(self, url: str, tags: Optional[list] = None) -> Optional[Note]:
        """
        Добавляет новую веб-закладку с автоматическим получением метаданных

        Args:
            url: URL веб-страницы
            tags: Список тегов для закладки

        Returns:
            Созданный объект Note или None при ошибке
        """
        try:
            print(f"📥 Добавление закладки: {url}")

            # Получаем метаданные
            metadata = self.parse_url_metadata(url)

            # Создаем закладку через NoteManager
            bookmark = self.note_manager.create_bookmark(
                url=metadata['url'],
                title=metadata['title'],
                description=metadata['description'],
                tags=tags
            )

            if bookmark:
                print(f"✅ Закладка создана: {bookmark.title}")
                # Добавляем дополнительные метаданные в описание
                if metadata.get('status_code'):
                    additional_info = f"\n\n---\nСтатус: {metadata['status_code']} | Размер: {metadata.get('content_length', 0)} байт"
                    if metadata.get('description'):
                        bookmark.page_description += additional_info
                    else:
                        bookmark.page_description = additional_info.strip()

                return bookmark
            else:
                print("❌ Не удалось создать закладку")
                return None

        except Exception as e:
            print(f"❌ Ошибка при добавлении закладки: {e}")
            return None

    def validate_url(self, url: str) -> bool:
        """Проверяет валидность URL"""
        if not url or not url.strip():
            return False

        url = url.strip()

        try:
            result = urlparse(url)

            # Если нет схемы, добавляем временно для проверки
            if not result.scheme:
                test_url = f"https://{url}"
                result = urlparse(test_url)

            # Проверяем наличие домена
            if not result.netloc:
                return False

            # Домен должен содержать точку (кроме localhost)
            if '.' not in result.netloc and result.netloc != 'localhost':
                return False

            return True

        except Exception:
            return False

    def normalize_url(self, url: str) -> str:
        """Нормализует URL"""
        if not url:
            return url

        url = url.strip()

        # Если URL уже имеет схему, возвращаем как есть
        if url.startswith(('http://', 'https://')):
            return url

        # Если начинается с www., добавляем https://
        if url.startswith('www.'):
            return f'https://{url}'

        # Для остальных случаев добавляем https://
        return f'https://{url}'

    def _extract_domain(self, url: str) -> str:
        """Извлекает домен из URL"""
        try:
            return urlparse(url).netloc
        except:
            return url

    def add_bookmark_with_metadata(self, url: str, tags: Optional[list] = None) -> Optional[WebBookmark]:
        """
        Добавляет закладку с автоматическим получением метаданных
        """
        try:
            print(f"📥 Добавление закладки: {url}")

            # Получаем метаданные
            metadata = self.parse_url_metadata(url)

            # Создаем закладку
            bookmark = self.create(
                url=metadata['url'],
                title=metadata['title'],
                description=metadata['description'],
                tags=tags
            )

            if bookmark:
                print(f"✅ Закладка создана: {bookmark.title}")
                return bookmark
            else:
                print("❌ Не удалось создать закладку")
                return None

        except Exception as e:
            print(f"❌ Ошибка при добавлении закладки: {e}")
            return None

    def bulk_add_bookmarks(self, urls: list, common_tags: Optional[list] = None) -> list:
        """
        Добавляет несколько закладок за раз

        Args:
            urls: Список URL
            common_tags: Общие теги для всех закладок

        Returns:
            Список созданных закладок
        """
        created_bookmarks = []

        for i, url in enumerate(urls):
            print(f"📥 Обработка {i + 1}/{len(urls)}: {url}")

            bookmark = self.add_bookmark(url, common_tags)
            if bookmark:
                created_bookmarks.append(bookmark)

            # Небольшая задержка чтобы не перегружать сервер
            time.sleep(1)

        print(f"✅ Создано закладок: {len(created_bookmarks)} из {len(urls)}")
        return created_bookmarks

    # В класс BookmarkManager добавим методы поиска:

    def search(self, search_text: str = "") -> List[WebBookmark]:
        """Ищет закладки по тексту"""
        all_bookmarks = self.get_all()

        if not search_text.strip():
            return all_bookmarks

        search_text_lower = search_text.lower()
        filtered_bookmarks = []

        for bookmark in all_bookmarks:
            if (search_text_lower in bookmark.title.lower() or
                    search_text_lower in bookmark.url.lower() or
                    (bookmark.description and search_text_lower in bookmark.description.lower())):
                filtered_bookmarks.append(bookmark)

        return filtered_bookmarks

    def search_by_tags(self, tag_names: List[str]) -> List[WebBookmark]:
        """Ищет закладки по тегам"""
        all_bookmarks = self.get_all()

        if not tag_names:
            return all_bookmarks

        filtered_bookmarks = []

        for bookmark in all_bookmarks:
            bookmark_tag_names = [tag.name.lower() for tag in bookmark.tags]
            # Проверяем, что ВСЕ указанные теги присутствуют
            if all(tag_name.lower() in bookmark_tag_names for tag_name in tag_names):
                filtered_bookmarks.append(bookmark)

        return filtered_bookmarks

    def search_by_text_and_tags(self, search_text: str, tag_names: List[str]) -> List[WebBookmark]:
        """Ищет закладки по тексту И тегам"""
        # Сначала фильтруем по тегам
        tagged_bookmarks = self.search_by_tags(tag_names)

        if not search_text.strip():
            return tagged_bookmarks

        # Затем фильтруем по тексту
        search_text_lower = search_text.lower()
        filtered_bookmarks = []

        for bookmark in tagged_bookmarks:
            if (search_text_lower in bookmark.title.lower() or
                    search_text_lower in bookmark.url.lower() or
                    (bookmark.description and search_text_lower in bookmark.description.lower())):
                filtered_bookmarks.append(bookmark)

        return filtered_bookmarks