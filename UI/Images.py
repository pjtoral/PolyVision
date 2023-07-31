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
    def __init__(self, folder, image_path, image_name, row, column):
        super().__init__()
        self.folder_path = folder
        self.image_path = image_path
        self.image_name = image_name
        self.row = row
        self.col = column

class ImagesUI(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Images")
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        self.setFixedSize(1400, 800)

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
       
        self.filaments_checkbox.setChecked(True)
        self.fragments_checkbox.setChecked(True)
        self.films_checkbox.setChecked(True)


        image_label = QLabel("IMAGE PROPERTIES")
        image_label.setContentsMargins(0,15,0,0)
        particle_details_layout = QVBoxLayout()
        self.particle_name_label = QLabel("Particle Name")
        self.length_label = QLabel("Length")
        self.width_label = QLabel("Width")
        self.color_label = QLabel("Color")
        self.shape_label = QLabel("Shape")
        self.magnification_label = QLabel("Magnification")
        self.notes_label = QLabel("Notes")
        self.notes_label.setWordWrap(True)
        self.notes_label.setFixedWidth(175)
        self.notes_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

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
        particle_details_layout.addWidget(self.particle_name_label)
        particle_details_layout.addWidget(underline_pn)
        particle_details_layout.addWidget(self.length_label)
        particle_details_layout.addWidget(underline_length)
        particle_details_layout.addWidget(self.width_label)
        particle_details_layout.addWidget(underline_width)
        particle_details_layout.addWidget(self.color_label)
        particle_details_layout.addWidget(underline_color)
        particle_details_layout.addWidget(self.shape_label)
        particle_details_layout.addWidget(underline_shape)
        particle_details_layout.addWidget(self.magnification_label)
        particle_details_layout.addWidget(underline_magnification)
        particle_details_layout.addWidget(self.notes_label)



        left_layout.addLayout(particle_details_layout)
        left_layout.addStretch()

        open_image_button = QPushButton("Open Image")
        self.image_pathway = None
        open_image_button.clicked.connect(lambda: self.open_image(self.image_pathway))
        left_layout.addWidget(open_image_button)

        self.left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.left_widget.setMaximumWidth(int(self.width() * 0.2))  
        main_layout.addWidget(self.left_widget, stretch=0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_widget_layout = QVBoxLayout()
        self.scroll_widget_layout.setContentsMargins(10, 10, 10, 10) 
        self.scroll_widget.setLayout(self.scroll_widget_layout)
        self.scroll_widget_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.grid_layout = QGridLayout()
        self.row = 0
        self.col = 0
        self.file_path = file_path
        self.scrape_folder(file_path)  
        self.scroll_widget_layout.addLayout(self.grid_layout)  
        scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(scroll_area) 

        self.filaments_checkbox.stateChanged.connect(self.on_filter_changed)
        self.fragments_checkbox.stateChanged.connect(self.on_filter_changed)
        self.films_checkbox.stateChanged.connect(self.on_filter_changed)
        self.length_min_input.textChanged.connect(self.on_filter_changed)
        self.length_max_input.textChanged.connect(self.on_filter_changed)
        self.width_min_input.textChanged.connect(self.on_filter_changed)
        self.width_max_input.textChanged.connect(self.on_filter_changed)

    def open_image(self,image_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(image_path))

    def create_image_label(self, folder_path, image_path, image_name, row, col):
        container = QWidget()
        container_layout = QVBoxLayout(container)
        label = QLabel()
        pixmap = QPixmap(image_path)
        label = ImageLabel(folder_path, image_path, image_name, row, col)
        scaled_pixmap = pixmap.scaled(200, 170, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)
        label.setCursor(QCursor(Qt.PointingHandCursor))

        def on_image_clicked(label):
            for row in range(self.grid_layout.rowCount()):
                for col in range(self.grid_layout.columnCount()):
                    item = self.grid_layout.itemAtPosition(row, col)
                    if item and item.widget():
                        item.widget().setStyleSheet("padding-top: 10px;padding-left: 10px;padding-right: 10px;   background-color: transparent;")
            data = get_image_data(label.folder_path, label.image_name)
            if data is not None and len(data) > 0:
                first_row = data[0]
                self.particle_name_label.setText("Name: " + first_row[1])  
                self.length_label.setText("Lenght: " +str(first_row[2]))
                self.width_label.setText("Width: " +str(first_row[3]))  
                self.color_label.setText("Color: " +first_row[4])  
                self.shape_label.setText("Shape: " +first_row[5]) 
                self.magnification_label.setText("Magnification: " + str(first_row[6]) +"x")  
                self.notes_label.setText("Note: " + first_row[7]) 
            container = label.parentWidget()
            container.setStyleSheet("padding-top: 10px;padding-left: 10px;padding-right: 10px;   background-color: #D3D3D3;")
            self.image_pathway = label.image_path


        label.mousePressEvent = lambda event, label=label: on_image_clicked(label)

        name_label = QLabel(image_name)
        name_label.setAlignment(Qt.AlignTop)
        name_label.setStyleSheet("QLabel { font-size: 12px; padding-bottom: 10px;}")
        name_label.setAlignment(Qt.AlignHCenter)

        container_layout.addWidget(label)
        container_layout.addWidget(name_label)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignTop)

        container.setStyleSheet("padding-top: 10px;padding-left: 10px;padding-right: 10px;  background-color: transparent;")  # Set container background transparent

        return container, label

    def is_image_file(self, file_path):
        image_reader = QImageReader(file_path)
        return image_reader.canRead()

    def scrape_folder(self, folder_path):
        valid_labels = []  
        row = 0
        col = 0

        # Clearing grid_layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget)
            widget.deleteLater()

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            label = self.create_image_label(folder_path, file_path, filename, row, col)
            if self.apply_filters(label):
                valid_labels.append(label)  
                col += 1
                if col == 4:  
                    row += 1
                    col = 0
            else:
                pass



        for label in valid_labels:
            self.grid_layout.addWidget(label[0], label[1].row, label[1].col)
              
    def apply_filters(self, label):

        filaments_checked = self.filaments_checkbox.isChecked()
        fragments_checked = self.fragments_checkbox.isChecked()
        films_checked = self.films_checkbox.isChecked()

        min_length_str = self.length_min_input.text()
        max_length_str = self.length_max_input.text()
        min_width_str = self.width_min_input.text()
        max_width_str = self.width_max_input.text()

        min_length = float(min_length_str) if min_length_str else 0.0
        max_length = float(max_length_str) if max_length_str else float('inf')
        min_width = float(min_width_str) if min_width_str else 0.0
        max_width = float(max_width_str) if max_width_str else float('inf')

        data = get_image_data(label[1].folder_path, label[1].image_name)
        if data:
            length = float(data[0][2]) 
            width = float(data[0][3]) 

           
            if (filaments_checked and data[0][5] == 'filament') or (fragments_checked and data[0][5] == 'fragment') or (films_checked and data[0][5] == 'film'):
                if min_length <= max_length and min_width <= max_width:
                    if min_length <= length <= max_length and min_width <= width <= max_width:
                        return True
                    else:

                        return False
                else:
                    QMessageBox.warning(self, "Invalid Range", "Invalid length or width range.")
                    self.length_min_input.setText("") 
                    self.length_max_input.setText("") 
                    self.width_min_input.setText("") 
                    self.width_max_input.setText("") 
                    return False
            else:
                return False

        else:
            
            return False

        return True

    def on_filter_changed(self):
        self.scrape_folder(self.file_path)