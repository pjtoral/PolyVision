import os
import sys 
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMainWindow
from PyQt5 import QtCore
from PyQt5.QtCore import *
import cv2
import numpy as np 

class Scene1(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)
        
        self.button = QtWidgets.QPushButton(self.QGraphicsScene)
        self.button.clicked.connect(self.switch_to_scene2)
        self.addItem(self.button)
    
    def switch_to_scene2(self):
        scene2 = Scene2()
        view.setScene(scene2)


class Scene2(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)
        
        self.button = QtWidgets.QPushButton(self.centralwidget)
        self.button.clicked.connect(self.switch_to_scene1)
        self.addItem(self.button)
    
    def switch_to_scene1(self):
        scene1 = Scene1()
        view.setScene(scene1)


if __name__ == "__main__":
    app = QApplication([])
    view = QGraphicsView()
    
    scene1 = Scene1()
    view.setScene(scene1)
    
    view.setWindowTitle("Scene Transition Example")
    view.show()
    
    app.exec_()
