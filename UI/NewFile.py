import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon

class NewFileUI(QtWidgets.QDialog): 
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("New File")
        self.setFixedSize(300, 150)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))

        layout = QtWidgets.QFormLayout()

        self.file_name_edit = QtWidgets.QLineEdit(self)
        self.location_edit = QtWidgets.QLineEdit(self)
        self.sampling_date_edit = QtWidgets.QLineEdit(self)

        self.sampling_date_edit.setReadOnly(True)  # Make sampling date read-only

        layout.addRow("File Name:", self.file_name_edit)
        layout.addRow("Location:", self.location_edit)
        layout.addRow("Sampling Date:", self.sampling_date_edit)

        start_button = QtWidgets.QPushButton("Start")

        button_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.addButton(start_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)

        start_button.clicked.connect(self.on_accepted)
        button_box.rejected.connect(self.on_rejected)

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

