from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional, Dict, List
import time
from .models import WebBookmark, Tag
from .database_manager import DatabaseManager


class BookmarkManager:
    """Менеджер для работы с веб-закладками через отдельную таблицу bookmarks"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self._migrate_bookmarks_table()
        print("✅ Менеджер закладок инициализирован")

    def _migrate_bookmarks_table(self):
        """Миграция таблицы bookmarks для добавления workspace_id"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем существование колонки workspace_id
                cursor.execute("PRAGMA table_info(bookmarks)")
                columns = [column[1] for column in cursor.fetchall()]

                if 'workspace_id' not in columns:
                    print("🔧 Добавляем колонку workspace_id в таблицу bookmarks")
                    cursor.execute("""
                        ALTER TABLE bookmarks 
                        ADD COLUMN workspace_id INTEGER DEFAULT 1
                        REFERENCES workspaces(id) ON DELETE SET DEFAULT
                    """)
                    conn.commit()
                    print("✅ Миграция таблицы bookmarks завершена")

        except Exception as e:
            print(f"❌ Ошибка при миграции таблицы bookmarks: {e}")

    def create(self, url: str, title: str = "", description: str = "",
               tags: Optional[List[str]] = None, favicon_url: Optional[str] = None,
               workspace_id: int = 1) -> Optional[WebBookmark]:
        """
        Создает новую веб-закладку

        Args:
            url: URL веб-страницы
            title: Заголовок закладки
            description: Описание закладки
            tags: Список тегов
            favicon_url: URL иконки (строка или None)
            workspace_id: ID рабочего пространства

        Returns:
            WebBookmark: Созданная закладка или None при ошибке
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

        # ВАЖНО: Проверяем и нормализуем favicon_url
        normalized_favicon_url = None
        if favicon_url is not None:
            if isinstance(favicon_url, str) and favicon_url.strip():
                normalized_favicon_url = favicon_url.strip()
            else:
                print(f"⚠️  Некорректный favicon_url: {type(favicon_url)}, установлен None")
                normalized_favicon_url = None

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Вставляем закладку
                cursor.execute(
                    """INSERT INTO bookmarks (url, title, description, favicon_url, workspace_id) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (normalized_url, title.strip(), description.strip(), normalized_favicon_url, workspace_id)
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
                    favicon_url=normalized_favicon_url,
                    workspace_id=workspace_id
                )
                bookmark.tags = tag_objects

                print(f"✅ Закладка создана: {bookmark} в workspace {workspace_id}")
                if tag_objects:
                    print(f"   🏷️ Привязаны теги: {[tag.name for tag in tag_objects]}")

                return bookmark

        except Exception as e:
            print(f"❌ Ошибка при создании закладки: {e}")
            return None

    def update_bookmark_description(self, bookmark_id: int, description: str) -> bool:
        """
        Обновляет описание закладки

        Args:
            bookmark_id: ID закладки
            description: Новое описание

        Returns:
            bool: True если успешно, False если ошибка
        """
        if not bookmark_id:
            print("❌ Ошибка: ID закладки не может быть пустым")
            return False

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем существование закладки
                cursor.execute("SELECT id FROM bookmarks WHERE id = ?", (bookmark_id,))
                if not cursor.fetchone():
                    print(f"❌ Закладка с ID {bookmark_id} не найдена")
                    return False

                # Обновляем описание
                cursor.execute(
                    "UPDATE bookmarks SET description = ? WHERE id = ?",
                    (description.strip(), bookmark_id)
                )
                conn.commit()

                success = cursor.rowcount > 0
                if success:
                    print(f"✅ Описание закладки {bookmark_id} обновлено: '{description[:50]}...'")
                else:
                    print(f"❌ Не удалось обновить описание закладки {bookmark_id}")

                return success

        except Exception as e:
            print(f"❌ Ошибка при обновлении описания закладки {bookmark_id}: {e}")
            return False

    def update_bookmark(self, bookmark_id: int, title: str = None, url: str = None,
                        description: str = None, tags: list = None) -> bool:
        """
        Обновляет закладку

        Args:
            bookmark_id: ID закладки
            title: Новое название
            url: Новый URL
            description: Новое описание
            tags: Новый список тегов

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем существование закладки
                cursor.execute("SELECT id FROM bookmarks WHERE id = ?", (bookmark_id,))
                if not cursor.fetchone():
                    print(f"❌ Закладка с ID {bookmark_id} не найдена")
                    return False

                # Обновляем основные данные
                update_fields = []
                update_values = []

                if title is not None:
                    update_fields.append("title = ?")
                    update_values.append(title)

                if url is not None:
                    update_fields.append("url = ?")
                    update_values.append(url)

                if description is not None:
                    update_fields.append("description = ?")
                    update_values.append(description)

                if update_fields:
                    update_values.append(bookmark_id)
                    query = f"UPDATE bookmarks SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(query, update_values)

                # Обновляем теги
                if tags is not None:
                    # Удаляем старые теги - ИСПРАВЛЕНО: используем правильное имя таблицы
                    cursor.execute("DELETE FROM bookmark_tag_relation WHERE bookmark_id = ?", (bookmark_id,))

                    # Добавляем новые теги
                    for tag_name in tags:
                        tag = self._get_or_create_tag_with_connection(cursor, tag_name.strip())
                        if tag and tag.id:
                            cursor.execute(
                                "INSERT INTO bookmark_tag_relation (bookmark_id, tag_id) VALUES (?, ?)",
                                (bookmark_id, tag.id)
                            )

                conn.commit()
                print(f"✅ Закладка {bookmark_id} успешно обновлена")
                return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении закладки {bookmark_id}: {e}")
            return False

    def update(self, bookmark_id: int, title: Optional[str] = None,
               description: Optional[str] = None, tags: Optional[List[str]] = None,
               url: Optional[str] = None, favicon_url: Optional[str] = None,
               workspace_id: Optional[int] = None) -> bool:
        """
        Обновляет данные закладки

        Args:
            bookmark_id: ID закладки
            title: Новый заголовок
            description: Новое описание
            tags: Новые теги
            url: Новый URL
            favicon_url: Новая иконка
            workspace_id: Новый workspace

        Returns:
            bool: True если обновление успешно
        """
        # Проверяем существование закладки
        existing_bookmark = self.get(bookmark_id)
        if not existing_bookmark:
            print(f"❌ Закладка с ID {bookmark_id} не существует")
            return False

        # Если обновляем URL - валидируем его
        normalized_url = None
        if url is not None:
            normalized_url = self.normalize_url(url)
            if not self.validate_url(normalized_url):
                print(f"❌ Ошибка: некорректный URL '{url}'")
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

                if url is not None:
                    update_fields.append("url = ?")
                    update_values.append(normalized_url)

                if favicon_url is not None:
                    update_fields.append("favicon_url = ?")
                    update_values.append(favicon_url)

                if workspace_id is not None:
                    update_fields.append("workspace_id = ?")
                    update_values.append(workspace_id)

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

                update_info = []
                if title is not None: update_info.append("заголовок")
                if description is not None: update_info.append("описание")
                if url is not None: update_info.append("URL")
                if tags is not None: update_info.append("теги")
                if workspace_id is not None: update_info.append("workspace")

                print(f"✅ Закладка с ID {bookmark_id} обновлена: {', '.join(update_info)}")
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

    def get(self, bookmark_id: int) -> Optional[WebBookmark]:
        """Возвращает закладку по ID"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """SELECT id, url, title, description, favicon_url, workspace_id, created_at, updated_at 
                    FROM bookmarks WHERE id = ?""",
                    (bookmark_id,)
                )
                result = cursor.fetchone()

                if not result:
                    print(f"❌ Закладка с ID {bookmark_id} не найдена")
                    return None

                (bookmark_id, url, title, description, favicon_url, workspace_id, created_at, updated_at) = result

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
                    workspace_id=workspace_id,
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

    def get_all(self, workspace_id: Optional[int] = None) -> List[WebBookmark]:
        """Возвращает все закладки с фильтрацией по workspace"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                if workspace_id is not None:
                    cursor.execute(
                        """SELECT id, url, title, description, favicon_url, workspace_id, created_at, updated_at 
                        FROM bookmarks WHERE workspace_id = ? ORDER BY created_at DESC""",
                        (workspace_id,)
                    )
                else:
                    cursor.execute(
                        """SELECT id, url, title, description, favicon_url, workspace_id, created_at, updated_at 
                        FROM bookmarks ORDER BY created_at DESC"""
                    )

                results = cursor.fetchall()

                bookmarks = []
                for (
                        bookmark_id, url, title, description, favicon_url, workspace_id, created_at,
                        updated_at) in results:
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
                        workspace_id=workspace_id,
                        created_date=created_date,
                        updated_date=updated_date
                    )
                    bookmark.tags = tag_objects
                    bookmarks.append(bookmark)

                workspace_info = f" в workspace {workspace_id}" if workspace_id is not None else ""
                print(f"✅ Загружено закладок{workspace_info}: {len(bookmarks)}")
                return bookmarks

        except Exception as e:
            print(f"❌ Ошибка при получении закладок: {e}")
            return []

    def get_bookmarks_by_workspace(self, workspace_id: int) -> List[WebBookmark]:
        """Возвращает закладки для указанного рабочего пространства"""
        return self.get_all(workspace_id)

    def search(self, search_text: str = "", workspace_id: Optional[int] = None) -> List[WebBookmark]:
        """Ищет закладки по тексту с фильтрацией по workspace"""
        all_bookmarks = self.get_all(workspace_id)

        if not search_text.strip():
            return all_bookmarks

        search_text_lower = search_text.lower()
        filtered_bookmarks = []

        for bookmark in all_bookmarks:
            if (search_text_lower in bookmark.title.lower() or
                    search_text_lower in bookmark.url.lower() or
                    (bookmark.description and search_text_lower in bookmark.description.lower())):
                filtered_bookmarks.append(bookmark)

        workspace_info = f" в workspace {workspace_id}" if workspace_id is not None else ""
        print(f"✅ Найдено закладок по запросу '{search_text}'{workspace_info}: {len(filtered_bookmarks)}")
        return filtered_bookmarks

    def search_by_tags(self, tag_names: List[str], workspace_id: Optional[int] = None) -> List[WebBookmark]:
        """Ищет закладки по тегам с фильтрацией по workspace"""
        all_bookmarks = self.get_all(workspace_id)

        if not tag_names:
            return all_bookmarks

        filtered_bookmarks = []

        for bookmark in all_bookmarks:
            bookmark_tag_names = [tag.name.lower() for tag in bookmark.tags]
            # Проверяем, что ВСЕ указанные теги присутствуют
            if all(tag_name.lower() in bookmark_tag_names for tag_name in tag_names):
                filtered_bookmarks.append(bookmark)

        workspace_info = f" в workspace {workspace_id}" if workspace_id is not None else ""
        print(f"✅ Найдено закладок по тегам {tag_names}{workspace_info}: {len(filtered_bookmarks)}")
        return filtered_bookmarks

    def search_by_text_and_tags(self, search_text: str, tag_names: List[str],
                                workspace_id: Optional[int] = None) -> List[WebBookmark]:
        """Ищет закладки по тексту И тегам с фильтрацией по workspace"""
        # Сначала фильтруем по тегам
        tagged_bookmarks = self.search_by_tags(tag_names, workspace_id)

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

        workspace_info = f" в workspace {workspace_id}" if workspace_id is not None else ""
        print(
            f"✅ Найдено закладок по тексту '{search_text}' и тегам {tag_names}{workspace_info}: {len(filtered_bookmarks)}")
        return filtered_bookmarks

    def parse_url_metadata(self, url: str) -> Dict[str, Optional[str]]:
        """
        Извлекает метаданные из веб-страницы
        """
        try:
            print(f"🔍 Получение метаданных для: {url}")

            # Увеличиваем таймаут для YouTube и других тяжелых сайтов
            timeout = 15 if 'youtube.com' in url or 'youtu.be' in url else 10

            # Делаем запрос с увеличенным таймаутом
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            # Парсим HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Извлекаем заголовок
            title = self._extract_title(soup)

            # Извлекаем описание
            description = self._extract_description(soup)

            # Извлекаем favicon
            favicon_url = self._extract_favicon(soup, url)

            # Извлекаем другие полезные метаданные
            metadata = {
                'title': title,
                'description': description,
                'favicon_url': favicon_url,
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

    def _extract_favicon(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Извлекает favicon URL"""
        # Ищем favicon в различных местах
        favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if favicon and favicon.get('href'):
            favicon_url = favicon['href']
            # Преобразуем относительный URL в абсолютный
            if favicon_url.startswith('/'):
                parsed_base = urlparse(base_url)
                favicon_url = f"{parsed_base.scheme}://{parsed_base.netloc}{favicon_url}"
            elif not favicon_url.startswith(('http://', 'https://')):
                parsed_base = urlparse(base_url)
                favicon_url = f"{parsed_base.scheme}://{parsed_base.netloc}/{favicon_url}"
            return favicon_url

        # Пробуем стандартный путь
        parsed_base = urlparse(base_url)
        standard_favicon = f"{parsed_base.scheme}://{parsed_base.netloc}/favicon.ico"

        # Проверяем существует ли стандартный favicon
        try:
            response = self.session.head(standard_favicon, timeout=5)
            if response.status_code == 200:
                return standard_favicon
        except:
            pass

        return None

    def _get_fallback_metadata(self, url: str, error: str) -> Dict[str, Optional[str]]:
        """Возвращает метаданные по умолчанию при ошибке"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        return {
            'title': f"{domain} (недоступен)",
            'description': f"Не удалось загрузить страницу: {error}",
            'favicon_url': None,
            'url': url,
            'status_code': 0,
            'content_type': '',
            'content_length': 0
        }

    def add_bookmark_with_metadata(self, url: str, tags: Optional[List[str]] = None,
                                   workspace_id: int = 1) -> Optional[WebBookmark]:
        """
        Добавляет закладку с автоматическим получением метаданных
        """
        try:
            print(f"📥 Добавление закладки: {url}")

            # ПРОВЕРКА И НОРМАЛИЗАЦИЯ workspace_id
            normalized_workspace_id = 1
            if isinstance(workspace_id, int):
                normalized_workspace_id = workspace_id
            else:
                print(f"⚠️  workspace_id имеет неверный тип: {type(workspace_id)}, преобразуем в int")
                try:
                    normalized_workspace_id = int(workspace_id) if workspace_id else 1
                except (ValueError, TypeError):
                    print(f"⚠️  Не удалось преобразовать workspace_id, используем значение по умолчанию 1")
                    normalized_workspace_id = 1

            print(f"🔍 Используем workspace_id: {normalized_workspace_id}")

            # Получаем метаданные
            metadata = self.parse_url_metadata(url)

            # Используем безопасный метод создания
            bookmark = self.safe_create_bookmark(
                url=metadata['url'],
                title=metadata['title'],
                description=metadata['description'] or '',
                tags=tags,
                workspace_id=normalized_workspace_id  # Используем нормализованный ID
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

    def safe_create_bookmark(self, url: str, title: str = "", description: str = "",
                             tags: Optional[List[str]] = None, workspace_id: int = 1) -> Optional[WebBookmark]:
        """
        Безопасное создание закладки без favicon_url
        """
        # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
        print(f"🔍 Отладка BookmarkManager.safe_create_bookmark():")
        print(f"   - URL: {url}")
        print(f"   - Title: {title}")
        print(f"   - Description: {description}")
        print(f"   - Tags: {tags}")
        print(f"   - Workspace ID: {workspace_id} (тип: {type(workspace_id)})")

        if not url or not url.strip():
            print("❌ Ошибка: URL не может быть пустым")
            return None

        normalized_url = self.normalize_url(url)

        if not self.validate_url(normalized_url):
            print(f"❌ Ошибка: некорректный URL '{url}'")
            return None

        if not title.strip():
            title = self._extract_domain(normalized_url)

        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Вставляем закладку без favicon_url
                cursor.execute(
                    """INSERT INTO bookmarks (url, title, description, workspace_id) 
                    VALUES (?, ?, ?, ?)""",
                    (normalized_url, title.strip(), description.strip(), workspace_id)
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

                bookmark = WebBookmark(
                    url=normalized_url,
                    title=title,
                    description=description,
                    bookmark_id=bookmark_id,
                    favicon_url=None,  # Всегда None для безопасного создания
                    workspace_id=workspace_id
                )
                bookmark.tags = tag_objects

                print(f"✅ Закладка создана (без иконки): {bookmark} в workspace {workspace_id}")
                return bookmark

        except Exception as e:
            print(f"❌ Ошибка при безопасном создании закладки: {e}")
            return None

    def bulk_add_bookmarks(self, urls: List[str], common_tags: Optional[List[str]] = None,
                           workspace_id: int = 1) -> List[WebBookmark]:
        """
        Добавляет несколько закладок за раз

        Args:
            urls: Список URL
            common_tags: Общие теги для всех закладок
            workspace_id: ID рабочего пространства

        Returns:
            List[WebBookmark]: Список созданных закладок
        """
        created_bookmarks = []

        for i, url in enumerate(urls):
            print(f"📥 Обработка {i + 1}/{len(urls)}: {url}")

            bookmark = self.add_bookmark_with_metadata(url, common_tags, workspace_id)
            if bookmark:
                created_bookmarks.append(bookmark)

            # Небольшая задержка чтобы не перегружать сервер
            time.sleep(1)

        print(f"✅ Создано закладок: {len(created_bookmarks)} из {len(urls)}")
        return created_bookmarks

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

    def get_bookmark_stats(self, workspace_id: Optional[int] = None) -> dict:
        """
        Возвращает статистику по закладкам

        Args:
            workspace_id: ID рабочего пространства

        Returns:
            dict: Статистика закладок
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                if workspace_id is not None:
                    cursor.execute(
                        "SELECT COUNT(*) FROM bookmarks WHERE workspace_id = ?",
                        (workspace_id,)
                    )
                else:
                    cursor.execute("SELECT COUNT(*) FROM bookmarks")

                total_count = cursor.fetchone()[0]

                if workspace_id is not None:
                    cursor.execute(
                        """SELECT COUNT(DISTINCT t.id) 
                        FROM tags t
                        JOIN bookmark_tag_relation btr ON t.id = btr.tag_id
                        JOIN bookmarks b ON btr.bookmark_id = b.id
                        WHERE b.workspace_id = ?""",
                        (workspace_id,)
                    )
                else:
                    cursor.execute(
                        """SELECT COUNT(DISTINCT t.id) 
                        FROM tags t
                        JOIN bookmark_tag_relation btr ON t.id = btr.tag_id"""
                    )

                tags_count = cursor.fetchone()[0]

                if workspace_id is not None:
                    cursor.execute(
                        """SELECT COUNT(*) FROM bookmarks 
                        WHERE workspace_id = ? AND DATE(created_at) = DATE('now')""",
                        (workspace_id,)
                    )
                else:
                    cursor.execute(
                        """SELECT COUNT(*) FROM bookmarks 
                        WHERE DATE(created_at) = DATE('now')"""
                    )

                today_count = cursor.fetchone()[0]

                stats = {
                    'total': total_count,
                    'with_tags': tags_count,
                    'added_today': today_count
                }

                workspace_info = f" для workspace {workspace_id}" if workspace_id is not None else ""
                print(f"📊 Статистика закладок{workspace_info}: {stats}")
                return stats

        except Exception as e:
            print(f"❌ Ошибка при получении статистики закладок: {e}")
            return {'total': 0, 'with_tags': 0, 'added_today': 0}
