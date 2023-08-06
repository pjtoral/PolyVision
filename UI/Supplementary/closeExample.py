import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

class YourMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Your Application")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)  # Remove close button
        self.setFixedSize(500, 300)  # Set a fixed window size (optional)

    def closeEvent(self, event):
        print("Window is closing due to user action.")
        # Add your custom actions here if needed.

        # Continue with the default close behavior
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = YourMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
