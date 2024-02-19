import sys
import os
import requests
import json
from PIL import Image
import io
import socket


class DetectMP():
    def __init__(self,file_path, port, parent=None):
        # Define the local URL
        ip_address = self.get_ip_address()
        print(ip_address)
        if not port:
            local_url = f"http://{ip_address}:5000/detect"
        else:
            print("Mutliclass")
            local_url = f"http://{ip_address}:4000/detect"

        # Load the image
        image_path = file_path
        image = Image.open(image_path)
        image = image.resize((640, 640))
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

    def get_ip_address(self):
        try:
            # Get the local hostname
            hostname = socket.gethostname()
            # Get the IP address associated with the hostname
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except socket.error:
            return "Unable to determine local IP address"