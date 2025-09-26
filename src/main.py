import sys

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("src/ui/test.ui", self)
        self.setMinimumSize(200, 200)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()