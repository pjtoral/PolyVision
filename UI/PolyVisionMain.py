import os
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
import cv2
import numpy as np
import serial
import serial.tools.list_ports
import time
from Statistics import StatisticsUI
from Images import ImagesUI
from NewFile import NewFileUI
from Database import *
from Capture import *
from Settings import SettingsUI
import json
from PIL import ImageEnhance
from SelfDestructingMessageBox import *
from GridOverlay import GridOverlay
from Detect import DetectUI
from GRBL import GrblUI


class Ui_MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.VideoCapture = VideoCapture()
        self.VideoCapture.start()
        self.VideoCapture.ImageUpdate.connect(self.ImageUpdateSlot)
        self.available_ports = list(serial.tools.list_ports.comports())
        self.comports = [f"{port.device} - {port.description.split(' (')[0].strip()}" for port in self.available_ports]
        self.ser = None
        self.blurThreshold = 8 
        self.measuring = False
        self.paused = False
        self.points = []
        self.distance = 0
        self.capturing = False
        with open("user_settings.json", "r") as f:
                settings_data = json.load(f)
        self.image_settings = settings_data.get("image_settings", {})

    
    #updating live feed in different Thread
    def ImageUpdateSlot(self, Image):
        if not self.paused:
            self.graphicsView.setPixmap(QPixmap.fromImage(Image))
            blurValue = self.calculateBlur(Image)

            if blurValue < self.blurThreshold:
                self.focusValue.setText("Blurry")
            else:
                self.focusValue.setText("Focused")
        else:
            pass

    #for calculating blur
    def calculateBlur(self, image):
        try:
            pilImage = Image.fromqimage(image)
            npImage = np.array(pilImage)
            grayImage = cv2.cvtColor(npImage, cv2.COLOR_BGR2GRAY)
            blurValue = cv2.Laplacian(grayImage, cv2.CV_64F).var()
            return blurValue
        except cv2.error as e:
            return 0

    #for canceling live feed (To add pa)
    def CancelFeed(self):
        self.ImageCapture.stop()

    #for capturing images
    def captureButtonClicked(self):
        self.frame = self.captureCurrentFrame()
        self.paused = True
        self.VideoCapture.ThreadActive = False
        self.capturing = True
        self.capture = CaptureUI()
        self.capture.length_clicked.connect(self.onLengthClicked)
        self.capture.width_clicked.connect(self.onWidthClicked)
        self.capture.save_clicked.connect(self.saving)
        self.capture.exec_() 
      
    def captureCurrentFrame(self):
        pixmap = self.graphicsView.pixmap()
        return pixmap.toImage()

    def saving(self):
        try:
            image = Image.fromqimage(self.frame)
            sized = image.resize((2560, 1440), Image.LANCZOS)
            sharpened = self.adjust_sharpness(sized, (self.imageSharpnes() / 100))
            saturated = self.adjust_saturation(sharpened, (self.imageSaturation() / 100))
            self.saveFrame(saturated)
        except Exception as e:
            print("Error occurred during image processing and saving:", e)

    def imageQuality(self):
        quality = self.image_settings.get("image_quality")
        if quality == "Low":
            return 10 
        elif quality  == "Medium":
            return 42 
        else:
            return 95

    def adjust_sharpness(self,image, factor):
        sharpener = ImageEnhance.Sharpness(image)
        return sharpener.enhance(1 + factor)

    def adjust_saturation(self,image, factor):
        saturater = ImageEnhance.Color(image)
        return saturater.enhance(1 + factor)

    def imageSharpnes(self):
        return self.image_settings.get("image_sharpness")

    def imageSaturation(self):
        return self.image_settings.get("image_saturation")

    def saveFrame(self, frame):
        self.VideoCapture.start()
        particle_name = self.capture.particle_name_edit.text()
        length = self.capture.length_edit.text()
        width= self.capture.width_edit.text()
        color= self.capture.color_edit.text()
        shape = self.capture.shape_edit.text()
        magnification = self.capture.magnification_edit.text()
        note = self.capture.note_edit.text()
        file_type = self.capture.photo_options_combo.currentText()
        frame_filename = f"{particle_name}.{file_type.upper()}" 
        save_folder = self.file_name  #path to folder
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        save_path = os.path.join(save_folder, frame_filename)
        frame.save(save_path, quality= self.imageQuality())
        insert_data(self.file_name, save_path,particle_name, length, width, color, shape, magnification, note)
        self.capture.close()
        self.capturing = False
        self.paused = False
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        msg_box = SelfDestructingMessageBox("Save", "\nSaving image and moving platform..", 7 , main_widget)
        msg_box.exec_()
        
    def onLengthClicked(self):
        self.lengthClicked = 1
        self.measureLength()

    def onWidthClicked(self):
        self.widthClicked = 1
        self.measureLength()

    #start-measuring
    def measureLength(self):
       if not self.measuring:
            if not self.capturing:
                self.frame = self.captureCurrentFrame()
            self.measureButton.setEnabled(True)
            self.measuring = True
            self.points = []
            self.measureButton.setText("Finish")
            QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
            self.graphicsView.mouseMoveEvent = self.mouseMoveEvent
            self.paused = True
            self.calibration = self.image_settings.get("calibration")

       else:
            self.stopMeasureLength()
            self.graphicsView.setPixmap(QPixmap.fromImage(self.frame))

    #stop-measuring
    def stopMeasureLength(self):
        self.measuring = False
        self.measureButton.setText("Measure")
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        self.paused = False
        self.lengthLabel.setVisible(False)
        if self.capturing :
            if self.lengthClicked == 1:
                self.capture.length_edit.setText(str(self.distance * self.calibration))
                self.lengthClicked = 0
            elif self.widthClicked == 1:
                self.capture.width_edit.setText(str(self.distance * self.calibration))
                self.widthClicked = 0
            self.capture.show()
        self.distance = 0 

    def mousePressEvent(self, event):
        if self.measuring and (event.button() == Qt.LeftButton):
            posGlobal = event.globalPos()
            pos = self.graphicsView.mapFromGlobal(posGlobal)
            self.points.append((pos.x(), pos.y()-40))
            self.currentPos = (pos.x(), pos.y()-40)
            pixmap = self.graphicsView.pixmap()
            qimage = pixmap.toImage()
            painter = QPainter(qimage)
            pen = QPen(Qt.gray)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawPoint(pos.x(),pos.y()-40)
            painter.end()
            self.graphicsView.setPixmap(QPixmap.fromImage(qimage))
            self.paintEvent()
        else:
            super().mousePressEvent(event)

    def paintEvent(self):
        if not self.paused:
            return
        pixmap = self.graphicsView.pixmap()
        if pixmap is None:
            return
        distance = []
        distanceLoc = 0
        qimage = pixmap.toImage()
        painter = QPainter(qimage)
        pen = QPen(QColor(211,211, 211), 1)
        pen.setDashPattern([2, 2, 2, 2])
        painter.setPen(pen)
        # Draw lines based on stored points
        for i in range(len(self.points) - 1):
            pt1 = self.points[i]
            pt2 = self.points[i + 1]
            painter.drawLine(pt1[0], pt1[1], pt2[0], pt2[1])
            self.lengthLabel.setGeometry(QtCore.QRect((pt2[0]+255), (pt2[1]+80), 50, 22))
            self.lengthLabel.setAlignment(Qt.AlignCenter)
            self.lengthLabel.setStyleSheet("background-color: rgba(255, 255, 255, 128);")
            self.lengthLabel.setVisible(True)
            distanceLoc = np.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)
            formatted_distance = "{:.2f}".format(distanceLoc)
        distance.append(distanceLoc)
        for i in range(len(distance)):
            self.distance = self.distance + distance[i]
        distanceShow = self.distance*self.calibration
        formatted_distance = "{:.2f}".format(distanceShow)
        self.lengthLabel.setText(str(formatted_distance))
        painter.end()
        pixmap = QPixmap.fromImage(qimage)
        self.graphicsView.setPixmap(pixmap)


    def mouseReleaseEvent(self, event):
        pass

    def goToDetect(self):
        self.paused = True
        self.detect = DetectUI()
        self.detect.close_signal.connect(self.setPausedFalse)
        self.detect.exec_()
        print("im here stats")

    def goToSettings(self):
        self.settings = SettingsUI()
        self.settings.apply_clicked.connect(self.set)
        self.settings.show()
        
    def goToCurrentImages(self):
        self.paused = True
        self.images = ImagesUI(self.file_name)
        self.images.exec_()
        if not self.images:
            self.setPausedFalse()

    def goToStatistics(self):
        self.paused = True
        self.statistics = StatisticsUI(self.file_name)
        self.statistics.close_signal.connect(self.setPausedFalse)
        self.statistics.exec_()
        print("im here stats")

    def setPausedFalse(self):
        print("im here")
        self.paused = False

    #accessing COM ports
    def serialConnect(self):
       
        if not self.ser:
            self.port = self.dropDown.currentText().split(" - ")[0] 
            print("Selected COM port:", self.port)
            try:
                self.ser = serial.Serial(self.port, baudrate=115200)
                time.sleep(2)
                print("Connected to GRBL")
                self.connectGRBL.setText("Disconnect")
                grbl = GrblUI()
                grbl.exec()
                #====== ADD AUTOMATION HERE=======#
            except serial.SerialException as e:
                print("Error opening serial port:", e)
                pass
        else:
            try:
                self.ser.close() 
                print("Disconnected from GRBL")
                self.connectGRBL.setText("Connect")  
                self.ser = None
            except serial.SerialException as e:
                print("Error closing serial port:", e)

    def moveUp(self):
        if self.ser:
            print("UP")
            self.gcode_command = b"G21 G91 G1 Y1 F100\r\n"
            self.ser.write(self.gcode_command)
        else:
            print("passed")

    def moveDown(self):
        if self.ser: 
            print("DOWN")
            self.gcode_command = b"G21 G91 G1 Y-1 F100\r\n"
            self.ser.write(self.gcode_command)
        else:
            pass

    def moveLeft(self):
        if self.ser:
            print("LEFT")
            self.gcode_command = b"G21 G91 G1 X-1 F100\r\n"
            self.ser.write(self.gcode_command)
        else:
            pass

    def moveRight(self):
        if self.ser:
            print("RIGHT")
            self.gcode_command = b"G21 G91 G1 X1 F100\r\n"
            self.ser.write(self.gcode_command)
        else:
            pass

    def moveHome(self):
        if self.ser:
            print("home")
            self.gcode_command = b"$H\r\n"
            self.ser.write(self.gcode_command)
        else:
            pass
        
    def closeEvent(self, event):
        self.videoCapture.stop()
        self.videoCapture.wait()
        event.accept()

    def set(self):
        if self.settings.grid_overlay_checkbox.isChecked():
            self.grid_overlay.setVisible(True)
        else:
            self.grid_overlay.setVisible(False)

    def refresh(self):
        self.available_ports = list(serial.tools.list_ports.comports())
        self.comports = [f"{port.device} - {port.description.split(' (')[0].strip()}" for port in self.available_ports]
        self.dropDown.addItems(self.comports)

    def on_new_action(self):
        new_file_widget = NewFileUI()
        if new_file_widget.exec_() == QtWidgets.QDialog.Accepted:
            self.file_name = new_file_widget.file_name_edit.text()
            location = new_file_widget.location_edit.text()
            sampling_date = new_file_widget.sampling_date_edit.text()
            self.placeValue.setText(self.file_name)        
            self.locationValue.setText(location)
            self.dateValue.setText(sampling_date)
            add_database_entry(self.file_name, f"{location}/microplastic.db", sampling_date)
            create_microplastics_database(self.file_name)
            self.paused = False
            self.statusValue.setText("Scanning...")
            self.detectionValue.setText("ON")
            self.captureButton.setEnabled(True)
            self.grblUP.setEnabled(True)
            self.grblUP.setEnabled(True)
            self.grblDOWN.setEnabled(True)
            self.grblLEFT.setEnabled(True)
            self.grblRIGHT.setEnabled(True)
            self.grblHOME.setEnabled(True)
            self.connectGRBL.setEnabled(True)
            self.imagesButton.setEnabled(True)
            self.detectButton.setEnabled(True)
            self.statisticsButton.setEnabled(True)
            self.measureButton.setEnabled(True)

    #defining pyQt5 widgets
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.showMaximized()
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")
        MainWindow.setWindowIcon(QIcon("res/PolyVisionLogo.png"))

        #instantiation of items
        self.centralwidget      =   QtWidgets.QWidget(MainWindow)
        self.progressBar        =   QtWidgets.QProgressBar(self.centralwidget)
        self.graphicsView       =   QtWidgets.QLabel(self.centralwidget)
        self.placeValue         =   QtWidgets.QLabel(self.centralwidget)
        self.locationLabel      =   QtWidgets.QLabel(self.centralwidget)
        self.locationValue      =   QtWidgets.QLabel(self.centralwidget)
        self.dataLabel          =   QtWidgets.QLabel(self.centralwidget)
        self.lengthLabel        =   QtWidgets.QLabel(self.centralwidget)
        self.dateValue          =   QtWidgets.QLabel(self.centralwidget)
        self.focusLabel         =   QtWidgets.QLabel(self.centralwidget)
        self.focusValue         =   QtWidgets.QLabel(self.centralwidget)
        self.statusLabel        =   QtWidgets.QLabel(self.centralwidget)
        self.statusValue        =   QtWidgets.QLabel(self.centralwidget)
        self.detectionLabel     =   QtWidgets.QLabel(self.centralwidget)
        self.detectionValue     =   QtWidgets.QLabel(self.centralwidget)
        self.progressLabel      =   QtWidgets.QLabel(self.centralwidget)
        self.grblTitle          =   QtWidgets.QLabel(self.centralwidget)
        self.highLabel          =   QtWidgets.QLabel(self.centralwidget)
        self.realTimeLabel      =   QtWidgets.QLabel(self.centralwidget)
        self.highLabel          =   QtWidgets.QLabel(self.centralwidget)
        self.moderateLabel      =   QtWidgets.QLabel(self.centralwidget)
        self.lowLabel           =   QtWidgets.QLabel(self.centralwidget)
        self.highValue          =   QtWidgets.QLabel(self.centralwidget)
        self.moderateValue      =   QtWidgets.QLabel(self.centralwidget)
        self.lowValue           =   QtWidgets.QLabel(self.centralwidget)
        self.classLabel         =   QtWidgets.QLabel(self.centralwidget)
        self.filamentLabel      =   QtWidgets.QLabel(self.centralwidget)  
        self.fragmentLabel      =   QtWidgets.QLabel(self.centralwidget)
        self.filmValue          =   QtWidgets.QLabel(self.centralwidget)
        self.fragmentValue      =   QtWidgets.QLabel(self.centralwidget)
        self.filmLabel          =   QtWidgets.QLabel(self.centralwidget)
        self.currentStatus      =   QtWidgets.QLabel(self.centralwidget)
        self.boxWidget          =   QtWidgets.QLabel(self.centralwidget)
        self.xWidget            =   QtWidgets.QLabel(self.centralwidget)
        self.zWidget            =   QtWidgets.QLabel(self.centralwidget)
        self.xLabel             =   QtWidgets.QLabel(self.centralwidget)
        self.xValue             =   QtWidgets.QLabel(self.centralwidget)
        self.yLabel             =   QtWidgets.QLabel(self.centralwidget)
        self.yValue             =   QtWidgets.QLabel(self.centralwidget)
        self.appTitle           =   QtWidgets.QLabel(self.centralwidget)
        self.dropDown           =   QtWidgets.QComboBox(self.centralwidget)
        self.grid_overlay       =   GridOverlay(self.centralwidget)
        self.appLogo            =   QtWidgets.QLabel(self.centralwidget)  
        self.filamentValue      =   QtWidgets.QLabel(self.centralwidget)     


        if self.image_settings.get("grid_overlay"):
            self.grid_overlay.setVisible(True)
        else:
            self.grid_overlay.setVisible(False)

        self.dropDown.addItems(self.comports)
        self.dropDown.setFocusPolicy(Qt.NoFocus)
        self.dropDown.activated.connect(self.refresh)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar.setProperty("value", 16)
        self.progressBar.setObjectName("progressBar")
        self.appLogo.setPixmap(QtGui.QPixmap("res/PolyVisionLogo.png"))
        self.appLogo.setScaledContents(True)

        
        #setting font for labels
        font = QtGui.QFont()
        font.setFamily("Nirmala UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.filmLabel.setFont(font)
        self.fragmentLabel.setFont(font)
        self.filamentLabel.setFont(font)
        self.lowLabel.setFont(font)
        self.highLabel.setFont(font)
        self.moderateLabel.setFont(font)
        self.dataLabel.setFont(font)
        self.focusLabel.setFont(font)
        self.statusLabel.setFont(font)
        self.detectionLabel.setFont(font)
        self.progressLabel.setFont(font)
        self.locationLabel.setFont(font)
        
        #setting font for values
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.locationValue.setFont(font)
        self.filamentValue.setFont(font)
        self.fragmentValue.setFont(font)
        self.filmValue.setFont(font)
        self.lowValue.setFont(font)
        self.moderateValue.setFont(font)
        self.highValue.setFont(font)
        self.dateValue.setFont(font)
        self.focusValue.setFont(font)
        self.statusValue.setFont(font)
        self.detectionValue.setFont(font)
        self.lengthLabel.setFont(font)
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.xLabel.setFont(font)
        self.yLabel.setFont(font)
        font.setPointSize(10)
        self.xValue.setFont(font)
        self.yValue.setFont(font)
        
        #seeting font for app Title
        font.setFamily("Gotham")
        font.setPointSize(14)
        font.setBold(True)
        self.appTitle.setFont(font)
        
        #setting font for section titles
        font.setPointSize(11)
        self.grblTitle.setFont(font)
        self.realTimeLabel.setFont(font)
        self.classLabel.setFont(font)
        self.currentStatus.setFont(font)
        
        #setting font size for folder name
        font.setPointSize(22)
        self.placeValue.setFont(font)
        
        #===============Capture Button for Images=========================#
        self.captureButton      = QtWidgets.QPushButton(self.centralwidget) 
        self.measureButton      = QtWidgets.QPushButton(self.centralwidget)        
        self.detectButton       = QtWidgets.QPushButton(self.centralwidget)
        self.imagesButton       = QtWidgets.QPushButton(self.centralwidget)
        self.statisticsButton   = QtWidgets.QPushButton(self.centralwidget)
        self.settingsButton     = QtWidgets.QPushButton(self.centralwidget) 
        self.grblUP             = QtWidgets.QPushButton(self.centralwidget) 
        self.grblDOWN           = QtWidgets.QPushButton(self.centralwidget) 
        self.grblLEFT           = QtWidgets.QPushButton(self.centralwidget) 
        self.grblRIGHT          = QtWidgets.QPushButton(self.centralwidget) 
        self.grblHOME           = QtWidgets.QPushButton(self.centralwidget)
        self.connectGRBL        = QtWidgets.QPushButton(self.centralwidget)


  
        #==================Stylesheets======================#
        #self.graphicsView.setStyleSheet("background-color: rgb(255,255,255);") #White
        self.graphicsView.setStyleSheet("background-color: rgb(0,0,0);") #Black
        self.filmLabel.setStyleSheet("color:#fbbf16;")
        self.fragmentLabel.setStyleSheet("color:#fbbf16;")
        self.filamentLabel.setStyleSheet("color:#fbbf16;")
        self.lowLabel.setStyleSheet("color:#fbbf16;")
        self.moderateLabel.setStyleSheet("color:#fbbf16;")
        self.highLabel.setStyleSheet("color:#fbbf16;")
        self.progressLabel.setStyleSheet("color:#fbbf16;")
        self.detectionLabel.setStyleSheet("color:#fbbf16;")
        self.statusLabel.setStyleSheet("color:#fbbf16;")
        self.locationLabel.setStyleSheet("color:#fbbf16;")
        self.dataLabel.setStyleSheet("color:#fbbf16;")
        self.focusLabel.setStyleSheet("color:#fbbf16;")
        self.captureButton.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.measureButton.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.detectButton.setStyleSheet("QPushButton {\n""background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 133, 63, 255), stop:0.909091 rgba(255, 255, 255, 167));\n""    color: #000000;\n""    font: bold 16px;\n""    border-radius: 0px;\n""    border-color: #FFFFFF;\n""}\n""QPushButton:hover {\n""   \n""    color: #FFFFFF;\n""}\n""")
        self.imagesButton.setStyleSheet("QPushButton {\n""    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 133, 63, 255), stop:0.909091 rgba(255, 255, 255, 167));\n""    color: #000000;\n""    font: bold 16px;\n""    border-radius: 0px;\n""    border-color: #FFFFFF;\n""}\n""QPushButton:hover {\n""   \n""    color: #FFFFFF;\n""}\n""")
        self.statisticsButton.setStyleSheet("QPushButton {\n""    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 133, 63, 255), stop:0.909091 rgba(255, 255, 255, 167));\n""    color: #000000;\n""    font: bold 16px;\n""    border-radius: 0px;\n""    border-color: #FFFFFF;\n""}\n""QPushButton:hover {\n""   \n""    color: #FFFFFF;\n""}\n""")          
        self.settingsButton.setStyleSheet("QPushButton {\n""    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 133, 63, 255), stop:0.909091 rgba(255, 255, 255, 167));\n""    color: #000000;\n""    font: bold 16px;\n""    border-radius: 0px;\n""    border-color: #FFFFFF;\n""}\n""QPushButton:hover {\n""   \n""    color: #FFFFFF;\n""}\n""")
        self.dropDown.setStyleSheet(''' QComboBox {border: 1px solid #ccc;border-radius: 5px;padding: 1px;background-color: #ffffff;color: #000000;font-size: 12px;}QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width: 20px;}''')
        self.grblUP.setStyleSheet(u"QPushButton {\n""       background-color: qconicalgradient(cx:0.5, cy:0, angle:90.9, stop:0 rgba(255, 255, 255, 255), stop:0.37223 rgba(255, 255, 255, 255), stop:0.373991 rgba(251, 191, 22, 255), stop:0.62362 rgba(253, 202, 22, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""     background-color: qconicalgradient(cx:0.5, cy:0, angle:90.9, stop:0 rgba(255, 255, 255, 255), stop:0.37223 rgba(255, 255, 255, 255), stop:0.373991 rgba(158, 120, 14, 255), stop:0.62362 rgba(158, 120, 14, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""}")
        self.grblDOWN.setStyleSheet(u"QPushButton {\n""    background-color: qconicalgradient(cx:0.494318, cy:1, angle:270, stop:0 rgba(255, 255, 255, 255), stop:0.373989 rgba(255, 255, 255, 255), stop:0.373991 rgba(252, 191, 22, 255), stop:0.623986 rgba(252, 191, 22, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: qconicalgradient(cx:0.494318, cy:1, angle:270, stop:0 rgba(255, 255, 255, 255), stop:0.37223 rgba(255, 255, 255, 255), stop:0.373991 rgba(158, 120, 14, 255), stop:0.62362 rgba(158, 120, 14, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""}")
        self.grblLEFT.setStyleSheet(u"QPushButton {\n""     background-color: qconicalgradient(cx:0, cy:0.499, angle:180.1, stop:0 rgba(255, 255, 255, 255), stop:0.375488 rgba(255, 255, 255, 255), stop:0.375911 rgba(252, 191, 22, 255), stop:0.622911 rgba(251, 191, 22, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: qconicalgradient(cx:0, cy:0.499, angle:180.1, stop:0 rgba(255, 255, 255, 255), stop:0.37548 rgba(255, 255, 255, 255), stop:0.375626 rgba(158, 120, 14, 255), stop:0.622911 rgba(158, 120, 14, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""}")
        self.grblRIGHT.setStyleSheet(u"QPushButton {\n""    background-color: qconicalgradient(cx:1, cy:0.499, angle:0.110478, stop:0 rgba(255, 255, 255, 255), stop:0.373989 rgba(255, 255, 255, 255), stop:0.373991 rgba(252, 191, 22, 255), stop:0.623986 rgba(252, 191, 22, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: qconicalgradient(cx:1, cy:0.499, angle:0.110478, stop:0 rgba(255, 255, 255, 255), stop:0.373989 rgba(255, 255, 255, 255), stop:0.373991 rgba(252, 191, 22, 255), stop:0.374003 rgba(158, 120, 14, 255), stop:0.623986 rgba(158, 120, 14, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""}")
        self.grblHOME.setStyleSheet(u"QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 10px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.boxWidget.setStyleSheet(u"\n""border: 2px solid #d3d3d3;\n""border-radius: 10px;\n" "background-color: transparent;\n")
        self.xWidget.setStyleSheet(u"\n""border: 1px solid #d3d3d3;\n""border-radius: 10px;\n" "background-color: transparent;\n")
        self.zWidget.setStyleSheet(u"\n""border: 1px solid #d3d3d3;\n""border-radius: 10px;\n" "background-color: transparent;\n")
        self.connectGRBL.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        
        #======================BUTTON ACTIONS===========================#
        self.captureButton.clicked.connect(self.captureButtonClicked)
        self.detectButton.clicked.connect(self.goToDetect)
        self.grblUP.clicked.connect(self.moveUp)
        self.grblDOWN.clicked.connect(self.moveDown)
        self.grblLEFT.clicked.connect(self.moveLeft)
        self.grblRIGHT.clicked.connect(self.moveRight)
        self.grblHOME.clicked.connect(self.moveHome)
        self.statisticsButton.clicked.connect(self.goToStatistics)
        self.settingsButton.clicked.connect(self.goToSettings)
        self.imagesButton.clicked.connect(self.goToCurrentImages)
        self.measureButton.clicked.connect(self.measureLength)
        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.connectGRBL.clicked.connect(self.serialConnect)
        #======================APP&LOGOS COORDNT========================#
        self.appTitle       .setGeometry(QtCore.QRect(100, 70, 140,40))
        self.appLogo         .setGeometry(QtCore.QRect(30, 60, 60, 50))
        #=====================MAIN VIEW COORDINATES=====================#
        self.progressLabel   .setGeometry(QtCore.QRect(290, 880, 80, 30))
        self.progressBar     .setGeometry(QtCore.QRect(380, 890, 1200, 20))
        self.graphicsView    .setGeometry(QtCore.QRect(290, 70, 1280, 800))
        self.grid_overlay    .setGeometry(QtCore.QRect(00, 70,1780, 800))
        #======================LOC. COORDINATES=========================#
        self.placeValue      .setGeometry(QtCore.QRect(1595, 60, 320, 50))
        self.locationLabel   .setGeometry(QtCore.QRect(1595, 110, 130, 30))
        self.locationValue   .setGeometry(QtCore.QRect(1745, 110, 200, 30))
        self.dataLabel       .setGeometry(QtCore.QRect(1595, 140, 130, 30))
        self.dateValue       .setGeometry(QtCore.QRect(1745, 140, 200, 30))
        #====================REPORT COORDINATES=========================#
        self.realTimeLabel   .setGeometry(QtCore.QRect(1595, 180, 175, 30))
        self.highLabel       .setGeometry(QtCore.QRect(1595, 210, 45, 30))
        self.highValue       .setGeometry(QtCore.QRect(1745, 210, 50, 30))
        self.moderateLabel   .setGeometry(QtCore.QRect(1595, 240, 90, 30))
        self.moderateValue   .setGeometry(QtCore.QRect(1745, 240, 50, 30))
        self.lowLabel        .setGeometry(QtCore.QRect(1595, 270, 40, 30))
        self.lowValue        .setGeometry(QtCore.QRect(1745, 270, 50, 30))
        #====================CLASSES COORDINATES=========================#
        self.classLabel      .setGeometry(QtCore.QRect(1595, 310, 150, 30))
        self.filamentLabel   .setGeometry(QtCore.QRect(1595, 340, 95, 30))
        self.filamentValue   .setGeometry(QtCore.QRect(1745, 340, 50, 30))
        self.fragmentLabel   .setGeometry(QtCore.QRect(1595, 370, 95, 30))
        self.fragmentValue   .setGeometry(QtCore.QRect(1745, 370, 50, 30))
        self.filmLabel       .setGeometry(QtCore.QRect(1595, 400, 50, 30))
        self.filmValue       .setGeometry(QtCore.QRect(1745, 400, 50, 30))
        #====================STATUS COORDINATES=========================#
        self.currentStatus   .setGeometry (QtCore.QRect(1595,440, 175,30))
        self.focusLabel      .setGeometry(QtCore.QRect(1595, 470, 50, 30))
        self.focusValue      .setGeometry(QtCore.QRect(1745, 470, 100, 30))
        self.statusLabel     .setGeometry(QtCore.QRect(1595, 500, 60, 30))
        self.statusValue     .setGeometry(QtCore.QRect(1745, 500, 100, 30))
        self.detectionLabel  .setGeometry(QtCore.QRect(1595, 530, 135, 30))
        self.detectionValue  .setGeometry(QtCore.QRect(1745, 530, 100, 30))
        #====================PICTURE COORDINATES=========================#
        self.captureButton   .setGeometry(QtCore.QRect(1600, 570, 140, 50))
        self.measureButton   .setGeometry(QtCore.QRect(1750, 570, 140, 50))
        #======================GRBL COORDINATES=========================#
        self.boxWidget       .setGeometry(QtCore.QRect(1595, 640, 300, 220))
        self.xWidget         .setGeometry(QtCore.QRect(1765, 690, 115, 150))
        self.zWidget         .setGeometry(QtCore.QRect(1610, 690, 150, 150))
        self.grblTitle       .setGeometry(QtCore.QRect(1660, 650, 180, 30))
        self.grblUP          .setGeometry(QtCore.QRect(1665, 695, 43, 43))
        self.grblDOWN        .setGeometry(QtCore.QRect(1665, 790, 43, 43))
        self.grblLEFT        .setGeometry(QtCore.QRect(1617, 743, 43, 43))
        self.grblRIGHT       .setGeometry(QtCore.QRect(1713, 743, 43, 43))
        self.grblHOME        .setGeometry(QtCore.QRect(1665, 743, 43, 43))
        self.xLabel          .setGeometry(QtCore.QRect(1777, 703, 45, 20))
        self.xValue          .setGeometry(QtCore.QRect(1807, 703, 70, 20))
        self.yLabel          .setGeometry(QtCore.QRect(1777, 727, 45, 20))
        self.yValue          .setGeometry(QtCore.QRect(1807, 727, 70, 20))
        self.dropDown        .setGeometry(QtCore.QRect(1773, 755, 100,30))
        #====================SETTINGS COORDINATES=========================#
        self.detectButton    .setGeometry(QtCore.QRect(0, 170, 261, 41))
        self.imagesButton    .setGeometry(QtCore.QRect(0, 260, 261, 41))
        self.statisticsButton.setGeometry(QtCore.QRect(0, 350, 261, 41))
        self.settingsButton  .setGeometry(QtCore.QRect(0, 440, 261, 41))
        self.connectGRBL     .setGeometry(QtCore.QRect(1773, 795, 100,30))
        #====================menuBar============================#


        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1253, 21))
        self.menubar.setStyleSheet("background-color: rgb(245, 245, 245);")
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setStyleSheet("selection-background-color: rgb(154, 231, 231);\n""selection-color: rgb(0, 0, 0);")
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setStyleSheet("selection-background-color: rgb(154, 231, 231);\n""selection-color: rgb(0, 0, 0);")
        self.menuEdit.setObjectName("menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionUndo = QtWidgets.QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtWidgets.QAction(MainWindow)
        self.actionRedo.setObjectName("actionRedo")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setObjectName("actionPaste")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PlastiScan"))

        #==============Setting Label Texts=======================#
        self.locationLabel.setText(_translate("MainWindow", "Location:"))
        self.dataLabel.setText(_translate("MainWindow", "Date Sampled:"))
        self.focusLabel.setText(_translate("MainWindow", "Focus:"))
        self.statusLabel.setText(_translate("MainWindow", "Status:"))
        self.detectionLabel.setText(_translate("MainWindow", "Auto Detection:"))
        self.progressLabel.setText(_translate("MainWindow", "Progress:"))
        self.realTimeLabel.setText(_translate("MainWindow", "Real-Time Report"))
        self.currentStatus.setText(_translate("MainWindow", "Current Status"))
        self.grblTitle.setText(_translate("MainWindow", "Platform Coordinates"))
        self.highLabel.setText(_translate("MainWindow", "High:"))
        self.moderateLabel.setText(_translate("MainWindow", "Moderate:"))
        self.lowLabel.setText(_translate("MainWindow", "Low:"))
        self.classLabel.setText(_translate("MainWindow", "Likely Classes"))
        self.filamentLabel.setText(_translate("MainWindow", "Filaments:"))
        self.fragmentLabel.setText(_translate("MainWindow", "Fragments:"))
        self.filmLabel.setText(_translate("MainWindow", "Films:"))
        self.appTitle.setText(_translate("MainWindow", "PlastiScan"))
        self.captureButton.setText(_translate("MainWindow", "Capture"))
        self.measureButton.setText(_translate("MainWindow", "Measure"))
        self.grblUP.setText(_translate("MainWindow", "↑"))
        self.grblUP.setShortcut("Up")
        self.grblDOWN.setText(_translate("MainWindow", "↓"))
        self.grblDOWN.setShortcut("Down")
        self.grblLEFT.setText(_translate("MainWindow", "←"))
        self.grblLEFT.setShortcut("Left")
        self.grblRIGHT.setText(_translate("MainWindow", "→"))
        self.grblRIGHT.setShortcut("Right")
        self.grblHOME.setText(_translate("MainWindow", "HOME"))
        self.detectButton.setText(_translate("MainWindow", "Detect"))
        self.imagesButton.setText(_translate("MainWindow", "Images"))
        self.statisticsButton.setText(_translate("MainWindow", "Statistics"))
        self.settingsButton.setText(_translate("MainWindow", "Settings"))
        self.xLabel.setText(_translate("MainWindow","X  :"))
        self.xValue.setText(_translate("MainWindow","1000.00"))
        self.yLabel.setText(_translate("MainWindow","Y  :"))
        self.yValue.setText(_translate("MainWindow","1000.00"))
        self.connectGRBL.setText(_translate("MainWindow","Connect"))


        #Menu Bar
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setStatusTip(_translate("MainWindow", "Save current file"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As"))
        self.actionSave_As.setStatusTip(_translate("MainWindow", "Save a file as..."))
        self.actionSave_As.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionUndo.setText(_translate("MainWindow", "Undo"))
        self.actionUndo.setStatusTip(_translate("MainWindow", "Undo edits"))
        self.actionUndo.setShortcut(_translate("MainWindow", "Ctrl+Z"))
        self.actionRedo.setText(_translate("MainWindow", "Redo"))
        self.actionRedo.setStatusTip(_translate("MainWindow", "Redo edit"))
        self.actionRedo.setShortcut(_translate("MainWindow", "Ctrl+Shift+Z"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionCopy.setStatusTip(_translate("MainWindow", "Copy a file"))
        self.actionCopy.setShortcut(_translate("MainWindow", "Ctrl+C"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionPaste.setStatusTip(_translate("MainWindow", "Paste a file"))
        self.actionPaste.setShortcut(_translate("MainWindow", "Ctrl+V"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionNew.setStatusTip(_translate("MainWindow", "Create New file"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))

        #===========Menu Bar Actions=============#
        self.actionNew.triggered.connect(self.on_new_action)


        self.captureButton.setEnabled(False)
        self.measureButton.setEnabled(False)
        self.grblUP.setEnabled(False)
        self.grblUP.setEnabled(False)
        self.grblDOWN.setEnabled(False)
        self.grblLEFT.setEnabled(False)
        self.grblRIGHT.setEnabled(False)
        self.grblHOME.setEnabled(False)
        self.connectGRBL.setEnabled(False)
        self.imagesButton.setEnabled(False)
        self.detectButton.setEnabled(False)
        self.statisticsButton.setEnabled(False)


class VideoCapture(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        self.capture = cv2.VideoCapture(0) #this is default camera
        # self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  
        # self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  
        # self.capture.set(cv2.CAP_PROP_FPS, 2)
        # self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 100)
        frame_count = 0
        while self.ThreadActive:
            ret, frame = self.capture.read()
            frame_count += 1
            if frame_count % 5 == 0:
                if ret:
                    # FlippedImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                    # #changing aspect ratio and scaling feed (keep this in mind for resolution of MP 1280, 720 gives HD 
                    # self.ImageUpdate.emit(ConvertToQtFormat)
                    Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    FlippedImage = cv2.flip(Image, 1)
                    ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                    Pic = ConvertToQtFormat.scaled(1280, 720, Qt.KeepAspectRatio)
                    self.ImageUpdate.emit(Pic)
                

    def stop(self):
        self.ThreadActive = False
        self.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setQuitOnLastWindowClosed(False)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
