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
from Database import *
from functools import partial


class ImageLabel(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

class ImagesUI(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Images")
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        self.setFixedSize(1300, 800)

        main_layout = QHBoxLayout(self)

        # Create the left-side widgets
        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)

        filter_label = QLabel("FILTER")
        self.filaments_checkbox = QCheckBox("Filaments")
        self.fragments_checkbox = QCheckBox("Fragments")
        self.films_checkbox = QCheckBox("Films")
        length_label = QLabel("Length")
        self.length_min_input = QLineEdit()
        self.length_min_input.setPlaceholderText("Min Length")
        self.length_max_input = QLineEdit()
        self.length_max_input.setPlaceholderText("Max Length")
        width_label = QLabel("Width")
        self.width_min_input = QLineEdit()
        self.width_min_input.setPlaceholderText("Min Width")
        self.width_max_input = QLineEdit()
        self.width_max_input.setPlaceholderText("Max Width")

        left_layout.addWidget(filter_label)
        left_layout.addWidget(self.filaments_checkbox)
        left_layout.addWidget(self.fragments_checkbox)
        left_layout.addWidget(self.films_checkbox)
        left_layout.addWidget(length_label)
        left_layout.addWidget(self.length_min_input)
        left_layout.addWidget(self.length_max_input)
        left_layout.addWidget(width_label)
        left_layout.addWidget(self.width_min_input)
        left_layout.addWidget(self.width_max_input)
       

        image_label = QLabel("IMAGE PROPERTIES")
        image_label.setContentsMargins(0,15,0,0)
        particle_details_layout = QVBoxLayout()
        particle_name_label = QLabel("Particle Name")
        length_label = QLabel("Length")
        width_label = QLabel("Width")
        color_label = QLabel("Color")
        shape_label = QLabel("Shape")
        magnification_label = QLabel("Magnification")
        notes_label = QLabel("Notes")

        underline_pn = QFrame()
        underline_pn.setFrameShape(QFrame.HLine)
        underline_pn.setFrameShadow(QFrame.Sunken)

        underline_length = QFrame()
        underline_length.setFrameShape(QFrame.HLine)
        underline_length.setFrameShadow(QFrame.Sunken)

        underline_width = QFrame()
        underline_width.setFrameShape(QFrame.HLine)
        underline_width.setFrameShadow(QFrame.Sunken)

        underline_color = QFrame()
        underline_color.setFrameShape(QFrame.HLine)
        underline_color.setFrameShadow(QFrame.Sunken)

        underline_shape = QFrame()
        underline_shape.setFrameShape(QFrame.HLine)
        underline_shape.setFrameShadow(QFrame.Sunken)

        underline_magnification = QFrame()
        underline_magnification.setFrameShape(QFrame.HLine)
        underline_magnification.setFrameShadow(QFrame.Sunken)

        underline_notes = QFrame()
        underline_notes.setFrameShape(QFrame.HLine)
        underline_notes.setFrameShadow(QFrame.Sunken)

        particle_details_layout.addWidget(image_label)
        particle_details_layout.addWidget(particle_name_label)
        particle_details_layout.addWidget(underline_pn)
        particle_details_layout.addWidget(length_label)
        particle_details_layout.addWidget(underline_length)
        particle_details_layout.addWidget(width_label)
        particle_details_layout.addWidget(underline_width)
        particle_details_layout.addWidget(color_label)
        particle_details_layout.addWidget(underline_color)
        particle_details_layout.addWidget(shape_label)
        particle_details_layout.addWidget(underline_shape)
        particle_details_layout.addWidget(magnification_label)
        particle_details_layout.addWidget(underline_magnification)
        particle_details_layout.addWidget(notes_label)



        left_layout.addLayout(particle_details_layout)
        left_layout.addStretch()

        open_image_button = QPushButton("Open Image")
        self.image_pathway = None
        open_image_button.clicked.connect(lambda: self.open_image(self.image_pathway))
        left_layout.addWidget(open_image_button)

        self.left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.left_widget.setMaximumWidth(int(self.width() * 0.2))  # 20% of the window width
        main_layout.addWidget(self.left_widget, stretch=0)
        


        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_widget_layout = QVBoxLayout()
        self.scroll_widget_layout.setContentsMargins(10, 10, 10, 10) 
        self.scroll_widget.setLayout(self.scroll_widget_layout)

        self.grid_layout = QGridLayout()
        self.row = 0
        self.col = 0
        self.scrape_folder(file_path)  
        self.scroll_widget_layout.addLayout(self.grid_layout)  
        scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(scroll_area, stretch=1) 

    def open_image(self,image_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(image_path))

    def show_image_details(self, image_name):
        pass
        #still ugly
            # if self.image_details_widget:
            #     self.layout.removeWidget(self.image_details_widget)
            #     self.image_details_widget.deleteLater()

            # self.image_details_widget = ImageDetailsWidget(image_name)
            # self.layout.addWidget(self.image_details_widget)

    def create_image_label(self, image_path, image_name):
        container = QWidget()  # Create a container for the image label and name label
        container_layout = QVBoxLayout(container)
        label = QLabel()
        pixmap = QPixmap(image_path)
        label = ImageLabel(image_path)
        scaled_pixmap = pixmap.scaled(200, 170, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)
        label.setCursor(QCursor(Qt.PointingHandCursor))

        def on_image_clicked(label):
            # Reset the background color of all image labels to default (transparent)
            for row in range(self.grid_layout.rowCount()):
                for col in range(self.grid_layout.columnCount()):
                    item = self.grid_layout.itemAtPosition(row, col)
                    if item and item.widget():
                        item.widget().setStyleSheet("padding-top: 10px;  background-color: transparent;")

            # Set the background color of the container to the desired color
            container = label.parentWidget()
            container.setStyleSheet("padding-top: 10px;  background-color: #D3D3D3;")
            self.image_pathway = label.image_path
            # Implement the functionality to show the image details here (if needed)
            # show_image_details(image_name)

        label.mousePressEvent = lambda event, label=label: on_image_clicked(label)

        name_label = QLabel(image_name)
        name_label.setAlignment(Qt.AlignTop)
        name_label.setStyleSheet("QLabel { font-size: 12px; padding-bottom: 10px;}")
        name_label.setAlignment(Qt.AlignHCenter)

        container_layout.addWidget(label)
        container_layout.addWidget(name_label)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Add padding to the container widget to make the background color bigger than the image
        container.setStyleSheet("padding-top: 10px;  background-color: transparent;")  # Set container background transparent

        self.grid_layout.addWidget(container, self.row, self.col)
        self.col += 1
        if self.col == 4:
            self.row += 2
            self.col = 0

        return container, label

    def is_image_file(self, file_path):
        image_reader = QImageReader(file_path)
        return image_reader.canRead()

    def scrape_folder(self, folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if self.is_image_file(file_path):
                label = self.create_image_label(file_path, filename)
