from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt


class WorkspacesWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Создаем простой интерфейс для рабочих пространств
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("<h1>Рабочие пространства</h1><p>Раздел в разработке</p>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
