import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QResizeEvent, QTransform
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QResizeEvent, QCursor
from PyQt5.QtCore import Qt, pyqtSlot, QUrl
from PyQt5.QtGui import QDesktopServices
import sys 
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog, QLineEdit, QPushButton
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

def open_image(image_path):
    QDesktopServices.openUrl(QUrl.fromLocalFile(image_path))

def show_image_details(self, image_name):
    pass
    #still ugly
        # if self.image_details_widget:
        #     self.layout.removeWidget(self.image_details_widget)
        #     self.image_details_widget.deleteLater()

        # self.image_details_widget = ImageDetailsWidget(image_name)
        # self.layout.addWidget(self.image_details_widget)

def create_image_label(image_path, image_name, self):
    label = QLabel()
    pixmap = QPixmap(image_path)
    scaled_pixmap = pixmap.scaled(400, 170, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
    label.setPixmap(scaled_pixmap)
    label.setAlignment(Qt.AlignCenter)
    label.setCursor(QCursor(Qt.PointingHandCursor))
    label.mousePressEvent = lambda event: open_image(image_path)
    name_label = QLabel(image_name)
    name_label.setAlignment(Qt.AlignTop)
    name_label.setStyleSheet("QLabel { font-size: 12px; color: gray; }")
    name_label.setStyleSheet("padding-left: 5px")
    self.grid_layout.addWidget(label, self.row, self.col)
    self.grid_layout.addWidget(name_label, self.row + 1, self.col)

    self.col += 1
    if self.col == 3:  # Adjust the number of images per row as needed
        self.row += 2
        self.col = 0

    return label

def is_image_file(file_path):
    image_reader = QImageReader(file_path)
    return image_reader.canRead()

def scrape_folder(folder_path, self):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if is_image_file(file_path):
            label = create_image_label(file_path, filename, self)



class ImagesUI(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Images")
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        self.setFixedSize(1000, 800)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a widget to hold the grid layout and add spacing around it
        scroll_widget = QWidget()
        scroll_widget_layout = QVBoxLayout()
        scroll_widget_layout.setContentsMargins(10, 10, 10, 10)  # Set spacing of 10 pixels around the layout
        scroll_widget.setLayout(scroll_widget_layout)

        self.grid_layout = QGridLayout()

        self.row = 0
        self.col = 0
        scrape_folder(file_path, self)  # Call the scrape_folder function with the folder path
        scroll_widget_layout.addLayout(self.grid_layout)  # Add the grid layout to the scroll widget layout
        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        self.image_details_widget = None



class ImageDetailsWidget(QDialog):
    def __init__(self, image_name, parent=None):
        super().__init__(parent)
        self.setFixedSize(1000, 800)
        self.setStyleSheet("background-color: yellow;")

        layout = QVBoxLayout()
        self.setLayout(layout)

        image_name_label = QLabel(image_name)
        image_name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_name_label)