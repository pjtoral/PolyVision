from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout
import sys

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
        super().__init__(parent)

        self.setWindowTitle("Popup Window")

        self.button = QPushButton("Close", self)
        self.button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
