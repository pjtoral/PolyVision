import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog, QLineEdit, QPushButton

class NewFileUI(QtWidgets.QDialog): 
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("New File")
        self.setFixedSize(415, 170)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))

        layout = QtWidgets.QFormLayout()
        self.current_directory = QtWidgets.QLabel("")
        self.update_current_directory_label()
        self.change_directory_button = QtWidgets.QPushButton("Change")
        self.file_name_edit = QtWidgets.QLineEdit(self)
        self.location_edit = QtWidgets.QLineEdit(self)
        self.sampling_date_edit = QtWidgets.QLineEdit(self)

        self.sampling_date_edit.setReadOnly(True)
        layout.addRow("Current dir:", self.current_directory)
        layout.addRow("File Name:", self.file_name_edit)
        layout.addRow("Location:", self.location_edit)
        layout.addRow("Sampling Date:", self.sampling_date_edit)

        start_button = QtWidgets.QPushButton("Start")

        button_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.addButton(self.change_directory_button, QtWidgets.QDialogButtonBox.ActionRole)
        button_box.addButton(start_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)

        start_button.clicked.connect(self.on_accepted)
        button_box.rejected.connect(self.on_rejected)
        self.change_directory_button.clicked.connect(self.change_path)

        layout.addRow(button_box)
        self.setLayout(layout)
        self.sampling_date_edit.setText(QtCore.QDate.currentDate().toString("yyyy-MM-dd"))

    def on_accepted(self):
        file_name = self.file_name_edit.text()
        location = self.location_edit.text()
        sampling_date = self.sampling_date_edit.text()

        self.accept()

    def on_rejected(self):
        self.reject()

    def change_path(self):
        selected_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if selected_directory:
            os.chdir(selected_directory)  # Change the current working directory
            self.update_current_directory_label() 

    def update_current_directory_label(self):
        current_directory = os.getcwd()  # Get the current working directory
        self.current_directory.setText(current_directory)

def main():
    app = QApplication(sys.argv)
    stat_ui = NewFileUI()
    stat_ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

