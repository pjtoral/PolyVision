import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QLabel, QComboBox, QPushButton, QVBoxLayout, QWidget

# Get a list of all available COM ports
available_ports = list(serial.tools.list_ports.comports())
comports = [f"{port.device} - {port.description}" for port in available_ports]

# Create the application
app = QApplication([])

# Create the main window
window = QWidget()
window.setWindowTitle("COM Port Selection")

# Create layout
layout = QVBoxLayout()

# Create a label
label = QLabel("Select a COM Port:")
layout.addWidget(label)

# Create a dropdown selection
dropdown = QComboBox()
dropdown.addItems(comports)
layout.addWidget(dropdown)

# Function to get the selected port
def get_selected_port():
    port = dropdown.currentText().split(" - ")[0]  # Extract the COM port
    print("Selected COM port:", port)

# Create a button to get the selected port
button = QPushButton("Get Port")
button.clicked.connect(get_selected_port)
layout.addWidget(button)

# Set the layout on the window
window.setLayout(layout)

# Show the window
window.show()

# Run the application
app.exec_()
