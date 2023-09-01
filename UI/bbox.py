import sys
import os
import cv2

class BoundingBox():

    def __init__(self,file_path, plots, parent=None):
        # Path to the image
        image_path = file_path

        # Bounding box data from the JSON object
        bounding_boxes = plots

        # Load the image
        self.image = cv2.imread(image_path)

        # Draw bounding boxes on the image
        for bbox_data in bounding_boxes:
            bbox = bbox_data["bbox"]
            class_id = bbox_data["class_id"]
            score = bbox_data["score"]

            x_min, y_min, x_max, y_max = map(int, bbox)
            color = (255,0,255)  # Green color for bounding boxes
            thickness = 2

            # Draw the bounding box
            cv2.rectangle(self.image, (x_min, y_min), (x_max, y_max), color, thickness)

            # Add label with class ID and score
            label = f"microplastic, Score: {score:.2f}"
            label_position = (x_min, y_min - 10)
            cv2.putText(self.image, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

    def get_image(self):
        return self.image
