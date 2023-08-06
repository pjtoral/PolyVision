import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt


class LineDrawingWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.red)
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw a line from (x1, y1) to (x2, y2)
        x1, y1 = 150, 00
        x2, y2 = 150, 300
        painter.drawLine(x1, y1, x2, y2)
        x1, y1 = 00, 150
        x2, y2 = 300, 150
        painter.drawLine(x1, y1, x2, y2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setGeometry(100, 100, 300, 300)

    layout = QVBoxLayout()  # Create a QVBoxLayout
    line_drawing_widget = LineDrawingWidget()
    layout.addWidget(line_drawing_widget)  # Add the LineDrawingWidget to the layout

    window.setLayout(layout)  # Set the layout for the window

    window.show()
    sys.exit(app.exec_())
