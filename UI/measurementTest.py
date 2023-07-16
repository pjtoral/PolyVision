from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QSize

class CustomWidget(QWidget):
    def sizeHint(self):
        return QSize(400, 400)  # Set the desired size of the widget

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a larger point at (100, 100) in red color
        pen = QPen(Qt.red)
        pen.setWidth(8)  # Increase the pen width to make the point larger
        painter.setPen(pen)
        painter.drawPoint(100, 100)

if __name__ == '__main__':
    app = QApplication([])
    widget = CustomWidget()
    widget.show()
    app.exec_()
