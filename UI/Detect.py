import os
import sys 
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
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
from requestMP import DetectMP
from bbox import BoundingBox



class DetectUI(QDialog):
    close_signal = pyqtSignal()

    def __init__(self, port, parent=None):
        super().__init__(parent)
        self.port = port
        self.setWindowTitle("Images")
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        self.setFixedSize(1400, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        main_layout = QHBoxLayout(self)

        # Create the left-side widgets
        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.addStretch()

        change_dir_button = QPushButton("Choose Image")
        change_dir_button.setFixedSize(175,30)
        change_dir_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        detect_button = QPushButton("Detect")
        detect_button.setFixedSize(175,30)
        detect_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        close_button = QPushButton("Close")
        close_button.setFixedSize(175,30)
        close_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.image_pathway = None
        detect_button.clicked.connect(self.detect_mp)
        change_dir_button.clicked.connect(self.change_path)
        close_button.clicked.connect(self.closeUI)
        left_layout.addWidget(change_dir_button)
        left_layout.addWidget(detect_button)
        left_layout.addWidget(close_button)
        self.left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.left_widget.setMaximumWidth(int(self.width() * 0.2))  

        self.scroll_widget = QLabel()
        self.scroll_widget.setMinimumSize(1175,770)
        self.scroll_widget.setStyleSheet("background-color: white;")
        self.scroll_widget_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_widget_layout)
        self.scroll_widget_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.file_path = None
        main_layout.addWidget(self.scroll_widget)
        main_layout.addWidget(self.left_widget, stretch=0) 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(224, 224, 212, 255))
        painter.setBrush(brush)
        rect = self.rect()
        painter.drawRoundedRect(rect, 10, 10)

    def closeUI(self):
        self.close_signal.emit()
        self.close()

    def detect_mp(self):
        plot = DetectMP(self.file_path, self.port)
        new_image = BoundingBox(self.file_path, plot.get_json(), self.port)
        rgb_image = new_image.get_image()
        # Convert ndarray image to QImage
        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        qimage = QtGui.QImage(rgb_image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        qpixmap = QtGui.QPixmap.fromImage(qimage)
        self.scroll_widget.setPixmap(qpixmap)
        self.scroll_widget.setScaledContents(True)


        #pass self.file_path to detectron2 local
        #read JSON and 
        pass

    def on_filter_changed(self):
        self.scrape_folder(self.file_path)

    def change_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        new_db, _ = QFileDialog.getOpenFileName(self, "Select Photo", self.file_path, "JPG (*.jpg *.jpeg)", options=options)
        if new_db:
            self.file_path= new_db
            print(self.file_path)
            self.scroll_widget.setPixmap(QtGui.QPixmap(self.file_path))
            self.scroll_widget.setScaledContents(True)

def main():
    app = QApplication(sys.argv)
    stat_ui = DetectUI(1)
    stat_ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
