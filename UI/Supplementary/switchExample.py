import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class SwitchButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #e6e6e6;
                border: 2px solid #d4d4d4;
                border-radius: 15px;
                padding: 2px;
            }
            QPushButton:checked {
                background-color: #78c16e;
            }
            QPushButton:checked:enabled:hover {
                background-color: #84d174;
            }
            QPushButton:pressed {
                padding: 4px;
            }
            """
        )

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Switch Example")
    window.resize(200, 100)
    layout = QHBoxLayout()

    switch_button = SwitchButton()
    switch_button.setFixedSize(60, 30)
    layout.addWidget(switch_button)

    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
