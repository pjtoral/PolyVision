import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog, QLineEdit, QPushButton

class CalibrateUI(QtWidgets.QDialog): 
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Calibrate")
        self.setFixedSize(415, 80)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))

        layout = QtWidgets.QFormLayout()
        self.current_directory = QtWidgets.QLabel("")
        self.distance_edit = QtWidgets.QLineEdit(self)


        layout.addRow("Actual Distance:", self.distance_edit)


        start_button = QtWidgets.QPushButton("Start")

        button_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.addButton(start_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)

        start_button.clicked.connect(self.on_accepted)
        button_box.rejected.connect(self.on_rejected)

        layout.addRow(button_box)
        self.setLayout(layout)


    def on_accepted(self):
        distance = self.distance_edit.text()
        self.accept()

    def on_rejected(self):
        self.reject()


def main():
    app = QApplication(sys.argv)
    stat_ui = CalibrateUI()
    stat_ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

