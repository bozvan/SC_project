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
        self._updating_format = False  # Флаг для предотвращения рекурсии
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Создаем текстовый редактор
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(True)

        # Создаем панель инструментов
        self.toolbar = self.create_toolbar()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)

        # Подключаем сигналы ПОСЛЕ создания всех элементов
        self.text_edit.cursorPositionChanged.connect(self.update_format_actions)

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Форматирование")
        toolbar.setIconSize(QSize(16, 16))

        # Шрифт
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.set_font_family)
        toolbar.addWidget(self.font_combo)

        # Размер шрифта
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(12)
        self.font_size.valueChanged.connect(self.set_font_size)
        toolbar.addWidget(self.font_size)

        toolbar.addSeparator()

        # Жирный
        bold_action = QAction("Ж", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.toggle_bold)
        toolbar.addAction(bold_action)
        self.format_actions['bold'] = bold_action

        # Курсив
        italic_action = QAction("К", self)
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self.toggle_italic)
        toolbar.addAction(italic_action)
        self.format_actions['italic'] = italic_action

        # Подчеркивание
        underline_action = QAction("Ч", self)
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

        # Списки
        bullet_list_action = QAction("•", self)
        bullet_list_action.setCheckable(True)
        bullet_list_action.triggered.connect(self.toggle_bullet_list)
        toolbar.addAction(bullet_list_action)
        self.format_actions['bullet_list'] = bullet_list_action

        number_list_action = QAction("1.", self)
        number_list_action.setCheckable(True)
        number_list_action.triggered.connect(self.toggle_number_list)
        toolbar.addAction(number_list_action)
        self.format_actions['number_list'] = number_list_action

        toolbar.addSeparator()

        # Отменить/Повторить
        undo_action = QAction("↶", self)
        undo_action.triggered.connect(self.text_edit.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction("↷", self)
        redo_action.triggered.connect(self.text_edit.redo)
        toolbar.addAction(redo_action)

        return toolbar

    def toggle_bold(self):
        """Переключение жирного начертания"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return

        fmt = QTextCharFormat()
        weight = QFont.Weight.Bold if not cursor.charFormat().fontWeight() == QFont.Weight.Bold else QFont.Weight.Normal
        fmt.setFontWeight(weight)
        cursor.mergeCharFormat(fmt)
        self.text_edit.setFocus()

    def toggle_italic(self):
        """Переключение курсива"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return

        fmt = QTextCharFormat()
        fmt.setFontItalic(not cursor.charFormat().fontItalic())
        cursor.mergeCharFormat(fmt)
        self.text_edit.setFocus()

    def toggle_underline(self):
        """Переключение подчеркивания"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return

        fmt = QTextCharFormat()
        fmt.setFontUnderline(not cursor.charFormat().fontUnderline())
        cursor.mergeCharFormat(fmt)
        self.text_edit.setFocus()

    def set_text_color(self):
        """Установка цвета текста"""
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                fmt = QTextCharFormat()
                fmt.setForeground(color)
                cursor.mergeCharFormat(fmt)
                self.text_edit.setFocus()

    def set_font_family(self, font):
        """Установка семейства шрифтов"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontFamily(font.family())
            cursor.mergeCharFormat(fmt)
            self.text_edit.setFocus()

    def set_font_size(self, size):
        """Установка размера шрифта"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)
            cursor.mergeCharFormat(fmt)
            self.text_edit.setFocus()

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

    def toggle_bullet_list(self):
        """Переключение маркированного списка"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()

        if self.format_actions['bullet_list'].isChecked():
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.Style.ListDisc)
            cursor.createList(list_fmt)
        else:
            # Снимаем форматирование списка
            block_fmt = QTextBlockFormat()
            cursor.setBlockFormat(block_fmt)

        self.text_edit.setFocus()

    def toggle_number_list(self):
        """Переключение нумерованного списка"""
        if self._updating_format:
            return

        cursor = self.text_edit.textCursor()

        if self.format_actions['number_list'].isChecked():
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.Style.ListDecimal)
            cursor.createList(list_fmt)
        else:
            # Снимаем форматирование списка
            block_fmt = QTextBlockFormat()
            cursor.setBlockFormat(block_fmt)

        self.text_edit.setFocus()

    def update_format_actions(self):
        """Обновление состояния кнопок панели инструментов"""
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

            # Обновляем комбо-боксы
            current_font = char_fmt.font()
            if current_font.family():
                self.font_combo.setCurrentFont(current_font)

            font_size = char_fmt.fontPointSize()
            if font_size > 0:
                self.font_size.setValue(int(font_size))
        finally:
            self._updating_format = False

    def set_html(self, html_content):
        """Установка HTML содержимого"""
        # Временно отключаем обновление формата
        self.text_edit.cursorPositionChanged.disconnect(self.update_format_actions)
        try:
            self.text_edit.setHtml(html_content)
        finally:
            # Восстанавливаем соединение
            self.text_edit.cursorPositionChanged.connect(self.update_format_actions)

    def to_html(self):
        """Получение HTML содержимого"""
        return self.text_edit.toHtml()

    def set_plain_text(self, text):
        """Установка простого текста"""
        # Временно отключаем обновление формата
        self.text_edit.cursorPositionChanged.disconnect(self.update_format_actions)
        try:
            self.text_edit.setPlainText(text)
        finally:
            # Восстанавливаем соединение
            self.text_edit.cursorPositionChanged.connect(self.update_format_actions)

    def to_plain_text(self):
        """Получение простого текста"""
        return self.text_edit.toPlainText()

    def clear(self):
        """Очистка редактора"""
        self.text_edit.clear()

    def get_text_edit(self):
        """Получение ссылки на QTextEdit"""
        return self.text_edit