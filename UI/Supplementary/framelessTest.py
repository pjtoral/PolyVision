import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class SelfDestructingMessageBox(QMessageBox):
    def __init__(self, title, message, duration, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Information)
        self.setWindowTitle(title)
        self.setText(message)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: white; ")

        self.duration = duration
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(duration * 1000)  # Convert seconds to milliseconds

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)

    def event(self, event):
        if event.type() == QEvent.Paint:
            self.hideButtons()
        return super().event(event)

    def hideButtons(self):
        # Hide all standard buttons to remove the "OK" button
        for button in self.findChildren(QPushButton):
            if self.buttonRole(button) in [QMessageBox.AcceptRole, QMessageBox.RejectRole]:
                button.hide()

class FramelessMessageBox(SelfDestructingMessageBox):
    def initUI(self):
        # Remove the window frame (title bar, close button, etc.)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Add a custom close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(self.text()))
        layout.addWidget(close_button)

if __name__ == "__main__":
    app = QApplication([])
    message_box = FramelessMessageBox("Title", "This is a frameless message box.", 5)
    message_box.show()
    app.exec_()
