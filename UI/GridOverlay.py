import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt


class GridOverlay(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.red)
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw a line from (x1, y1) to (x2, y2)
        x1, y1 = 950, 00
        x2, y2 = 950, 950
        painter.drawLine(x1, y1, x2, y2)
        x1, y1 = 290, 400
        x2, y2 = 1570, 400
        painter.drawLine(x1, y1, x2, y2)