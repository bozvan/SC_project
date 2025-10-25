from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame

from core.settings_manager import QtSettingsManager


class WorkspaceCard(QFrame):
    """Виджет карточки рабочего пространства"""

    workspaceSelected = pyqtSignal(int)  # ID workspace
    workspaceEditRequested = pyqtSignal(int)  # ID workspace
    workspaceDeleteRequested = pyqtSignal(int)  # ID workspace

    def __init__(self, workspace, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.settings_manager = QtSettingsManager()
        self.id = workspace.id
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        self.setMinimumHeight(160)
        self.setMaximumHeight(160)

        self.setMinimumWidth(self.frameGeometry().width() // 2)
        self.setMaximumWidth(
            self.frameGeometry().width() // 2)  # ширина карточки workspace определяется динамически по ширине виджета
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Заголовок с названием
        title_layout = QtWidgets.QHBoxLayout()
        self.title_label = QtWidgets.QLabel(self.workspace.name)
        title_font = QtGui.QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)

        # Бейдж для workspace по умолчанию
        if self.workspace.is_default:
            default_label = QtWidgets.QLabel("(по умолчанию)")
            default_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
            title_layout.addWidget(default_label)

        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Кнопки управления (скрыты для workspace по умолчанию)
        if not self.workspace.is_default:
            self.btn_edit = QtWidgets.QPushButton("✏️")
            self.btn_edit.setToolTip("Редактировать")
            self.btn_edit.setFixedSize(30, 30)
            self.btn_edit.setStyleSheet("QPushButton { border: none; font-size: 14px; }")
            self.btn_edit.clicked.connect(self.on_edit_clicked)

            self.btn_delete = QtWidgets.QPushButton("🗑️")
            self.btn_delete.setToolTip("Удалить")
            self.btn_delete.setFixedSize(30, 30)
            self.btn_delete.setStyleSheet("QPushButton { border: none; font-size: 14px; color: #e74c3c; }")
            self.btn_delete.clicked.connect(self.on_delete_clicked)

            title_layout.addWidget(self.btn_edit)
            title_layout.addWidget(self.btn_delete)

        layout.addLayout(title_layout)

        # Описание
        if self.workspace.description:
            desc_label = QtWidgets.QLabel(self.workspace.description)
            desc_label.setStyleSheet("color: #7f8c8d; margin-top: 5px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Информация о дате создания
        date_text = f"Создано: {self.workspace.created_date.strftime('%d.%m.%Y')}"
        date_label = QtWidgets.QLabel(date_text)
        date_label.setStyleSheet("color: #95a5a6; font-size: 10px; margin-top: 8px;")
        layout.addWidget(date_label)

        # ДОБАВЬТЕ ЭТУ СТРОКУ - растягивающий элемент перед кнопкой
        layout.addStretch()

        # Кнопка выбора
        self.btn_select = QtWidgets.QPushButton("Выбрать")
        self.btn_select.clicked.connect(self.on_select_clicked)

        if self.workspace.id == self.settings_manager.get_last_workspace():
            self.btn_select.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        else:
            self.btn_select.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)

        layout.addWidget(self.btn_select)

        # ДОБАВЬТЕ ЭТУ СТРОКУ - небольшой отступ снизу
        layout.addSpacing(10)

        # Стиль для workspace по умолчанию
        if self.workspace.is_default:
            self.setProperty("class", "default-workspace")
            self.setStyle(self.style())

    def on_select_clicked(self):
        self.workspaceSelected.emit(self.id)

    def on_edit_clicked(self):
        self.workspaceEditRequested.emit(self.id)

    def on_delete_clicked(self):
        self.workspaceDeleteRequested.emit(self.id)
