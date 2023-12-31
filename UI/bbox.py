import sys
import os
import cv2
import random
from PIL import Image
import numpy as np

class BoundingBox():

    def __init__(self,file_path, plots, parent=None):
        # Bounding box data from the JSON object
        bounding_boxes = plots

        image_path = file_path
        image = Image.open(image_path)
        image = image.resize((640, 640))
        
        self.image= np.array(image)

        # Draw bounding boxes on the image
        for bbox_data in bounding_boxes:
            bbox = bbox_data["bbox"]
            class_id = bbox_data["class_id"]
            score = bbox_data["score"]

            x_min, y_min, x_max, y_max = map(int, bbox)

            red = random.randint(0, 150)
            green = random.randint(0, 150)
            blue = random.randint(0, 150)
            color = (red, green, blue)

            thickness = 1

            # Draw the bounding box
            cv2.rectangle(self.image, (x_min, y_min), (x_max, y_max), color, thickness)

            # Add label with class ID and score
            label = f"microplastic, Score: {score:.2f}"
            label_position = (x_min, y_min-2)
            cv2.putText(self.image, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.27, color, thickness)

    def get_image(self):
        return self.image
