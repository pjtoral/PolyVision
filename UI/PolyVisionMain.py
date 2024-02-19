import os
import sys 
from PIL import Image
from PyQt5 import QtGui, QtWidgets, QtMultimedia
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
import math
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
from OkayMessageBox import *
from Detect import DetectUI
from GRBL import GrblUI
from LiveDetect import *
from CalibrationUI import CalibrateUI
from CoordinateUI import CoordinateUI
import threading
from VerificationMessageBox import VerificationBox
from collections import deque
import winsound

class Ui_MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.autoScanning = None
        self.autoFocusing = None
        self.image_queue = deque()
        self.VideoCapture = None
        self.available_ports = list(serial.tools.list_ports.comports())
        self.comports = [f"{port.device} - {port.description.split(' (')[0].strip()}" for port in self.available_ports]
        self.ser = None
        self.blurThreshold = 100 
        self.x = 0
        self.y = 0
        self.measuring = False
        self.paused = False
        self.points = []
        self.distance = 0
        self.capturing = False
        self.calibrating = False
        self.settings = None
        self.z = 0
        self.xLimit = 95
        self.yLimit = 85
        self.totalScan = 0
        self.currentScan = 0
        self.currentMP = 0
        self.widthClicked = None
        self.lengthClicked = None
        with open("user_settings.json", "r") as f:
                self.settings_data = json.load(f)
        self.image_settings = self.settings_data.get("image_settings", {})
        self.grbl_settings = self.settings_data.get("grbl_settings", {})
        self.general_settings = self.settings_data.get("general_features", {})
        self.port = 0
        if self.general_settings["model"] == "Binary":
            self.port = 0
        else:
            self.port = 1
        self.captureDone = None
        create_main_database(os.getcwd())
        create_retraining_database(os.getcwd())
        
    #updating live feed in different Thread
    def ImageUpdateSlot(self, Image):
        if not self.paused:
            # Define the crop parameters (adjust as needed)
            left = 100
            top = 100
            right = Image.width() - 240
            bottom = Image.height() - 395

            # Create a copy of a region from the original image
            cropped_image = Image.copy(left, top, right - left, bottom - top)
            
            # Assuming graphicsView is a QGraphicsView
            self.graphicsView.setPixmap(QPixmap.fromImage(cropped_image))
            if self.autoFocusing is not None:
                self.image_queue.append(self.captureCurrentFrame())

        else:
            pass

    def calculate_blur_and_color(self, pic):

        np_image = self.qimage_to_numpy(pic)
        gray_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
        sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=5)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        blur_value = np.mean(gradient_magnitude)
        average_pixel_value = np.mean(np_image)

        return blur_value, average_pixel_value

    def qimage_to_numpy(self, qimage):
        width = qimage.width()
        height = qimage.height()
        byte_count = qimage.byteCount()
        format = qimage.format()

        # Convert the QImage to a NumPy array
        ptr = qimage.bits()
        ptr.setsize(byte_count)
        arr = np.frombuffer(ptr, dtype=np.uint8)

        if format == QImage.Format_RGB888:
            arr = arr.reshape(height, width, 3)
        elif format == QImage.Format_RGB32:
            arr = arr.reshape(height, width, 4)

        return arr

    #for canceling live feed (To add pa)
    def CancelFeed(self):
        self.ImageCapture.stop()

    #for capturing images
    def captureButtonClicked(self):
        try:
            self.frame = self.captureCurrentFrame()
            self.paused = True
            self.capturing = True
            self.calibrating = False
            self.capture = CaptureUI()
            self.capture.length_clicked.connect(self.onLengthClicked)
            self.capture.width_clicked.connect(self.onWidthClicked)
            self.capture.save_clicked.connect(self.saving)
            self.capture.on_rejected.connect(self.captureClose)
            toReturn = self.capture.exec()
            return toReturn
        except:
            pass
            
    def captureClose(self):
        self.VideoCapture.start()
        self.paused = False
      
    def captureCurrentFrame(self):
        pixmap = self.graphicsView.pixmap()
        return pixmap.toImage()

    def saving(self):
        try:
            image = Image.fromqimage(self.frame)
            sized = image.resize((1600, 900), Image.LANCZOS)
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
        try:
            particle_name = self.capture.particle_name_edit.text() or None
            if particle_name is None:
                # Display an error message
                QMessageBox.critical(self, "Error", "Particle name cannot be empty.", QMessageBox.Ok)
                return  # Do not proceed further if particle_name is None

            length = self.capture.length_edit.text() or ""
            width = self.capture.width_edit.text() or ""
            color = self.capture.color_edit.text() or ""
            shape = self.capture.shape_edit.currentText() or ""
            magnification = self.capture.magnification_edit.text() or ""
            note = self.capture.note_edit.text() or ""
            file_type = self.capture.photo_options_combo.currentText()
            
            frame_filename = f"{particle_name}.{file_type.upper()}" 
            save_folder = self.file_name  # path to folder
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
            save_path = os.path.join(save_folder, frame_filename)
            frame.save(save_path, quality=self.imageQuality())

            # Adjust the insert_data function to handle NULL values appropriately
            insert_data(self.file_name, save_path, particle_name, length, width, color, shape, magnification, note)

            self.capture.close()
            self.capturing = False
            self.paused = False
            self.currentMP += 1
            self.focusValue.setText(str(self.currentMP))
        except Exception as e:
            print("Exception occurred saving image:", e)

        
    def retrainSave(self, frame, isMP, bounding_box):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        save_folder = "retrainingImages"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        save_path = os.path.join(current_directory, save_folder)
        # Get the current row number
        current_row_number = count_rows_in_retraining_database(current_directory)
        # Create a unique image name based on the row number
        image_name = f"image_{current_row_number}.png"
        # Save the image using Pillow (PIL)
        frame.save(os.path.join(save_path, image_name))
        bounding_box_str = json.dumps(bounding_box)
        # Now call retrain_data with the image name
        retrain_data(current_directory, image_name, isMP, bounding_box_str)
        
    def onLengthClicked(self):
        self.capture.hide()
        self.lengthClicked = 1
        self.measureLength()

    def onWidthClicked(self):
        self.capture.hide()
        self.widthClicked = 1
        self.measureLength()

    def measureClicked(self):
        self.calibrating = False
        self.measureLength()

    #start-measuring
    def measureLength(self):
        try:
           self.paused = True
           if not self.measuring:
                if not self.capturing:
                    self.frame = self.captureCurrentFrame()
                self.measuring = True
                self.measureButton.setEnabled(True)
                self.points = []
                self.measureButton.setText("Finish")
                QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
                self.graphicsView.mouseMoveEvent = self.mouseMoveEvent
                self.calibration = self.image_settings.get("calibration")
           else:
                self.stopMeasureLength()
                self.graphicsView.setPixmap(QPixmap.fromImage(self.frame))
        except Exception as e:
            print("Error occurred during measuring:", e)

    def stopMeasureLength(self):
        self.measuring = False
        self.measureButton.setText("Measure")
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        self.paused = False
        self.lengthLabel.setVisible(False)
        if self.capturing and self.measuring != True:
            if self.lengthClicked == 1:
                self.capture.length_edit.setText(str(self.distance * self.calibration))
                self.lengthClicked = 0
            elif self.widthClicked == 1:
                self.capture.width_edit.setText(str(self.distance * self.calibration))
                self.widthClicked = 0
            self.capture.show()
        self.distance = 0 
        self.calibrating = False

    def mousePressEvent(self, event):
        if self.measuring and (event.button() == Qt.LeftButton):
            posGlobal = event.globalPos()
            pos = self.graphicsView.mapFromGlobal(posGlobal)
            self.points.append((pos.x(), pos.y()))
            self.currentPos = (pos.x(), pos.y())
            pixmap = self.graphicsView.pixmap()
            qimage = pixmap.toImage()
            painter = QPainter(qimage)
            pen = QPen(Qt.red)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawPoint(pos.x(),pos.y())
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
        pen = QPen(QColor(255,0,0), 1)
        pen.setDashPattern([2, 2, 2, 2])
        painter.setPen(pen)
        # Draw lines based on stored points
        for i in range(len(self.points) - 1):
            pt1 = self.points[i]
            pt2 = self.points[i + 1]
            painter.drawLine(pt1[0], pt1[1],pt2[0],pt2[1])
            self.lengthLabel.setGeometry(QtCore.QRect((pt2[0]+255), (pt2[1]+80), 50, 22))
            self.lengthLabel.setAlignment(Qt.AlignCenter)
            self.lengthLabel.setStyleSheet("background-color: rgba(255, 255, 255, 128);")
            self.lengthLabel.setVisible(True)
            distanceLoc = np.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)
            formatted_distance = "{:.2f}".format(distanceLoc)
        distance.append(distanceLoc)
        for i in range(len(distance)):
            self.distance = self.distance + distance[i]

        painter.end()
        pixmap = QPixmap.fromImage(qimage)
        self.graphicsView.setPixmap(pixmap)
        if (self.calibrating and (len(self.points) == 2)):
            self.calculatePixelDistanceRation()

        distanceShow = (self.distance*self.calibration) + (0.002*self.z)
        formatted_distance = "{:.2f}".format(distanceShow)
        self.lengthLabel.setText(str(formatted_distance))

    def calibrate(self):
        try:
            if self.settings is not None:
                self.settings.hide()
            self.calibrating = True 
            self.measuring = False
            self.measureLength()
        except Exception as e:
            print("Error occurred during calibration:", e)

    def calculatePixelDistanceRation(self):
        calibrateUI = CalibrateUI()
        if calibrateUI.exec_() == QtWidgets.QDialog.Accepted:
            actual = calibrateUI.distance_edit.text()
            try:
                integer_value = int(actual)
                self.calibration = integer_value/self.distance  
                #add saving of calibration and close show setting UI again
                self.image_settings["calibration"] = self.calibration
                if self.settings is not None:
                    self.settings.show()
                # Update settings_data dictionary
                self.settings_data["image_settings"] = self.image_settings
                file_path = "user_settings.json"  
                with open(file_path, "w") as f:
                    json.dump(self.settings_data, f, indent=4) 
                self.calibrating = False
                self.stopMeasureLength()
            except ValueError:
                self.stopMeasureLength()

            

            file_path = "user_settings.json"  
            settings_data = {} 
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    settings_data = json.load(f)
        else:
            self.stopMeasureLength()
            
    def mouseReleaseEvent(self, event):
        pass

    def goToDetect(self):
        self.paused = True
        self.detect = DetectUI(self.port)
        self.detect.close_signal.connect(self.setPausedFalse)
        self.detect.exec_()

    def goToSettings(self):
        self.settings = SettingsUI()
        self.settings.calibration_clicked.connect(self.calibrate)
        self.settings.apply_clicked.connect(self.refreshSettings)
        continued = self.settings.exec_()


    def refreshSettings(self):
        with open("user_settings.json", "r") as f:
                self.settings_data = json.load(f)
                self.image_settings = self.settings_data.get("image_settings", {})
                self.grbl_settings = self.settings_data.get("grbl_settings", {})
                self.general_settings = self.settings_data.get("general_features", {})
                if self.general_settings["model"] == "Binary":
                    self.port = 0
                else:
                    self.port = 1

        
    def goToCurrentImages(self):
        self.paused = True
        self.images = ImagesUI(self.file_name)
        continued = self.images.exec_()
        if continued == QDialog.Rejected :
            self.setPausedFalse()

    def goToStatistics(self):
        self.paused = True
        self.statistics = StatisticsUI(self.file_name)
        self.statistics.close_signal.connect(self.setPausedFalse)
        self.statistics.exec_()


    def setPausedFalse(self):
        self.paused = False

    #accessing COM ports
    def serialConnect(self):
        if not self.ser:
            self.port = self.dropDown.currentText().split(" - ")[0] 
            try:
                self.ser = serial.Serial(self.port, baudrate=115200)
                time.sleep(2)
                self.connectGRBL.setText("Disconnect")
                self.grblzUP.setEnabled(True)
                self.grblzDOWN.setEnabled(True)
                self.grblUP.setEnabled(True)
                self.grblDOWN.setEnabled(True)
                self.grblLEFT.setEnabled(True)
                self.grblRIGHT.setEnabled(True)
                self.grblHOME.setEnabled(True)
                self.emergencyGRBL.setEnabled(True)
                self.focusBTN.setEnabled(True)
                self.grbl = GrblUI()
                #====== ADD AUTOMATION HERE=======#
                self.grbl.auto_clicked.connect(self.autoScan)
                self.grbl.manual_clicked.connect(self.manualScan)
                self.grbl.exec_()
                    
            except Exception as e:
                print("Error connecting serial port:", e)
                
        else:
            try:
                self.ser.close() 
                self.connectGRBL.setText("Connect")  
                self.ser = None
            except Exception as e:
                print("Error closing serial port:", e)

    def focusUp(self):
        if self.ser:
            if self.z != 120:
                string = "G21 G91 G1 Z" 
                string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + "\r\n"
                toSend = string.encode('utf-8')
                self.ser.write(toSend)
                self.z += self.grbl_settings["steps_per_mm"]
                self.zValue.setText(str(self.z))

    def focusDown(self):
        if self.ser:
            if self.z != 0:
                string = "G21 G91 G1 Z-" 
                string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + "\r\n"
                toSend = string.encode('utf-8')
                self.ser.write(toSend)
                self.z -= self.grbl_settings["steps_per_mm"]
                self.zValue.setText(str(self.z))

  
    def moveUp(self):
        if self.ser:
            if self.grbl_settings["area_scan"] == False:
                if self.y != self.yLimit:
                    string = "G21 G91 G1 Y" 
                    string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + "\r\n"
                    toSend = string.encode('utf-8')
                    self.ser.write(toSend)
                    self.y += self.grbl_settings["steps_per_mm"]
                    self.yValue.setText(str(self.y))
            else:
                if self.y != 0: 
                    string = "G21 G91 G1 Y-" 
                    string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + "\r\n"
                    toSend = string.encode('utf-8')
                    self.ser.write(toSend)
                    self.y -= self.grbl_settings["steps_per_mm"]
                    self.yValue.setText(str(self.y))

    def moveDown(self):
        if self.ser:
            if self.grbl_settings["area_scan"] == False:
                if self.y != 0: 
                    string = "G21 G91 G1 Y-" 
                    string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + "\r\n"
                    toSend = string.encode('utf-8')
                    self.ser.write(toSend)
                    self.y -= self.grbl_settings["steps_per_mm"]
                    self.yValue.setText(str(self.y))
            else:
                if self.y != self.yLimit:
                    string = "G21 G91 G1 Y" 
                    string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + "\r\n"
                    toSend = string.encode('utf-8')
                    self.ser.write(toSend)
                    self.y += self.grbl_settings["steps_per_mm"]
                    self.yValue.setText(str(self.y))

    def moveLeft(self):
        if self.ser:
            if self.grbl_settings["area_scan"] == False:
                if self.x != self.xLimit:
                    string = "G21 G91 G1 X-" 
                    string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + "\r\n"
                    toSend = string.encode('utf-8')
                    self.ser.write(toSend)
                    self.x += self.grbl_settings["steps_per_mm"]
                    self.xValue.setText(str(self.x))
            else:
                 if self.x != 15:
                    string = "G21 G91 G1 X" 
                    string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + " \r\n"
                    toSend = string.encode('utf-8')
                    self.ser.write(toSend)
                    self.x -= self.grbl_settings["steps_per_mm"]
                    self.xValue.setText(str(self.x))

    def moveRight(self):
        if self.ser:
            if self.grbl_settings["area_scan"] == False:
                if self.x != 15:
                    string = "G21 G91 G1 X" 
                    string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + " \r\n"
                    toSend = string.encode('utf-8')
                    self.ser.write(toSend)
                    self.x -= self.grbl_settings["steps_per_mm"]
                    self.xValue.setText(str(self.x))
            else:
                if self.x != self.xLimit:
                    string = "G21 G91 G1 X-" 
                    string += str(self.grbl_settings["steps_per_mm"]) + " F" + str(self.grbl_settings["max_feedrate"]) + "\r\n"
                    toSend = string.encode('utf-8')
                    self.ser.write(toSend)
                    self.x += self.grbl_settings["steps_per_mm"]
                    self.xValue.setText(str(self.x))

    def moveHome(self):
        if self.ser:
            self.gcode_command = b"$H\r\n"
            self.ser.write(self.gcode_command)
            self.x = 15
            self.xValue.setText(str(self.x))
            self.y = 0
            self.yValue.setText(str(self.y))
        else:
            pass

    def emergencyStop(self):
        if self.autoFocusing is not None:
            self.autoFocusing.updateThread(False)

        if self.autoScanning is not None:
            self.autoScanning.stop()

        if self.ser:
            self.gcode_command = b"!\r\n"
            self.ser.write(self.gcode_command)
            self.ser.close()
            time.sleep(1)
            self.ser = serial.Serial(self.port, baudrate=115200)
            time.sleep(3)
            self.gcode_command = b"$X\r\n"
            self.ser.write(self.gcode_command)

        else:
            pass

    def autoScan(self):
        self.connectGRBL.setEnabled(False)
        self.grblUP.setEnabled(False)
        self.grblDOWN.setEnabled(False)
        self.grblLEFT.setEnabled(False)
        self.grblRIGHT.setEnabled(False)
        self.grblzUP.setEnabled(False)
        self.grblzDOWN.setEnabled(False)
        self.focusBTN.setEnabled(False)
        self.grblHOME.setEnabled(False)
        self.detectionValue.setText("ON")
        self.statusValue.setText("Scanning")
        self.grbl.hide()
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        self.high = 0
        self.med = 0
        self.low = 0
        self.scanBTN.setText("Continue")
        self.statusValue.setText("Scanning..")
        self.detectionValue.setText("ON")
        #============== Home XY Table ================#
        self.paused = False #pause while moving      
        self.coordinates = CoordinateUI()
        self.coordinates.exec_()
        start_x = self.coordinates.largest_x
        start_y = self.coordinates.largest_y
        rows = self.coordinates.distance_y
        cols = self.coordinates.distance_x
        if start_x is not None and start_y is not None:
            self.autoScanning = AutoScan(self.ser, start_x, start_y, rows, cols)
            self.totalScan = rows * cols
            self.autoScanning.start()
            self.autoScanning.ImageScan.connect(self.scanForMP)
            self.autoScanning.Homing.connect(self.homingPrompt)
            self.autoScanning.Finished.connect(self.finishedScan)

    def startFocusing(self):   
        self.autoFocusing = AutoFocus(self.ser,self.image_queue,self.zValue)
        self.autoFocusing.focused.connect(self.doneFocus)
        self.image_queue.append(self.captureCurrentFrame())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.stopFocusing)
        self.timer.start(7000)
        self.autoFocusing.start()

    def stopFocusing(self):
        if self.autoFocusing is not None:
            self.autoFocusing.ThreadActive = False 
            text = self.zValue.text()
            self.z = float(text)
            string = "G21 G91 G1 Z-" 
            string +=  str(self.z) + " F1000\r\n"
            print(string)
            toSend = string.encode('utf-8')
            self.ser.write(toSend)
            self.z = 0
            self.zValue.setText(str(self.z))
            # prompt = OkayMessageBox("Manual Focusing is Needed")
            # prompt.exec_()
            self.timer.stop()
            self.autoFocusing = None

    def doneFocus(self):
        self.timer.stop()
        self.autoFocusing = None
        text = self.zValue.text()
        self.z = float(text)

    def calculate_blur(self, Pic):
        # Convert the QImage to a numpy array
        npImage = self.qimage_to_numpy(Pic)
        grayImage = cv2.cvtColor(npImage, cv2.COLOR_RGB2GRAY)
        # Use Tenengrad (Sobel) operator for blur detection
        sobelx = cv2.Sobel(grayImage, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(grayImage, cv2.CV_64F, 0, 1, ksize=5)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        blur_value = np.mean(gradient_magnitude)

        return blur_value

    def qimage_to_numpy(self, qimage):
        width = qimage.width()
        height = qimage.height()
        byte_count = qimage.byteCount()
        format = qimage.format()

        # Convert the QImage to a NumPy array
        ptr = qimage.bits()
        ptr.setsize(byte_count)
        arr = np.frombuffer(ptr, dtype=np.uint8)

        if format == QImage.Format_RGB888:
            arr = arr.reshape(height, width, 3)
        elif format == QImage.Format_RGB32:
            arr = arr.reshape(height, width, 4)

        return arr

    def manualScanBTN(self):   
        if self.scanBTN.text() == "Continue":
            if self.autoScanning is not None:
                self.autoScanning.event.set()
        else:
            self.manualScanMP()

    def manualScanMP(self):
        self.statusValue.setText("Scanning")   
        currentFrame = self.captureCurrentFrame()
        image = Image.fromqimage(currentFrame)
        sized = image.resize((640, 640), Image.LANCZOS)
        self.paused = True #pause while requesting from API

        detector =  DetectMP(sized, self.port)
        if len(detector.get_json()) != 0:
            if self.general_settings["sound"] == True:
                winsound.Beep(800, 500)
                winsound.Beep(800, 500)
                winsound.Beep(800, 750)
            low = 0
            med = 0
            high = 0
            for items in detector.get_json():
                if items["score"] > 0.70 and items["score"] < 0.80:
                    low += 1
                elif items["score"] > 0.80 and items["score"] < 0.90:
                    med += 1
                elif items["score"] >= 0.90  and items["score"] < 1.0:
                    high += 1
            self.highValue.setText(str(high)) 
            self.moderateValue.setText(str(med))  
            self.lowValue.setText(str(low)) 
            new_image = BoundingBox(sized, detector.get_json(), self.port)
            rgb_image = new_image.get_image()
            height, width, channel = rgb_image.shape
            bytes_per_line = 3 * width
            qimage = QtGui.QImage(rgb_image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            qpixmap = QPixmap.fromImage(qimage)
            scaled = qpixmap.scaled(1280,720)
            self.graphicsView.setPixmap(scaled)
            # self.graphicsView.setScaledContents(True)
            dialog = VerificationBox("Microplastic Found. Capture Image?") 
            continued = dialog.exec_()    
            if continued == QDialog.Accepted:
                verify = VerificationBox("Is this a Microplastic?")
                go = verify.exec_()
                if go == QDialog.Accepted:
                    self.paused = True
                    qpixmap = QPixmap.fromImage(currentFrame)
                    image = Image.fromqimage(qpixmap)
                    self.graphicsView.setPixmap(qpixmap)
                    self.captureButtonClicked()
                    self.retrainSave(currentFrame, True, detector.get_json()) #frame, bool, bounding box
                else:
                    self.retrainSave(currentFrame, False, detector.get_json()) #frame, bool, bounding box
                    self.paused = False
            else:
                self.retrainSave(currentFrame, False, detector.get_json()) #frame, bool, bounding box
                self.paused = False
        else:
            self.retrainSave(currentFrame, True, detector.get_json()) #frame, bool, bounding box
            self.paused = False
        self.statusValue.setText("Idle")
            


    def autoFocus(self):
        self.autoFocusing.updateThread(False)
         

    def scanForMP(self):
        self.currentScan += 1
        self.progressBar.setProperty("value", (self.currentScan/self.totalScan) * 100)
        self.x = self.autoScanning.x
        self.y = self.autoScanning.y
        self.xValue.setText(str(self.x))
        self.yValue.setText(str(self.y))

        currentFrame = self.captureCurrentFrame()
        image = Image.fromqimage(currentFrame)
        sized = image.resize((640, 640), Image.LANCZOS)
        self.paused = True #pause while requesting from API
        detector =  DetectMP(sized, self.port)
        if len(detector.get_json()) != 0:
            if self.general_settings["sound"] == True:
                winsound.Beep(800, 500)
                winsound.Beep(800, 500)
                winsound.Beep(800, 750)
            low = 0
            med = 0
            high = 0
            for items in detector.get_json():
                if items["score"] > 0.70 and items["score"] < 0.80:
                    low += 1
                elif items["score"] > 0.80 and items["score"] < 0.90:
                    med += 1
                elif items["score"] >= 0.90  and items["score"] < 1.0:
                    high += 1

            self.highValue.setText(str(high)) 
            self.moderateValue.setText(str(med))  
            self.lowValue.setText(str(low)) 
            print("With MP")
            new_image = BoundingBox(sized, detector.get_json(), self.port)
            rgb_image = new_image.get_image()
            height, width, channel = rgb_image.shape
            bytes_per_line = 3 * width
            qimage = QtGui.QImage(rgb_image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            qpixmap = QPixmap.fromImage(qimage)
            scaled = qpixmap.scaled(1280,720)
            self.graphicsView.setPixmap(scaled)
            # self.graphicsView.setScaledContents(True)
            dialog = VerificationBox("Microplastic Found. Capture Image?") 
            continued = dialog.exec_()    
            if continued == QDialog.Accepted:     
                verify = VerificationBox("Is this a Microplastic?")
                yes = verify.exec_()
                if yes == QDialog.Accepted:
                    qpixmap = QPixmap.fromImage(currentFrame)
                    image = Image.fromqimage(qpixmap)
                    self.graphicsView.setPixmap(qpixmap)
                    self.paused = True
                    self.captureDone = self.captureButtonClicked()
                    self.retrainSave(currentFrame, True, detector.get_json()) #frame, bool, bounding box
                else:
                    self.retrainSave(currentFrame, False, detector.get_json()) #frame, bool, bounding box
                    self.autoScanning.event.set()
                    self.paused = False 
            else:
                self.retrainSave(currentFrame, False, detector.get_json()) #frame, bool, bounding box
                self.autoScanning.event.set()
                self.paused = False           
        else:
            self.retrainSave(currentFrame, False, "") #frame, bool, bounding box
            self.paused = False
            self.autoScanning.event.set()

                
    def homingPrompt(self):
        dialog = OkayMessageBox("Homing... Click Okay when finished.")
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.autoScanning.event.set()

    def finishedScan(self):
        self.progressBar.setProperty("value", 0)
        self.currentScan = 0
        self.totalScan = 0
        self.paused = False #unpause
        self.connectGRBL.setEnabled(True)
        self.grblUP.setEnabled(True)
        self.grblDOWN.setEnabled(True )
        self.grblLEFT.setEnabled(True )
        self.grblRIGHT.setEnabled(True )
        self.grblzUP.setEnabled(True )
        self.grblzDOWN.setEnabled(True )
        self.focusBTN.setEnabled(True )
        self.grblHOME.setEnabled(True)
        self.statusValue.setText("Idle")
        self.detectionValue.setText("OFF")
        verify = VerificationBox("Do you want to rescan?")
        self.x = 15
        self.y = 0 
        self.xValue.setText(str(self.x))
        self.yValue.setText(str(self.y))
        continued = verify.exec_()
        if continued == QDialog.Accepted:
            self.autoScan()
        else:
            self.scanBTN.setText("Scan")

    def manualScan(self):
        self.moveHome()
        # pass

    def closeEvent(self, event):
        self.videoCapture.stop()
        self.videoCapture.wait()
        event.accept()

    def count_images_in_folder(self, folder_path):
        # List all files in the folder
        all_files = os.listdir(folder_path)

        # Filter for image files (you can add more extensions if needed)
        image_files = [file for file in all_files if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]

        # Count the number of image files
        num_images = len(image_files)

        return num_images

    def on_new_action(self):
        
        new_file_widget = NewFileUI()
        if new_file_widget.exec_() == QtWidgets.QDialog.Accepted and new_file_widget.file_name_edit.text() != '' and new_file_widget.location_edit.text() != '':
            self.file_name = new_file_widget.file_name_edit.text()
            location = new_file_widget.location_edit.text()
            sampling_date = new_file_widget.sampling_date_edit.text()
            self.placeValue.setText(self.file_name)        
            self.locationValue.setText(location)
            self.dateValue.setText(sampling_date)
            self.selected_camera_index = new_file_widget.camera_combo_box.currentIndex()
            if self.VideoCapture is not None:
                self.VideoCapture.ThreadActive = False
            self.VideoCapture = VideoCapture(self.selected_camera_index)
            self.VideoCapture.start()
            self.VideoCapture.ImageUpdate.connect(self.ImageUpdateSlot)
            add_database_entry(self.file_name, f"{location}/microplastic.db", sampling_date)
            create_microplastics_database(self.file_name)
            self.paused = False
            self.statusValue.setText("Idle....")
            self.detectionValue.setText("OFF")
            self.highValue.setText("0") 
            self.moderateValue.setText("0")  
            self.lowValue.setText("0") 

            self.currentMP = self.count_images_in_folder(self.file_name)
            self.focusValue.setText(str(self.currentMP))
            self.captureButton.setEnabled(True)
            self.connectGRBL.setEnabled(True)
            self.imagesButton.setEnabled(True)
            self.detectButton.setEnabled(True)
            self.statisticsButton.setEnabled(True)
            self.measureButton.setEnabled(True)
            self.calibrateBTN.setEnabled(True)
            self.scanBTN.setEnabled(True)
            self.available_ports = list(serial.tools.list_ports.comports())
            self.comports = [f"{port.device} - {port.description.split(' (')[0].strip()}" for port in self.available_ports]
            self.dropDown.addItems(self.comports)

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
        self.currentStatus      =   QtWidgets.QLabel(self.centralwidget)
        self.boxWidget          =   QtWidgets.QLabel(self.centralwidget)
        self.xWidget            =   QtWidgets.QLabel(self.centralwidget)
        self.zWidget            =   QtWidgets.QLabel(self.centralwidget)
        self.xLabel             =   QtWidgets.QLabel(self.centralwidget)
        self.xValue             =   QtWidgets.QLabel(self.centralwidget)
        self.zLabel             =   QtWidgets.QLabel(self.centralwidget)
        self.zValue             =   QtWidgets.QLabel(self.centralwidget)
        self.yLabel             =   QtWidgets.QLabel(self.centralwidget)
        self.yValue             =   QtWidgets.QLabel(self.centralwidget)
        self.appTitle           =   QtWidgets.QLabel(self.centralwidget)
        self.dropDown           =   QtWidgets.QComboBox(self.centralwidget)
        self.appLogo            =   QtWidgets.QLabel(self.centralwidget)  
        self.filamentValue      =   QtWidgets.QLabel(self.centralwidget)     

        self.dropDown.setFocusPolicy(Qt.NoFocus)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.appLogo.setPixmap(QtGui.QPixmap("res/PolyVisionLogo.png"))
        self.appLogo.setScaledContents(True)

        
        #setting font for labels
        font = QtGui.QFont()
        font.setFamily("Nirmala UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
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
        self.zLabel.setFont(font)
        font.setPointSize(10)
        self.xValue.setFont(font)
        self.yValue.setFont(font)
        self.zValue.setFont(font)
        
        #seeting font for app Title
        font.setFamily("Gotham")
        font.setPointSize(14)
        font.setBold(True)
        self.appTitle.setFont(font)
        
        #setting font for section titles
        font.setPointSize(11)
        self.grblTitle.setFont(font)
        self.realTimeLabel.setFont(font)
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
        self.grblzUP            = QtWidgets.QPushButton(self.centralwidget) 
        self.grblzDOWN          = QtWidgets.QPushButton(self.centralwidget) 
        self.grblLEFT           = QtWidgets.QPushButton(self.centralwidget) 
        self.grblRIGHT          = QtWidgets.QPushButton(self.centralwidget) 
        self.grblHOME           = QtWidgets.QPushButton(self.centralwidget)
        self.connectGRBL        = QtWidgets.QPushButton(self.centralwidget)
        self.emergencyGRBL      = QtWidgets.QPushButton(self.centralwidget)
        self.calibrateBTN       = QtWidgets.QPushButton(self.centralwidget)
        self.scanBTN            = QtWidgets.QPushButton(self.centralwidget)
        self.focusBTN           = QtWidgets.QPushButton(self.centralwidget)


        #==================Stylesheets======================#
        self.graphicsView.setStyleSheet("background-color: rgb(0,0,0);") #Black
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
        self.grblzUP.setStyleSheet(u"QPushButton {\n""       background-color: qconicalgradient(cx:0.5, cy:0, angle:90.9, stop:0 rgba(255, 255, 255, 255), stop:0.37223 rgba(255, 255, 255, 255), stop:0.373991 rgba(251, 191, 22, 255), stop:0.62362 rgba(253, 202, 22, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""     background-color: qconicalgradient(cx:0.5, cy:0, angle:90.9, stop:0 rgba(255, 255, 255, 255), stop:0.37223 rgba(255, 255, 255, 255), stop:0.373991 rgba(158, 120, 14, 255), stop:0.62362 rgba(158, 120, 14, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""}")
        self.grblzDOWN.setStyleSheet(u"QPushButton {\n""    background-color: qconicalgradient(cx:0.494318, cy:1, angle:270, stop:0 rgba(255, 255, 255, 255), stop:0.373989 rgba(255, 255, 255, 255), stop:0.373991 rgba(252, 191, 22, 255), stop:0.623986 rgba(252, 191, 22, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: qconicalgradient(cx:0.494318, cy:1, angle:270, stop:0 rgba(255, 255, 255, 255), stop:0.37223 rgba(255, 255, 255, 255), stop:0.373991 rgba(158, 120, 14, 255), stop:0.62362 rgba(158, 120, 14, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""}")
        self.grblLEFT.setStyleSheet(u"QPushButton {\n""     background-color: qconicalgradient(cx:0, cy:0.499, angle:180.1, stop:0 rgba(255, 255, 255, 255), stop:0.375488 rgba(255, 255, 255, 255), stop:0.375911 rgba(252, 191, 22, 255), stop:0.622911 rgba(251, 191, 22, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: qconicalgradient(cx:0, cy:0.499, angle:180.1, stop:0 rgba(255, 255, 255, 255), stop:0.37548 rgba(255, 255, 255, 255), stop:0.375626 rgba(158, 120, 14, 255), stop:0.622911 rgba(158, 120, 14, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""}")
        self.grblRIGHT.setStyleSheet(u"QPushButton {\n""    background-color: qconicalgradient(cx:1, cy:0.499, angle:0.110478, stop:0 rgba(255, 255, 255, 255), stop:0.373989 rgba(255, 255, 255, 255), stop:0.373991 rgba(252, 191, 22, 255), stop:0.623986 rgba(252, 191, 22, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: qconicalgradient(cx:1, cy:0.499, angle:0.110478, stop:0 rgba(255, 255, 255, 255), stop:0.373989 rgba(255, 255, 255, 255), stop:0.373991 rgba(252, 191, 22, 255), stop:0.374003 rgba(158, 120, 14, 255), stop:0.623986 rgba(158, 120, 14, 255), stop:0.624043 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));\n""}")
        self.grblHOME.setStyleSheet(u"QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 10px;\n""    border-radius: 1px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.boxWidget.setStyleSheet(u"\n""border: 2px solid #d3d3d3;\n""border-radius: 10px;\n" "background-color: transparent;\n")
        self.xWidget.setStyleSheet(u"\n""border: 1px solid #d3d3d3;\n""border-radius: 10px;\n" "background-color: transparent;\n")
        self.zWidget.setStyleSheet(u"\n""border: 1px solid #d3d3d3;\n""border-radius: 10px;\n" "background-color: transparent;\n")
        self.connectGRBL.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.emergencyGRBL.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.calibrateBTN.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.scanBTN.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.focusBTN.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 16px;\n""    border-radius: 10px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
       
        #======================BUTTON ACTIONS===========================#
        self.captureButton.clicked.connect(self.captureButtonClicked)
        self.detectButton.clicked.connect(self.goToDetect)
        self.grblUP.clicked.connect(self.moveUp)
        self.grblDOWN.clicked.connect(self.moveDown)
        self.grblzUP.clicked.connect(self.focusUp)
        self.grblzDOWN.clicked.connect(self.focusDown)
        self.grblLEFT.clicked.connect(self.moveLeft)
        self.grblRIGHT.clicked.connect(self.moveRight)
        self.grblHOME.clicked.connect(self.moveHome)
        self.statisticsButton.clicked.connect(self.goToStatistics)
        self.settingsButton.clicked.connect(self.goToSettings)
        self.imagesButton.clicked.connect(self.goToCurrentImages)
        self.measureButton.clicked.connect(self.measureClicked)
        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.connectGRBL.clicked.connect(self.serialConnect)
        self.emergencyGRBL.clicked.connect(self.emergencyStop)
        self.calibrateBTN.clicked.connect(self.calibrate)
        self.scanBTN.clicked.connect(self.manualScanBTN)
        self.focusBTN.clicked.connect(self.startFocusing)

        #======================APP&LOGOS COORDNT========================#
        self.appTitle       .setGeometry(QtCore.QRect(100, 70, 140,40))
        self.appLogo         .setGeometry(QtCore.QRect(30, 60, 60, 50))
        #=====================MAIN VIEW COORDINATES=====================#
        self.progressLabel   .setGeometry(QtCore.QRect(290, 817, 80, 30))
        self.progressBar     .setGeometry(QtCore.QRect(380, 823, 565, 25))
        self.graphicsView    .setGeometry(QtCore.QRect(290, 90, 1280, 720))
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
        #====================STATUS COORDINATES==========================
        self.currentStatus      .setGeometry(QtCore.QRect(1595, 310, 175, 30))
        self.focusLabel         .setGeometry(QtCore.QRect(1595, 340, 105, 30))
        self.focusValue         .setGeometry(QtCore.QRect(1745, 340, 100, 30))
        self.statusLabel        .setGeometry(QtCore.QRect(1595, 370, 60, 30))
        self.statusValue        .setGeometry(QtCore.QRect(1745, 370, 100, 30))
        self.detectionLabel     .setGeometry(QtCore.QRect(1595, 400, 135, 30))
        self.detectionValue     .setGeometry(QtCore.QRect(1745, 400, 100, 30))
        #====================PICTURE COORDINATES=========================#
        self.captureButton   .setGeometry(QtCore.QRect(1600, 440, 280, 35))
        self.measureButton   .setGeometry(QtCore.QRect(1600, 480, 280, 35))
        self.calibrateBTN    .setGeometry(QtCore.QRect(1600, 520, 280, 35))
        self.scanBTN        .setGeometry(QtCore.QRect(1600, 560, 280, 35))
        #======================GRBL COORDINATES=========================#
        self.boxWidget       .setGeometry(QtCore.QRect(1595, 610, 300, 250))
        self.xWidget         .setGeometry(QtCore.QRect(1765, 690, 115, 150))
        self.zWidget         .setGeometry(QtCore.QRect(1610, 690, 150, 150))
        self.grblTitle       .setGeometry(QtCore.QRect(1645, 620, 200, 35))
        self.grblUP          .setGeometry(QtCore.QRect(1665, 695, 43, 43))
        self.grblDOWN        .setGeometry(QtCore.QRect(1665, 790, 43, 43))
        self.grblzUP          .setGeometry(QtCore.QRect(1800, 695, 43, 43))
        self.grblzDOWN        .setGeometry(QtCore.QRect(1800, 743, 43, 43))
        self.grblLEFT        .setGeometry(QtCore.QRect(1617, 743, 43, 43))
        self.grblRIGHT       .setGeometry(QtCore.QRect(1713, 743, 43, 43))
        self.grblHOME        .setGeometry(QtCore.QRect(1665, 743, 43, 43))
        self.xLabel          .setGeometry(QtCore.QRect(1622, 655, 45, 20))
        self.xValue          .setGeometry(QtCore.QRect(1652, 657, 50, 20))
        self.yLabel          .setGeometry(QtCore.QRect(1708, 655, 45, 20))
        self.yValue          .setGeometry(QtCore.QRect(1738, 657, 50, 20))
        self.zLabel          .setGeometry(QtCore.QRect(1800, 655, 45, 20))
        self.zValue          .setGeometry(QtCore.QRect(1820, 657, 50, 20))
        self.dropDown        .setGeometry(QtCore.QRect(950, 820, 300,30))
        self.connectGRBL     .setGeometry(QtCore.QRect(1260, 820, 150,30))
        self.emergencyGRBL   .setGeometry(QtCore.QRect(1420, 820, 150,30))
        self.focusBTN        .setGeometry(QtCore.QRect(1780, 795, 85, 30))
        #====================SETTINGS COORDINATES=========================#
        self.detectButton    .setGeometry(QtCore.QRect(0, 170, 261, 41))
        self.imagesButton    .setGeometry(QtCore.QRect(0, 260, 261, 41))
        self.statisticsButton.setGeometry(QtCore.QRect(0, 350, 261, 41))
        self.settingsButton  .setGeometry(QtCore.QRect(0, 440, 261, 41))
        
        #====================menuBar============================#

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1253, 40))
        self.menubar.setStyleSheet("background-color: rgb(245, 245, 245);")
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionHelp = QtWidgets.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionYT = QtWidgets.QAction(MainWindow)
        self.actionYT.setObjectName("actionYT")

        self.menubar.addAction(self.actionNew)
        self.menubar.addAction(self.actionYT)
        self.menubar.addAction(self.actionHelp)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "C.Scope.AI"))
        #==============Setting Label Texts=======================#
        self.locationLabel.setText(_translate("MainWindow", "Location:"))
        self.dataLabel.setText(_translate("MainWindow", "Date Sampled:"))
        self.focusLabel.setText(_translate("MainWindow", "Current MP:"))
        self.statusLabel.setText(_translate("MainWindow", "Status:"))
        self.detectionLabel.setText(_translate("MainWindow", "Auto Detection:"))
        self.progressLabel.setText(_translate("MainWindow", "Progress:"))
        self.realTimeLabel.setText(_translate("MainWindow", "Real-Time Report"))
        self.currentStatus.setText(_translate("MainWindow", "Current Status"))
        self.grblTitle.setText(_translate("MainWindow", "Platform Coordinates"))
        self.highLabel.setText(_translate("MainWindow", "High:"))
        self.moderateLabel.setText(_translate("MainWindow", "Moderate:"))
        self.lowLabel.setText(_translate("MainWindow", "Low:"))
        self.appTitle.setText(_translate("MainWindow", "C.Scope.AI"))
        self.captureButton.setText(_translate("MainWindow", "Capture"))
        self.measureButton.setText(_translate("MainWindow", "Measure"))
        self.grblzUP.setText(_translate("MainWindow", "↑"))
        self.grblUP.setText(_translate("MainWindow", "↑"))
        self.grblUP.setShortcut("Up")
        self.grblzDOWN.setText(_translate("MainWindow", "↓"))
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
        self.xValue.setText(_translate("MainWindow","00.0"))
        self.yLabel.setText(_translate("MainWindow","Y  :"))
        self.yValue.setText(_translate("MainWindow","00.0"))
        self.zLabel.setText(_translate("MainWindow","Z  :"))
        self.zValue.setText(_translate("MainWindow","00.0"))
        self.connectGRBL.setText(_translate("MainWindow","Connect"))
        self.emergencyGRBL.setText(_translate("MainWindow","Emergency Stop"))
        self.calibrateBTN.setText(_translate("MainWindow","Calibrate"))
        self.scanBTN.setText(_translate("MainWindow","Scan"))
        self.focusBTN.setText(_translate("MainWindow","Focus"))


        #Menu Bar
        self.actionHelp.setText(_translate("MainWindow", "Help?"))
        self.actionHelp.setShortcut(_translate("MainWindow", "Ctrl+H"))
        self.actionYT.setText(_translate("MainWindow", "Guide"))
        self.actionYT.setShortcut(_translate("MainWindow", "Ctrl+Y"))
        self.actionNew.setText(_translate("MainWindow", "New File"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))

        #===========Menu Bar Actions=============#
        self.actionNew.triggered.connect(self.on_new_action)
        self.actionHelp.triggered.connect(SettingsUI.redirectDocumentation)
        self.actionYT.triggered.connect(SettingsUI.redirectYoutube)

        self.captureButton.setEnabled(False)
        self.measureButton.setEnabled(False)
        self.grblzUP.setEnabled(False)
        self.grblzDOWN.setEnabled(False)
        self.grblUP.setEnabled(False)
        self.grblDOWN.setEnabled(False)
        self.grblLEFT.setEnabled(False)
        self.grblRIGHT.setEnabled(False)
        self.grblHOME.setEnabled(False)
        self.connectGRBL.setEnabled(False)
        self.emergencyGRBL.setEnabled(False)
        self.imagesButton.setEnabled(False)
        self.detectButton.setEnabled(False)
        self.statisticsButton.setEnabled(False)
        self.calibrateBTN.setEnabled(False)
        self.scanBTN.setEnabled(False)
        self.focusBTN.setEnabled(False)

        self.captureButton.setShortcut("C")
        self.measureButton.setShortcut("M")
        self.grblzUP.setShortcut("Ctrl+Up")
        self.grblzDOWN.setShortcut("Ctrl+Down")
        self.connectGRBL.setShortcut("G")
        self.emergencyGRBL.setShortcut("E")
        self.calibrateBTN.setShortcut("P")
        self.scanBTN.setShortcut("S")
        self.settingsButton.setShortcut("Ctrl+S")
        self.imagesButton.setShortcut("Ctrl+I")
        self.detectButton.setShortcut("Ctrl+D")
        self.statisticsButton.setShortcut("Ctrl+A")



class VideoCapture(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, index):
        super().__init__()
        self.index = index
    def run(self):
        self.ThreadActive = True
        self.capture = cv2.VideoCapture(self.index)
        frame_count = 0
        while self.ThreadActive:
            ret, frame = self.capture.read()
            frame_count += 1
            if ret:
                FlippedImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], FlippedImage.strides[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(1620,1215, Qt.KeepAspectRatio) 
                self.ImageUpdate.emit(Pic)
        self.capture.release()

    def stop(self):
        self.ThreadActive = False
        self.quit()

class AutoScan(QThread):
    ImageScan = pyqtSignal()
    Homing = pyqtSignal()
    Finished = pyqtSignal()
    def __init__(self,serial, start_x, start_y, rows, cols):
        super().__init__()
        self.ser = serial
        self.start_x = start_x
        self.start_y = start_y * (-1)
        self.rows = rows
        self.cols = cols 
        self.x = 0
        self.y = 0

    def run(self):
        self.ThreadActive = True
        self.event = threading.Event()
        while self.ThreadActive:
            try:
                self.ser.write(b"$H\r\n")
                time.sleep(5)
                self.Homing.emit()
                self.event.wait()  
                if self.event.is_set():
                    self.event.clear()
                #================= START AUTOMATED SCAN ================#
                string = "G21 G91 G1 X" 
                string += str(self.start_x+15) + " F1000\r\n"
                toSend = string.encode('utf-8')
                self.ser.write(toSend)
                self.x -= self.start_x
                time.sleep((self.start_x/7*-1)+1)
                string = "G21 G91 G1 Y" 
                string += str(self.start_y) + " F1000\r\n"
                toSend = string.encode('utf-8')
                self.ser.write(toSend)
                self.y += self.start_y
                time.sleep((self.start_y/6.5)+1)

                #loop while petridish is unscanned
                for rows in range(int(self.rows)):
                    self.ImageScan.emit()
                    self.event.wait()  
                    if self.event.is_set():
                        self.event.clear()
                    for cols in range(int(self.cols)): 
                        if cols < self.cols - 1:
                            if rows%2 == 0:
                                self.ser.write(b"G21 G91 G1 X-5 F1000\r\n")
                                self.x += 5
                                time.sleep(3)
                            else:
                                self.ser.write(b"G21 G91 G1 X5 F1000\r\n")
                                self.x -= 5
                                time.sleep(3)
                            self.ImageScan.emit()
                            self.event.wait()  
                            if self.event.is_set():
                                self.event.clear()

                    if rows < self.rows - 1:  # Only move down if it's not the last row
                        self.ser.write(b"G21 G91 G1 Y3 F1000\r\n")
                        self.y += 3
                        time.sleep(3)                    

                self.ser.write(b"$H\r\n")

                self.Homing.emit()
                self.event.wait()  
                if self.event.is_set():
                    self.event.clear()

                self.Finished.emit()
                self.event.wait()  
                if self.event.is_set():
                    self.event.clear()
                self.ThreadActive = False
            except:
                pass


    def stop(self):
        self.ThreadActive = False
        self.quit()


class AutoFocus(QThread):
    focused = pyqtSignal()
    def __init__(self, serial, image_queue, zValue):
        super().__init__()
        self.ser = serial
        self.image_queue = image_queue
        text = zValue.text()
        self.z = float(text)
        self.zValue = zValue
        self.gcode_command = b"$X\r\n"
        self.ser.write(self.gcode_command)
        self.up = 1
        self.event = threading.Event()
        self.ThreadActive = True
        self.prev_blur_value = float('inf')
        self.blurThreshold = 600
        self.zinc = 5
        self.increment = 1


    def run(self):
        image = self.image_queue.pop()
        height = image.height()
        width = image.width()

        rows = 3
        cols = 3
        region_height = height // rows
        region_width = width // cols

        result_image =image.copy()

        y1, y2 = 1 * region_height, (1 + 1) * region_height
        x1, x2 = 1 * region_width, (1 + 1) * region_width

        region_rect = QRect(x1, y1, region_width, region_height)

        # Extract the region from the image
        region = image.copy(region_rect)

 
        self.blurValue, average_pixel_value = self.calculate_blur_and_color(region)
        while self.ThreadActive:  # Run indefinitely

            try:
                # Check if the image is near white or near black
                if average_pixel_value < 120:
                    self.blurThreshold = 500
                elif average_pixel_value > 150:
                    self.blurThreshold = 250
                else:
                   self.blurThreshold = 150

                if self.ThreadActive:

                    if self.blurValue < self.blurThreshold:
                        # Focus adjustment code here
                        if self.up:
                            string = "G21 G91 G1 Z" 
                            string +=  str(self.zinc) + " F1000\r\n"
                            toSend = string.encode('utf-8')
                            self.ser.write(toSend)
                            self.z += self.zinc
                        else:
                            if self.z > 0:
                                string = "G21 G91 G1 Z-" 
                                string +=  str(self.zinc) + " F1000\r\n"
                                toSend = string.encode('utf-8')
                                self.ser.write(toSend)
                                self.z -= self.zinc

                        self.zValue.setText(str(self.z))
                        time.sleep(1)

                        
                        difference = abs(self.blurValue - self.prev_blur_value)
                        if difference < 10:
                            self.zinc = 8
                        elif difference > 100:
                            self.zinc = 1
                        else:
                            self.zinc = 5


                        image = self.image_queue.pop()
                        self.prev_blur_value = self.blurValue
                        self.blurValue, average_pixel_value = self.calculate_blur_and_color(image)

                        if self.up:
                            if round(self.blurValue) < round(self.prev_blur_value):
                                self.up = not self.up
                        else:
                            if round(self.prev_blur_value) < round(self.blurValue):
                                self.up = not self.up

                            
                    else:
                        self.ThreadActive = False
                        self.focused.emit()
                        self.image_queue.clear()
                        self.quit()
                else:
                    pass
            except:
                pass

    def updateThread(self, value):
        self.ThreadActive = value

    def stop(self):
        self.ThreadActive = False
        self.quit()

    def calculate_blur_and_color(self, pic):

        np_image = self.qimage_to_numpy(pic)
        gray_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
        sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=5)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        blur_value = np.mean(gradient_magnitude)
        average_pixel_value = np.mean(np_image)

        return blur_value, average_pixel_value

    def qimage_to_numpy(self, qimage):
        width = qimage.width()
        height = qimage.height()
        byte_count = qimage.byteCount()
        format = qimage.format()

        # Convert the QImage to a NumPy array
        ptr = qimage.bits()
        ptr.setsize(byte_count)
        arr = np.frombuffer(ptr, dtype=np.uint8)

        if format == QImage.Format_RGB888:
            arr = arr.reshape(height, width, 3)
        elif format == QImage.Format_RGB32:
            arr = arr.reshape(height, width, 4)

        return arr



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)

    def closeEvent(self, event):
        if self.ui.ser:
            if self.ui.z != 0:
                string = "G21 G91 G1 Z-" 
                string += str(self.ui.z) + " F1000\r\n"
                toSend = string.encode('utf-8')
                self.ui.ser.write(toSend)
            string = "$H\r\n"
            toSend = string.encode('utf-8')
            self.ui.ser.write(toSend)

        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setQuitOnLastWindowClosed(False)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

