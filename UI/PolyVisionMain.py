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
from Settings import SettingsUI
from Images import ImagesUI
from NewFile import NewFileUI
from Database import *
from Capture import *



class Ui_MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.VideoCapture = VideoCapture()
        self.VideoCapture.start() #creating a simultaneous thread 
        self.VideoCapture.ImageUpdate.connect(self.ImageUpdateSlot)
        self.available_ports = list(serial.tools.list_ports.comports())
        self.comports = [f"{port.device} - {port.description.split(' (')[0].strip()}" for port in self.available_ports]
        self.ser = None
        self.blurThreshold = 8 
        self.measuring = False
        self.paused = True
        self.points = []
        self.distance = 0


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
        self.capture = CaptureUI()
        self.capture.length_clicked.connect(self.onLengthClicked)
        self.capture.width_clicked.connect(self.onWidthClicked)
        self.capture.save_clicked.connect(self.saving)
        self.capture.exec_() 


    def captureCurrentFrame(self):
        # Get the current frame from the graphics view
        pixmap = self.graphicsView.pixmap()
        return pixmap.toImage()

    def saving(self):
        self.saveFrame(self.frame)


    def saveFrame(self, frame):
        particle_name = self.capture.particle_name_edit.text()
        length = self.capture.length_edit.text()
        width= self.capture.width_edit.text()
        color= self.capture.color_edit.text()
        shape = self.capture.shape_edit.text()
        magnification = self.capture.magnification_edit.text()
        note = self.capture.note_edit.text()

        
        file_type = self.capture.photo_options_combo.currentText()
        frame_filename = f"{particle_name}.{file_type.upper()}" 
        print(file_type)
        save_folder = self.file_name  #path to folder
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        save_path = os.path.join(save_folder, frame_filename)
        self.frame.save(save_path)
        insert_data(self.file_name, save_path,particle_name, length, width, color, shape, magnification, note)
        self.capture.close()
        self.paused = False

    def onLengthClicked(self):
        self.lengthClicked = 1
        self.measureLength()


    def onWidthClicked(self):
        self.widthClicked = 1
        self.measureLength()


    #start-measuring
    def measureLength(self):
       if not self.measuring:
            self.measuring = True
            self.points = []
            self.measureButton.setText("Finish")
            QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
            self.graphicsView.mouseMoveEvent = self.mouseMoveEvent
            self.paused = True
       else:
            self.stopMeasureLength()
            self.graphicsView.setPixmap(QPixmap.fromImage(self.frame))


    #stop-measuring
    def stopMeasureLength(self):
        print("Stop measurement called")
        self.measuring = False
        self.measureButton.setText("Measure")
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        #self.paused = False
        self.lengthLabel.setVisible(False)
        print('Total Distance:',self.distance, 'pixels')
        print('Total Distance:',self.distance*0.0084, 'milimeters')
        if self.lengthClicked == 1:
            self.capture.length_edit.setText(str(self.distance * 0.0084))
            self.lengthClicked = 0
        elif self.widthClicked == 1:
            self.capture.width_edit.setText(str(self.distance * 0.0084))
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
            print('Current Distance:', formatted_distance, 'pixels')
        print('Outside:', distanceLoc, 'pixels')
        distance.append(distanceLoc)
        for i in range(len(distance)):
            self.distance = self.distance + distance[i]
        distanceShow = self.distance*0.0084
        formatted_distance = "{:.2f}".format(distanceShow)
        self.lengthLabel.setText(str(formatted_distance))
        painter.end()
        pixmap = QPixmap.fromImage(qimage)
        self.graphicsView.setPixmap(pixmap)


    #accessing COM ports
    def serialConnect(self):
        self.port = self.dropDown.currentText().split(" - ")[0]  # Extract the COM port
        print("Selected COM port:", self.port)
        try:
            self.ser = serial.Serial(self.port, baudrate=115200)
            time.sleep(2)
            print("Connected to GRBL")
        except serial.SerialException as e:
            print("Error opening serial port:", e)

    def mouseReleaseEvent(self, event):
        pass

    def goToSettings(self):
        self.settings = SettingsUI()
        self.settings.show()

    def goToCurrentImages(self):
        print(self.file_name)
        self.images = ImagesUI(self.file_name)
        self.images.show()


    def moveUp(self):
        if self.ser:
            self.gcode_command = b"G21 G91 G1 Y10 F1000\r\n"
            self.ser.write(self.gcode_command)
        else:
            pass

    def moveDown(self):
        if self.ser: 
            self.gcode_command = b"G21 G91 G1 Y-10 F1000\r\n"
            self.ser.write(self.gcode_command)
        else:
            pass

    def moveLeft(self):
        if self.ser:
            self.gcode_command = b"G21 G91 G1 X10 F1000\r\n"
            self.ser.write(self.gcode_command)
        else:
            pass

    def moveRight(self):
        if self.ser:
            self.gcode_command = b"G21 G91 G1 X-10 F1000\r\n"
            self.ser.write(self.gcode_command)
        else:
            pass
        
    def closeEvent(self, event):
        self.videoCapture.stop()
        self.videoCapture.wait()
        event.accept()

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
        




    #defining pyQt5 widgets
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.showMaximized()
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")
        MainWindow.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        #instantiation of items
        self.centralwidget      =   QtWidgets.QWidget(MainWindow)
        self.progressBar        =   QtWidgets.QProgressBar(self.centralwidget) #for progress
        self.graphicsView       =   QtWidgets.QLabel(self.centralwidget) #for camera view
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
        #self.yWidget            =   QtWidgets.QLabel(self.centralwidget)
        self.zWidget            =   QtWidgets.QLabel(self.centralwidget)
        self.xLabel             =   QtWidgets.QLabel(self.centralwidget)
        self.xValue             =   QtWidgets.QLabel(self.centralwidget)
        self.yLabel             =   QtWidgets.QLabel(self.centralwidget)
        self.yValue             =   QtWidgets.QLabel(self.centralwidget)
        self.applTitle          =   QtWidgets.QLabel(self.centralwidget)
        self.dropDown           =   QtWidgets.QComboBox(self.centralwidget)

        self.dropDown.addItems(self.comports)
        self.dropDown.setFocusPolicy(Qt.NoFocus)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar.setProperty("value", 16)
        self.progressBar.setObjectName("progressBar")
        
        #this is for the OpenCV Video
        self.graphicsView.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.graphicsView.setObjectName("graphicsView")
        self.currentStatus.setObjectName("currentStatus")
        self.placeValue.setObjectName("placeValue")
        self.locationLabel.setStyleSheet("color:#fbbf16;")
        self.locationLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.locationLabel.setObjectName("locationLabel")
        self.locationValue.setStyleSheet("")
        self.locationValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.locationValue.setObjectName("locationValue")
        self.dataLabel.setStyleSheet("color:#fbbf16;")
        self.dataLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.dataLabel.setObjectName("dataLabel")
        self.dateValue.setStyleSheet("")
        self.dateValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.dateValue.setObjectName("dateValue")
        self.focusLabel.setStyleSheet("color:#fbbf16;")
        self.focusLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.focusLabel.setObjectName("focusLabel")
        self.focusValue.setStyleSheet("")
        self.focusValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.focusValue.setObjectName("focusValue")
        self.statusLabel.setStyleSheet("color:#fbbf16;")
        self.statusLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.statusLabel.setObjectName("statusLabel")
        self.statusValue.setStyleSheet("")
        self.statusValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.statusValue.setObjectName("statusValue")
        self.detectionLabel.setStyleSheet("color:#fbbf16;")
        self.detectionLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.detectionLabel.setObjectName("detectionLabel")
        self.detectionValue.setStyleSheet("")
        self.detectionValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.detectionValue.setObjectName("detectionValue")
        self.progressLabel.setStyleSheet("color:#fbbf16;")
        self.progressLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.progressLabel.setObjectName("progressLabel")
        self.grblTitle.setObjectName("grblTitle")
        self.realTimeLabel.setObjectName("realTimeLabel")
        self.highLabel.setStyleSheet("color:#fbbf16;")
        self.highLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.highLabel.setObjectName("highLabel")
        self.moderateLabel.setStyleSheet("color:#fbbf16;")
        self.moderateLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.moderateLabel.setObjectName("moderateLabel")
        self.lowLabel.setStyleSheet("color:#fbbf16;")
        self.lowLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lowLabel.setObjectName("lowLabel")
        self.highValue.setStyleSheet("")
        self.highValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.highValue.setObjectName("highValue")
        self.moderateValue.setStyleSheet("")
        self.moderateValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.moderateValue.setObjectName("moderateValue")
        self.lowValue.setStyleSheet("")
        self.lowValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lowValue.setObjectName("lowValue")
        self.classLabel.setObjectName("classLabel")
        self.filamentLabel.setStyleSheet("color:#fbbf16;")
        self.filamentLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.filamentLabel.setObjectName("filamentLabel")
        self.fragmentLabel.setStyleSheet("color:#fbbf16;")
        self.fragmentLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.fragmentLabel.setObjectName("fragmentLabel")
        self.filmValue.setStyleSheet("")
        self.filmValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.filmValue.setObjectName("filmValue")
        self.fragmentValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.fragmentValue.setObjectName("fragmentValue")
        self.filmLabel.setStyleSheet("color:#fbbf16;")
        self.filmLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.filmLabel.setObjectName("filmLabel")    
        self.applTitle.setObjectName("applTitle")
        self.appLogo = QtWidgets.QLabel(self.centralwidget)    
        self.appLogo.setPixmap(QtGui.QPixmap("res/PolyVisionLogo.png"))
        self.appLogo.setScaledContents(True)
        self.appLogo.setObjectName("appLogo")
        self.filamentValue = QtWidgets.QLabel(self.centralwidget)    
        self.filamentValue.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.filamentValue.setObjectName("filamentValue")
        
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
        font.setFamily("Segoe UI Historic")
        font.setPointSize(18)
        self.applTitle.setFont(font)
        
        #setting font for section titles
        font.setPointSize(11)
        self.grblTitle.setFont(font)
        self.realTimeLabel.setFont(font)
        self.classLabel.setFont(font)
        self.currentStatus.setFont(font)
        
        #setting font size for folder name
        font.setPointSize(22)
        self.placeValue.setFont(font)
        
        #Capture Button for Images
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

        self.captureButton.setObjectName("captureButton")
        self.measureButton.setObjectName("measureButton")
        self.grblUP.setObjectName("grblUP")
        self.grblDOWN.setObjectName("grblDOWN")
        self.grblLEFT.setObjectName("grblLEFT")
        self.grblRIGHT.setObjectName("grblRIGHT")
        self.grblHOME.setObjectName("grblHOME")
        self.detectButton.setObjectName("detectButton")
        self.imagesButton.setObjectName("imagesButton")
        self.statisticsButton.setObjectName("statisticsButton")
        self.settingsButton.setObjectName("settingsButton")
        self.connectGRBL.setObjectName("connectGRBL")
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
        #self.yWidget.setStyleSheet(u"\n""border: 1px solid #d3d3d3;\n""border-radius: 10px;\n" "background-color: transparent;\n")
        self.zWidget.setStyleSheet(u"\n""border: 1px solid #d3d3d3;\n""border-radius: 10px;\n" "background-color: transparent;\n")
        self.connectGRBL.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        #======================BUTTON ACTIONS===========================#
        self.captureButton.clicked.connect(self.captureButtonClicked)
        self.grblUP.clicked.connect(self.moveUp)
        self.grblDOWN.clicked.connect(self.moveDown)
        self.grblLEFT.clicked.connect(self.moveLeft)
        self.grblRIGHT.clicked.connect(self.moveRight)
        #self.statisticsButton.clicked.connect(self.goToStatistics)
        self.settingsButton.clicked.connect(self.goToSettings)
        self.imagesButton.clicked.connect(self.goToCurrentImages)
        self.measureButton.clicked.connect(self.measureLength)
        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.connectGRBL.clicked.connect(self.serialConnect)
        #======================APP&LOGOS COORDNT========================#
        self.applTitle       .setGeometry(QtCore.QRect(100, 70, 140, 30))
        self.appLogo         .setGeometry(QtCore.QRect(30, 60, 60, 50))
        #=====================MAIN VIEW COORDINATES=====================#
        self.progressLabel   .setGeometry(QtCore.QRect(290, 880, 80, 30))
        self.progressBar     .setGeometry(QtCore.QRect(380, 890, 1200, 20))
        self.graphicsView    .setGeometry(QtCore.QRect(290, 70, 1280, 800))
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
        #self.yWidget         .setGeometry(QtCore.QRect(1765, 767, 115, 72))
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
        MainWindow.setWindowTitle(_translate("MainWindow", "PolyVision"))

        #Labels
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
        self.applTitle.setText(_translate("MainWindow", "PolyVision"))
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
        Capture = cv2.VideoCapture(0) #this is default camera
        #Capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set the width to 1280 pixels
        #Capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Set the height to 720 pixels
        #Capture.set(cv2.CAP_PROP_FPS, 30)
        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                FlippedImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #FlippedImage = cv2.flip(Image, 0)
                #FlippedImage = cv2.flip(FlippedImage, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                #changing aspect ratio and scaling feed (keep this in mind for resolution of MP 1280, 720 gives HD )
                ImageScaled = ConvertToQtFormat.scaled(1280,720, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(ImageScaled)
    def stop(self):
        self.ThreadActive = False
        self.quit()

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(1000,800)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        
         # Set the background color for the window
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor("#FFFFFF"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        main_layout = QVBoxLayout()
        # Image Acquisition Settings
        image_acquisition_group = QGroupBox("Image Acquisition Settings")
        image_acquisition_layout = QVBoxLayout()

        exposure_label = QLabel("Exposure Time:")
        exposure_spinbox = QSpinBox()
        exposure_spinbox.setRange(1, 1000)
        image_acquisition_layout.addWidget(exposure_label)
        image_acquisition_layout.addWidget(exposure_spinbox)

        resolution_label = QLabel("Resolution:")
        resolution_spinbox = QSpinBox()
        resolution_spinbox.setRange(1, 10000)
        image_acquisition_layout.addWidget(resolution_label)
        image_acquisition_layout.addWidget(resolution_spinbox)

        image_acquisition_group.setLayout(image_acquisition_layout)
        main_layout.addWidget(image_acquisition_group)

        # GRBL Controller Settings
        grbl_controller_group = QGroupBox("GRBL Controller Settings")
        grbl_controller_layout = QVBoxLayout()

        steps_label = QLabel("Steps per Unit:")
        steps_spinbox = QSpinBox()
        steps_spinbox.setRange(1, 1000)
        grbl_controller_layout.addWidget(steps_label)
        grbl_controller_layout.addWidget(steps_spinbox)

        feed_rate_label = QLabel("Maximum Feed Rate:")
        feed_rate_spinbox = QSpinBox()
        feed_rate_spinbox.setRange(1, 1000)
        grbl_controller_layout.addWidget(feed_rate_label)
        grbl_controller_layout.addWidget(feed_rate_spinbox)

        grbl_controller_group.setLayout(grbl_controller_layout)
        main_layout.addWidget(grbl_controller_group)

        # Microplastics Detection Settings
        microplastics_detection_group = QGroupBox("Microplastics Detection Settings")
        microplastics_detection_layout = QVBoxLayout()

        threshold_label = QLabel("Detection Threshold:")
        threshold_slider = QSlider(Qt.Horizontal)
        threshold_slider.setRange(0, 100)
        threshold_slider.setValue(50)
        microplastics_detection_layout.addWidget(threshold_label)
        microplastics_detection_layout.addWidget(threshold_slider)

        machine_learning_label = QLabel("Machine Learning Algorithm:")
        machine_learning_options = ["Option 1", "Option 2", "Option 3"]
        machine_learning_combobox = QComboBox()
        machine_learning_combobox.addItems(machine_learning_options)
        microplastics_detection_layout.addWidget(machine_learning_label)
        microplastics_detection_layout.addWidget(machine_learning_combobox)

        microplastics_detection_group.setLayout(microplastics_detection_layout)
        main_layout.addWidget(microplastics_detection_group)

        # Other settings groups can be added in a similar manner

        # Apply and Close buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.applySettings)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addStretch(1)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def applySettings(self):
        # Implement the logic to apply the settings here
        print("Settings applied")

class ImagesWindow(QDialog):
     def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Folder Images")
        self.button = QPushButton("Close", self)
        self.button.clicked.connect(self.close)
        self.resize(1000,800)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
