import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton, QVBoxLayout, QGraphicsView, QGraphicsScene, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import QTimer, QEvent, Qt


import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton, QVBoxLayout, QGraphicsView, QGraphicsScene, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import QTimer, QEvent, Qt


class CenterLinesGraphicsView(QGraphicsView):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setAlignment(Qt.AlignCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.pixmap_item = self.scene.addPixmap(pixmap)

    def resizeEvent(self, event):
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def drawBackground(self, painter, rect):
        # Call the base class implementation to preserve the default behavior
        super().drawBackground(painter, rect)

        # Draw vertical and horizontal center lines
        center_x = int(self.viewport().width() / 2)
        center_y = int(self.viewport().height() / 2)

        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawLine(center_x, 0, center_x, self.viewport().height())
        painter.drawLine(0, center_y, self.viewport().width(), center_y)



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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Example of how to use the self-destructing widget
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)

    # Load the example image
    pixmap = QPixmap("path_to_your_image.png")
    graphics_view = CenterLinesGraphicsView(pixmap)
    layout.addWidget(graphics_view)

    def show_message():
        title = "Self-Destructing Message"
        message = "This message will self-destruct in 5 seconds!"
        duration = 5

        msg_box = SelfDestructingMessageBox(title, message, duration, main_widget)
        msg_box.show()

    button = QPushButton("Show Self-Destructing Message")
    button.clicked.connect(show_message)
    layout.addWidget(button)

    main_widget.show()
    sys.exit(app.exec_())
