import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class SelfDestructingMessageBox(QMessageBox):
    def __init__(self, title, message, duration, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Information)
        self.setWindowTitle(title)
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint) 
        self.setText(message)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: white;")

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
