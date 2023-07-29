from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGraphicsView, QGraphicsScene
import numpy as np

class Ui_MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.measuring = False
        self.points = []
        self.currentPos = None

        self.measureButton = QPushButton("Measure")
        self.measureButton.clicked.connect(self.measureLength)

        self.graphicsView = QGraphicsView()
        self.graphicsScene = QGraphicsScene()
        self.graphicsView.setScene(self.graphicsScene)

        layout = QVBoxLayout()
        layout.addWidget(self.graphicsView)
        layout.addWidget(self.measureButton)
        self.setLayout(layout)

        self.setMouseTracking(True)

    def measureLength(self):
        if not self.measuring:
            self.measuring = True
            self.points = []
            self.measureButton.setText("Finish")
            QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        else:
            self.stopMeasureLength()

    def stopMeasureLength(self):
        self.measuring = False
        if len(self.points) >= 2:
            distance = np.sqrt((self.points[-1][0] - self.points[0][0]) ** 2 + (self.points[-1][1] - self.points[0][1]) ** 2)
            print('Total Distance:', distance, 'pixels')

        self.measureButton.setText("Measure")
        QApplication.restoreOverrideCursor()

    def mousePressEvent(self, event):
        if self.measuring and event.button() == Qt.LeftButton:
            pos = self.graphicsView.mapToScene(event.pos())
            self.points.append((pos.x(), pos.y()))
            self.currentPos = (pos.x(), pos.y())
            self.update()

    def mouseMoveEvent(self, event):
        if self.measuring:
            pos = self.graphicsView.mapToScene(event.pos())
            self.currentPos = (pos.x(), pos.y())
            self.update()

    def paintEvent(self, event):
        if self.measuring and self.currentPos:
            painter = QPainter(self)
            pen = QPen(Qt.red)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(self.points[0][0], self.points[0][1], self.currentPos[0], self.currentPos[1])

app = QApplication([])
window = Ui_MainWindow()
window.show()
app.exec_()
