import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon
class OkayMessageBox(QDialog):
    def __init__(self, text="", parent=None):
        super().__init__(parent)

        # Create a dialog
        self.setWindowTitle("GRBL")
        self.setFixedSize(270, 100)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        layout = QVBoxLayout()

        label = QLabel(text, self)

        # Add a Done button
        done_button = QPushButton("Okay", self)
        done_button.clicked.connect(self.accept)

        # Add widgets to the layout
        layout.addWidget(label)
        layout.addWidget(done_button)

        # Set the layout for the dialog
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    initial_text = "Place Petri Dish. Click Done when finished."  # Set the initial text here
    dialog = OkayMessageBox(initial_text)
    result = dialog.exec_()
    
    sys.exit(app.exec_())
