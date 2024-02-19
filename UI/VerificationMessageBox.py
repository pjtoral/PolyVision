import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon

class VerificationBox(QDialog):
    def __init__(self, text="", parent=None):
        super().__init__(parent)

        # Create a dialog
        self.setWindowTitle("C.Scope.AI")
        self.setFixedSize(250, 100)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        layout = QVBoxLayout()

        label = QLabel(text, self)

        # Add a Done button
        button_layout = QHBoxLayout()

        yes_button = QPushButton("YES", self)
        yes_button.clicked.connect(self.accept)

        no_button = QPushButton("NO", self)
        no_button.clicked.connect(self.reject)

        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)

        # Add widgets to the layout
        layout.addWidget(label)
        layout.addLayout(button_layout)

        # Set the layout for the dialog
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    initial_text = "Is this a Microplastic?"  # Set the initial text here
    dialog = VerificationBox(initial_text)
    result = dialog.exec_()
    
    sys.exit(app.exec_())