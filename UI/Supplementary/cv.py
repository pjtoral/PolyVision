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
from PyQt5.uic import loadUi
import cv2
import numpy as np 

# Create a VideoCapture object
cap = cv2.VideoCapture(0)

# Start capturing video
cap.start()

# Initialize pause flag
paused = False

# Capture frames continuously
while True:
    # Check if the video is paused
    if not paused:
        # Read frame from video capture
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame as needed
        # ...

        # Display the frame
        cv2.imshow("Video", frame)

    # Check for key press
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('p'):
        # Toggle the pause flag
        paused = not paused

# Stop capturing video
cap.stop()

# Release the video capture resources
cap.release()

# Close any open windows
cv2.destroyAllWindows()