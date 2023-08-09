from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QSize
import sys

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Custom Frameless Dialog")

        # Set the dialog's size
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.button = QPushButton("Close Dialog")
        self.button.clicked.connect(self.close)
        layout.addWidget(self.button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        brush = QBrush(QColor(255, 255, 255, 255))
        painter.setBrush(brush)

        # Create a rounded rectangle within the dialog's size
        rect = self.rect()
        painter.drawRoundedRect(rect, 20, 20)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = CustomDialog()
    dialog.exec_()
    sys.exit(app.exec_())
