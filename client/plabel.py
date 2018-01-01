from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent

class PLable(QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

    def mouseReleaseEvent(self, QMouseEvent):
        self.clicked.emit()