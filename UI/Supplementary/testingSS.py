from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
import sys

class WidgetScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Hello, this is a widget.")
        layout.addWidget(self.label)

        screenshot_button = QPushButton("Take Screenshot")
        screenshot_button.clicked.connect(self.take_screenshot)
        layout.addWidget(screenshot_button)

        self.setLayout(layout)

    def take_screenshot(self):
        screenshot = self.grab()  # Capture the contents of the widget as a pixmap
        screenshot.save("widget_screenshot.png", "PNG")  # Save the pixmap as a PNG image

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WidgetScreenshotApp()
    window.show()
    sys.exit(app.exec_())
