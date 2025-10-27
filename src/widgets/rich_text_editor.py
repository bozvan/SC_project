from PyQt6.QtWidgets import (QTextEdit, QToolBar, QVBoxLayout, QWidget,
                             QFontComboBox, QSpinBox, QColorDialog, QToolButton)
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

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Форматирование")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setFixedHeight(32)

        # Шрифт
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self.default_font_family))
        self.font_combo.setFixedHeight(24)
        self.font_combo.currentFontChanged.connect(self.set_font_family)
        toolbar.addWidget(self.font_combo)

        # Размер шрифта - увеличенная ширина
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(self.default_font_size)
        self.font_size.setFixedHeight(24)
        self.font_size.setFixedWidth(70)  # Увеличили ширину

        # Явно устанавливаем стиль для спинбокса
        spinbox_style = """
               QSpinBox {
                   background-color: #0d1117;
                   color: white;
                   border: 1px solid #444444;
                   border-radius: 3px;
                   padding: 4px 8px;
                   font-family: "Segoe UI", "Arial", sans-serif;
                   font-size: 12px;
               }
               QSpinBox:hover {
                   border: 1px solid #666666;
               }
               QSpinBox:focus {
                   border: 1px solid #E16428;
               }
               QSpinBox::up-button, QSpinBox::down-button {
                   background-color: #2d3746;
                   border: none;
                   width: 15px;
                   height: 10px;
                   margin: 0px;
               }
               QSpinBox::up-button {
                   subcontrol-position: top right;
                   border-bottom: 1px solid #1a1f29;
               }
               QSpinBox::down-button {
                   subcontrol-position: bottom right;
                   border-top: 1px solid #1a1f29;
               }
               QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                   background-color: #3d4756;
               }
               QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                   background-color: #E16428;
               }
               QSpinBox::up-arrow {
                   width: 0px;
                   height: 0px;
                   border-left: 4px solid transparent;
                   border-right: 4px solid transparent;
                   border-bottom: 5px solid #cccccc;
               }
               QSpinBox::down-arrow {
                   width: 0px;
                   height: 0px;
                   border-left: 4px solid transparent;
                   border-right: 4px solid transparent;
                   border-top: 5px solid #cccccc;
               }
               QSpinBox::up-button:hover::up-arrow {
                   border-bottom-color: white;
               }
               QSpinBox::down-button:hover::down-arrow {
                   border-top-color: white;
               }
               QSpinBox::up-button:pressed::up-arrow, 
               QSpinBox::down-button:pressed::down-arrow {
                   border-bottom-color: white;
                   border-top-color: white;
               }
           """
        self.font_size.setStyleSheet(spinbox_style)

        self.font_size.valueChanged.connect(self.set_font_size)
        toolbar.addWidget(self.font_size)


        # Добавляем разделитель с отступом
        toolbar.addSeparator()

        # Создаем кнопки с фиксированным размером
        button_style = "QToolButton { min-width: 28px; min-height: 24px; max-height: 24px; }"

        # Жирный
        bold_btn = QToolButton()
        bold_btn.setText("B")
        bold_btn.setCheckable(True)
        bold_btn.setStyleSheet(button_style)
        bold_btn.clicked.connect(self.toggle_bold)
        toolbar.addWidget(bold_btn)
        self.format_actions['bold'] = bold_btn

        # Курсив
        italic_btn = QToolButton()
        italic_btn.setText("I")
        italic_btn.setCheckable(True)
        italic_btn.setStyleSheet(button_style)
        italic_btn.clicked.connect(self.toggle_italic)
        toolbar.addWidget(italic_btn)
        self.format_actions['italic'] = italic_btn

        # Подчеркивание
        underline_btn = QToolButton()
        underline_btn.setText("U")
        underline_btn.setCheckable(True)
        underline_btn.setStyleSheet(button_style)
        underline_btn.clicked.connect(self.toggle_underline)
        toolbar.addWidget(underline_btn)
        self.format_actions['underline'] = underline_btn

        toolbar.addSeparator()

        # Цвет текста
        color_btn = QToolButton()
        color_btn.setText("Ц")
        color_btn.setStyleSheet(button_style)
        color_btn.clicked.connect(self.set_text_color)
        toolbar.addWidget(color_btn)

        toolbar.addSeparator()

        # Выравнивание
        align_left_btn = QToolButton()
        align_left_btn.setText("◀")
        align_left_btn.setCheckable(True)
        align_left_btn.setStyleSheet(button_style)
        align_left_btn.clicked.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignLeft))
        toolbar.addWidget(align_left_btn)
        self.format_actions['align_left'] = align_left_btn

        align_center_btn = QToolButton()
        align_center_btn.setText("Ⓧ")
        align_center_btn.setCheckable(True)
        align_center_btn.setStyleSheet(button_style)
        align_center_btn.clicked.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignCenter))
        toolbar.addWidget(align_center_btn)
        self.format_actions['align_center'] = align_center_btn

        align_right_btn = QToolButton()
        align_right_btn.setText("▶")
        align_right_btn.setCheckable(True)
        align_right_btn.setStyleSheet(button_style)
        align_right_btn.clicked.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignRight))
        toolbar.addWidget(align_right_btn)
        self.format_actions['align_right'] = align_right_btn

        toolbar.addSeparator()

        # Отменить/Повторить
        undo_btn = QToolButton()
        undo_btn.setText("↶")
        undo_btn.setToolTip("Отменить (Ctrl+Z)")
        undo_btn.setStyleSheet(button_style)
        undo_btn.clicked.connect(self.text_edit.undo)
        toolbar.addWidget(undo_btn)

        redo_btn = QToolButton()
        redo_btn.setText("↷")
        redo_btn.setToolTip("Повторить (Ctrl+Y)")
        redo_btn.setStyleSheet(button_style)
        redo_btn.clicked.connect(self.text_edit.redo)
        toolbar.addWidget(redo_btn)

        return toolbar

    # Остальные методы остаются без изменений...
    def on_char_format_changed(self, fmt):
        """Обработчик изменения текущего формата символов"""
        if self._updating_format:
            return
        self.update_format_actions()

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
