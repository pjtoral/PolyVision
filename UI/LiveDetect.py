import sys
import os
import requests
import json
import io
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PIL.ImageQt import ImageQt  # Import ImageQt from PIL to convert PIL Image to QImage
from PIL import Image


class DetectMP():
    def __init__(self,image, parent=None):
        # Define the local URL
        local_url = "http://localhost:5000/detect"

        # Convert the QImage to a PPM image in memory
        image_bytes = io.BytesIO()
        image.save(image_bytes, "PPM")
        image_bytes.seek(0)

        payload = {'image': image_bytes}

        # Make the POST request
        response = requests.post(local_url, files=payload)

        # Process the JSON response
        if response.status_code == 200:
            self.result = response.json()
            print(json.dumps(self.result, indent=4))
        else:
            print("Error:", response.status_code)
            print(response.text)

    def get_json(self):
        return self.result

class BoundingBox():
    def __init__(self, imageLoad, plots, parent=None):
        # Bounding box data from the JSON object
        bounding_boxes = plots

        image_np = np.array(imageLoad)

        # Draw bounding boxes on the image
        for bbox_data in bounding_boxes:
            bbox = bbox_data["bbox"]
            class_id = bbox_data["class_id"]
            score = bbox_data["score"]

            x_min, y_min, x_max, y_max = map(int, bbox)
            #add random numbers
            color = (255, 0, 255)
            thickness = 1

            # Draw the bounding box
            cv2.rectangle(image_np, (x_min, y_min), (x_max, y_max), color, thickness)

            # Add label with class ID and score
            label = f"microplastic, Score: {score:.2f}"
            label_position = (x_min, y_min)
            cv2.putText(image_np, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.27, color, thickness)

        # Convert the modified NumPy array back to a QImage
        self.image = image_np


    def get_image(self):
        return self.image