import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog, QLineEdit, QPushButton
from PyQt5.QtCore import *

class GrblUI(QtWidgets.QDialog): 
    manual_clicked = pyqtSignal()
    auto_clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GRBL")
        self.setFixedSize(415, 100)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))

        layout = QtWidgets.QFormLayout()
        label = QtWidgets.QLabel("Connected to Controller. Choose a Mode to Start.")
        label.setAlignment(QtCore.Qt.AlignCenter)  # Center align the label text
        font = label.font()  # Get the current font
        font.setPointSize(9)  # Set the font size to 16 (adjust as needed)
        label.setFont(font) 

        manual_button = QtWidgets.QPushButton("Manual")
        auto_button = QtWidgets.QPushButton("Automatic")

        button_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.addButton(manual_button, QtWidgets.QDialogButtonBox.ActionRole)
        button_box.addButton(auto_button, QtWidgets.QDialogButtonBox.ActionRole)

        top_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        bottom_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        manual_button.clicked.connect(self.manual_grbl)
        auto_button.clicked.connect(self.auto_grbl)

        layout.addItem(top_spacer)
        layout.addRow(label)
        layout.addItem(bottom_spacer)
        layout.addRow(button_box)
        self.setLayout(layout)

    def manual_grbl(self):
        self.manual_clicked.emit()
        self.close()

    def auto_grbl(self):
        print("automatic")
        self.auto_clicked.emit()
        self.close()

def main():
    app = QApplication(sys.argv)
    stat_ui = GrblUI()
    stat_ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

