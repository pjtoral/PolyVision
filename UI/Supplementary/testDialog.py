import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel

class MyDialog(QDialog):
    def __init__(self, text="", parent=None):
        super().__init__(parent)

        # Create a dialog
        self.setWindowTitle("Custom Dialog")
        self.setGeometry(200, 200, 300, 150)

        # Create a layout for the dialog
        layout = QVBoxLayout()

        # Add a label with the provided text
        label = QLabel(text, self)

        # Add a Done button
        done_button = QPushButton("Done", self)
        done_button.clicked.connect(self.accept)

        # Add widgets to the layout
        layout.addWidget(label)
        layout.addWidget(done_button)

        # Set the layout for the dialog
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    initial_text = "Place Petri Dish"  # Set the initial text here
    dialog = MyDialog(initial_text)
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        print("User clicked Done.")
    
    sys.exit(app.exec_())
