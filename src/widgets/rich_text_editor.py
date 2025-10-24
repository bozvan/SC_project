from PyQt6.QtWidgets import (QTextEdit, QToolBar, QVBoxLayout, QWidget,
                             QFontComboBox, QSpinBox, QColorDialog)
from PyQt6.QtGui import (QTextCharFormat, QFont, QTextListFormat,
                         QTextBlockFormat, QTextCursor, QAction)
from PyQt6.QtCore import Qt, QSize


class RichTextEditor(QWidget):
    """Виджет богатого текстового редактора с панелью инструментов"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.format_actions = {}
        self._updating_format = False
        self.default_font_size = 12
        self.default_font_family = "Arial"
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Создаем текстовый редактор
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(True)

        # Устанавливаем начальный формат по умолчанию
        default_fmt = QTextCharFormat()
        default_fmt.setFontPointSize(self.default_font_size)
        default_fmt.setFontFamily(self.default_font_family)
        self.text_edit.setCurrentCharFormat(default_fmt)

        # Создаем панель инструментов
        self.toolbar = self.create_toolbar()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)

        # Подключаем сигналы
        self.text_edit.cursorPositionChanged.connect(self.update_format_actions)
        self.text_edit.currentCharFormatChanged.connect(self.on_char_format_changed)

    def on_char_format_changed(self, fmt):
        """Обработчик изменения текущего формата символов"""
        if self._updating_format:
            return
        self.update_format_actions()

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Форматирование")
        toolbar.setIconSize(QSize(16, 16))

        # Шрифт
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self.default_font_family))
        self.font_combo.currentFontChanged.connect(self.set_font_family)
        toolbar.addWidget(self.font_combo)

        # Размер шрифта
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(self.default_font_size)
        self.font_size.valueChanged.connect(self.set_font_size)
        toolbar.addWidget(self.font_size)

        toolbar.addSeparator()

        # Жирный
        bold_action = QAction("B", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.toggle_bold)
        toolbar.addAction(bold_action)
        self.format_actions['bold'] = bold_action

        # Курсив
        italic_action = QAction("I", self)
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self.toggle_italic)
        toolbar.addAction(italic_action)
        self.format_actions['italic'] = italic_action

        # Подчеркивание
        underline_action = QAction("U", self)
        underline_action.setCheckable(True)
        underline_action.triggered.connect(self.toggle_underline)
        toolbar.addAction(underline_action)
        self.format_actions['underline'] = underline_action

        toolbar.addSeparator()

        # Цвет текста
        color_action = QAction("Ц", self)
        color_action.triggered.connect(self.set_text_color)
        toolbar.addAction(color_action)

        toolbar.addSeparator()

        # Выравнивание
        align_left_action = QAction("◀", self)
        align_left_action.setCheckable(True)
        align_left_action.triggered.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignLeft))
        toolbar.addAction(align_left_action)
        self.format_actions['align_left'] = align_left_action

        align_center_action = QAction("Ⓧ", self)
        align_center_action.setCheckable(True)
        align_center_action.triggered.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignCenter))
        toolbar.addAction(align_center_action)
        self.format_actions['align_center'] = align_center_action

        align_right_action = QAction("▶", self)
        align_right_action.setCheckable(True)
        align_right_action.triggered.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignRight))
        toolbar.addAction(align_right_action)
        self.format_actions['align_right'] = align_right_action

        toolbar.addSeparator()

        # Отменить/Повторить
        undo_action = QAction("↶", self)
        undo_action.setToolTip("Отменить (Ctrl+Z)")
        undo_action.triggered.connect(self.text_edit.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction("↷", self)
        redo_action.setToolTip("Повторить (Ctrl+Y)")
        redo_action.triggered.connect(self.text_edit.redo)
        toolbar.addAction(redo_action)

        return toolbar

    def get_current_format(self):
        """Получает текущий формат символов"""
        cursor = self.text_edit.textCursor()
        return cursor.charFormat()

    def apply_format_change(self, format_change_func):
        """Применяет изменение формата, сохраняя остальные стили"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()

        # Получаем текущий формат
        current_format = self.get_current_format()

        # Создаем новый формат на основе текущего
        new_format = QTextCharFormat(current_format)

        # Применяем изменение
        format_change_func(new_format)

        # Применяем обновленный формат
        if cursor.hasSelection():
            cursor.mergeCharFormat(new_format)
        else:
            self.text_edit.setCurrentCharFormat(new_format)

        self.text_edit.setFocus()

    def toggle_bold(self):
        """Переключение жирного стиля"""

        def change_bold(fmt):
            is_bold = fmt.fontWeight() == QFont.Weight.Bold
            new_weight = QFont.Weight.Normal if is_bold else QFont.Weight.Bold
            fmt.setFontWeight(new_weight)

        self.apply_format_change(change_bold)

    def toggle_italic(self):
        """Переключение курсивного стиля"""

        def change_italic(fmt):
            fmt.setFontItalic(not fmt.fontItalic())

        self.apply_format_change(change_italic)

    def toggle_underline(self):
        """Переключение подчеркивания"""

        def change_underline(fmt):
            fmt.setFontUnderline(not fmt.fontUnderline())

        self.apply_format_change(change_underline)

    def set_text_color(self):
        """Установка цвета текста"""
        color = QColorDialog.getColor()
        if color.isValid():
            def change_color(fmt):
                fmt.setForeground(color)

            self.apply_format_change(change_color)

    def set_font_family(self, font):
        """Установка семейства шрифтов"""
        if self._updating_format:
            return

        def change_font_family(fmt):
            fmt.setFontFamily(font.family())

        self.apply_format_change(change_font_family)

    def set_font_size(self, size):
        """Установка размера шрифта"""
        if self._updating_format:
            return

        def change_font_size(fmt):
            fmt.setFontPointSize(size)

        self.apply_format_change(change_font_size)

    def set_alignment(self, alignment):
        """Установка выравнивания"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(alignment)
        cursor.mergeBlockFormat(block_fmt)
        self.text_edit.setFocus()

        # Обновляем кнопки выравнивания
        self._updating_format = True
        try:
            for key in ['align_left', 'align_center', 'align_right']:
                self.format_actions[key].setChecked(False)
            if alignment == Qt.AlignmentFlag.AlignLeft:
                self.format_actions['align_left'].setChecked(True)
            elif alignment == Qt.AlignmentFlag.AlignCenter:
                self.format_actions['align_center'].setChecked(True)
            elif alignment == Qt.AlignmentFlag.AlignRight:
                self.format_actions['align_right'].setChecked(True)
        finally:
            self._updating_format = False

    def update_format_actions(self):
        """Обновление состояния кнопок форматирования"""
        if self._updating_format:
            return

        self._updating_format = True
        try:
            cursor = self.text_edit.textCursor()
            char_fmt = cursor.charFormat()
            block_fmt = cursor.blockFormat()

            # Обновляем кнопки форматирования текста
            self.format_actions['bold'].setChecked(char_fmt.fontWeight() == QFont.Weight.Bold)
            self.format_actions['italic'].setChecked(char_fmt.fontItalic())
            self.format_actions['underline'].setChecked(char_fmt.fontUnderline())

            # Обновляем выравнивание
            alignment = block_fmt.alignment()
            self.format_actions['align_left'].setChecked(alignment == Qt.AlignmentFlag.AlignLeft)
            self.format_actions['align_center'].setChecked(alignment == Qt.AlignmentFlag.AlignCenter)
            self.format_actions['align_right'].setChecked(alignment == Qt.AlignmentFlag.AlignRight)

            # Обновляем шрифт и размер
            current_font = char_fmt.font()
            font_family = current_font.family()

            # Если шрифт не установлен (по умолчанию), используем дефолтный
            if not font_family or font_family == "":
                font_family = self.default_font_family
                self.font_combo.setCurrentFont(QFont(font_family))
            else:
                self.font_combo.setCurrentFont(current_font)

            font_size = char_fmt.fontPointSize()
            # Если размер шрифта не установлен (по умолчанию), используем дефолтный
            if font_size <= 0:
                font_size = self.default_font_size
            self.font_size.setValue(int(font_size))

        except Exception as e:
            print(f"Ошибка при обновлении формата: {e}")
        finally:
            self._updating_format = False

    def set_html(self, html_content):
        """Установка HTML контента"""
        # Временно отключаем сигналы для предотвращения рекурсии
        try:
            self.text_edit.cursorPositionChanged.disconnect(self.update_format_actions)
            self.text_edit.currentCharFormatChanged.disconnect(self.on_char_format_changed)
        except:
            pass

        try:
            self.text_edit.setHtml(html_content)
        except Exception as e:
            print(f"Ошибка при установке HTML: {e}")
        finally:
            # Восстанавливаем сигналы
            try:
                self.text_edit.cursorPositionChanged.connect(self.update_format_actions)
                self.text_edit.currentCharFormatChanged.connect(self.on_char_format_changed)
            except:
                pass

    def to_html(self):
        """Получение HTML контента"""
        try:
            return self.text_edit.toHtml()
        except Exception as e:
            print(f"Ошибка при получении HTML: {e}")
            return ""

    def set_plain_text(self, text):
        """Установка простого текста"""
        try:
            self.text_edit.cursorPositionChanged.disconnect(self.update_format_actions)
            self.text_edit.currentCharFormatChanged.disconnect(self.on_char_format_changed)
        except:
            pass

        try:
            self.text_edit.setPlainText(text)
            # Сбрасываем к формату по умолчанию
            default_fmt = QTextCharFormat()
            default_fmt.setFontPointSize(self.default_font_size)
            default_fmt.setFontFamily(self.default_font_family)
            self.text_edit.setCurrentCharFormat(default_fmt)
        except Exception as e:
            print(f"Ошибка при установке текста: {e}")
        finally:
            try:
                self.text_edit.cursorPositionChanged.connect(self.update_format_actions)
                self.text_edit.currentCharFormatChanged.connect(self.on_char_format_changed)
            except:
                pass

    def to_plain_text(self):
        """Получение простого текста"""
        try:
            return self.text_edit.toPlainText()
        except Exception as e:
            print(f"Ошибка при получении текста: {e}")
            return ""

    def clear(self):
        """Очистка редактора"""
        try:
            self.text_edit.clear()
            # Сбрасываем к формату по умолчанию
            default_fmt = QTextCharFormat()
            default_fmt.setFontPointSize(self.default_font_size)
            default_fmt.setFontFamily(self.default_font_family)
            self.text_edit.setCurrentCharFormat(default_fmt)
        except Exception as e:
            print(f"Ошибка при очистке: {e}")

    def get_text_edit(self):
        """Получение текстового редактора"""
        return self.text_edit
