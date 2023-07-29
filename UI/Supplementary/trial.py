from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import *
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")

        self.button = QPushButton("Open Popup", self)
        self.button.clicked.connect(self.openPopup)
        self.setCentralWidget(self.button)

    def openPopup(self):
        popup = PopupWindow(self)
        popup.exec_()

class PopupWindow(QDialog):
     def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Folder Images")
        #Creation of Things
        self.button = QPushButton("Close", self)
        self.button.setGeometry(QtCore.QRect(0, 170, 100, 100))
        self.button.clicked.connect(self.close)
        self.moderateLabel      =   QtWidgets.QLabel("hello",self)
        self.resize(1000,800)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
