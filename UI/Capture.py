import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSpacerItem, QSizePolicy, QComboBox
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon



class CaptureUI(QtWidgets.QDialog):
    length_clicked = pyqtSignal()
    width_clicked = pyqtSignal()
    save_clicked = pyqtSignal()
    on_rejected = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Capture Image")
        self.setFixedSize(400, 425)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))

        layout = QVBoxLayout()

        self.particle_name_edit = QLineEdit()
        self.length_edit = QLineEdit()
        self.width_edit = QLineEdit()
        self.color_edit = QLineEdit()
        self.shape_edit = QLineEdit()
        self.magnification_edit = QLineEdit()
        self.note_edit = QLineEdit()

        layout.addWidget(QLabel("Particle Name:"))
        particle_name_layout = QHBoxLayout()
        particle_name_layout.addWidget(self.particle_name_edit)
        self.photo_options_combo = QComboBox()
        self.photo_options_combo.addItems(["JPG", "JPEG", "PNG"])
        self.photo_options_combo.setCurrentText("JPG")
        particle_name_layout.addWidget(self.photo_options_combo)
        layout.addLayout(particle_name_layout)

        layout.addWidget(QLabel("Length (mm): "))
        length_layout = QHBoxLayout()
        length_layout.addWidget(self.length_edit)
        self.measure_length_button = QPushButton(" Measure Length ", self)
        self.measure_length_button.clicked.connect(self.measure_length)
        length_layout.addWidget(self.measure_length_button)
        layout.addLayout(length_layout)

        layout.addWidget(QLabel("Width (mm):  "))
        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width_edit)
        self.measure_width_button = QPushButton(" Measure  Width ", self)
        self.measure_width_button.clicked.connect(self.measure_width)
        width_layout.addWidget(self.measure_width_button)
        layout.addLayout(width_layout)

        layout.addWidget(QLabel("Color:"))
        layout.addWidget(self.color_edit)
        layout.addWidget(QLabel("Shape:"))
        layout.addWidget(self.shape_edit)
        layout.addWidget(QLabel("Magnification:"))
        layout.addWidget(self.magnification_edit)
        layout.addWidget(QLabel("Note:"))
        layout.addWidget(self.note_edit)

        self.save_button = QPushButton("Save Image", self)
        self.save_button.clicked.connect(self.saveFrame)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    
    def measure_length(self):
        self.length_clicked.emit()
        self.hide()

    def measure_width(self):
        self.width_clicked.emit()
        self.hide()

    def saveFrame(self):
        self.save_clicked.emit()

    
    def closeEvent(self, event):
        print("here")
        self.on_rejected.emit()
        event.accept()

