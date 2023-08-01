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


class SettingsUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMaximumSize(800, 500)
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))

        # Set the background color for the window
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor("#FFFFFF"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        mother_layout = QVBoxLayout()
        main_layout = QHBoxLayout()

        # Left-side layout containing the Image Acquisition and GRBL Settings
        left_layout = QVBoxLayout()

        # Image Acquisition Settings
        image_acquisition_group = QGroupBox("Image Acquisition Settings")
        image_acquisition_layout = QVBoxLayout()

        resolution_group = QGroupBox("")
        resolution_layout = QHBoxLayout()
        resolution_label = QLabel ("Resolution: ")
        resolution_layout.addWidget(resolution_label)
        resolution_dropbox = QComboBox()
        resolution_options = ["Low", "Medium", "High"]
        resolution_dropbox.addItems(resolution_options)
        resolution_layout.addWidget(resolution_dropbox)
        resolution_group.setLayout(resolution_layout)
        image_acquisition_layout.addWidget(resolution_group)


        sharpness_balance_group = QGroupBox("")
        sharpness_balance_layout = QHBoxLayout()
        sharpness_balance_label = QLabel ("Sharpness: ")
        sharpness_balance_slider= QSlider(Qt.Horizontal)
        sharpness_balance_slider.setRange(1, 100)
        sharpness_balance_slider.setValue(0)
        sharpness_balance_layout.addWidget(sharpness_balance_label)
        sharpness_balance_layout.addWidget(sharpness_balance_slider)
        sharpness_balance_group.setLayout(sharpness_balance_layout)
        image_acquisition_layout.addWidget(sharpness_balance_group)


        saturation_balance_group = QGroupBox("")
        saturation_balance_layout = QHBoxLayout()
        saturation_balance_label = QLabel ("Saturation: ")
        saturation_balance_slider= QSlider(Qt.Horizontal)
        saturation_balance_slider.setRange(-100, 100)
        saturation_balance_slider.setValue(0)
        saturation_balance_layout.addWidget(saturation_balance_label)
        saturation_balance_layout.addWidget(saturation_balance_slider)
        saturation_balance_group.setLayout(saturation_balance_layout)
        image_acquisition_layout.addWidget(saturation_balance_group)

        row_layout = QHBoxLayout()

        grid_overlay_group = QGroupBox("")
        grid_overlay_layout = QHBoxLayout()
        grid_overlay_label = QLabel("Grid Overlay:")
        grid_overlay_checkbox = QPushButton()
        grid_overlay_checkbox.setCheckable(True)
        grid_overlay_checkbox.setStyleSheet(
            """
            QPushButton {
                background-color: #e6e6e6;
                border: 2px solid #d4d4d4;
                border-radius: 15px;
                padding: 2px;
            }
            QPushButton:checked {
                background-color: #78c16e;
            }
            QPushButton:checked:enabled:hover {
                background-color: #84d174;
            }
            QPushButton:pressed {
                padding: 4px;
            }
            """
        )
        grid_overlay_checkbox.setFixedSize(100, 20)
        grid_overlay_layout.addWidget(grid_overlay_label)
        grid_overlay_layout.addWidget(grid_overlay_checkbox, alignment= Qt.AlignRight)
        grid_overlay_group.setLayout(grid_overlay_layout)


        cloud_integration_group = QGroupBox("")
        cloud_integration_layout = QHBoxLayout()
        cloud_integration_label = QLabel ("Cloud Integration: ")
        cloud_integration_layout.addWidget(cloud_integration_label)
        cloud_integration_button = QPushButton("Connect to Google")
        cloud_integration_button.setFixedSize(125,28)
        cloud_integration_layout.addWidget(cloud_integration_button)
        cloud_integration_group.setLayout(cloud_integration_layout)


        row_layout.addWidget(grid_overlay_group)
        row_layout.addWidget(cloud_integration_group)
        image_acquisition_layout.addLayout(row_layout)


        calibration_group = QGroupBox("")
        calibration_layout = QHBoxLayout()

        calibration_label = QLabel ("Measurement Calibration: ")
        calibration_layout.addWidget(calibration_label)
        calibration_button = QPushButton("Calibrate")
        calibration_button.setFixedSize(300,28)
        calibration_layout.addWidget(calibration_button)
        calibration_group.setLayout(calibration_layout)
        image_acquisition_layout.addWidget(calibration_group)



        image_acquisition_group.setLayout(image_acquisition_layout)
        left_layout.addWidget(image_acquisition_group)

        # GRBL Controller Settings
        grbl_controller_group = QGroupBox("GRBL Controller Settings")
        grbl_controller_layout = QVBoxLayout()



     


        scan_area_group = QGroupBox("")
        scan_area_layout = QHBoxLayout()
        scan_area_label = QLabel ("Petridish size (mm): ")
        scan_area_layout.addWidget(scan_area_label)
        scan_area_line_edit = QLineEdit()
        scan_area_line_edit.setPlaceholderText("diameter in mm")
        scan_area_layout.addWidget(scan_area_line_edit)
        scan_area_group.setLayout(scan_area_layout)

        grbl_controller_layout.addWidget(scan_area_group)



        row_layout = QHBoxLayout()
        steps_group = QGroupBox("")
        feedrate_group = QGroupBox("")
        steps_layout = QHBoxLayout()
        feedrate_layout = QHBoxLayout()

        steps_label = QLabel ("Steps/mm: ")
        steps_layout.addWidget(steps_label)
        steps_line_edit = QLineEdit()
        steps_line_edit.setPlaceholderText("s/mm")
        steps_layout.addWidget(steps_line_edit)
        feedrate_label = QLabel ("Feedrate: ")
        feedrate_layout.addWidget(feedrate_label)
        feed_line_edit = QLineEdit()
        feed_line_edit.setPlaceholderText("rate")
        feedrate_layout.addWidget(feed_line_edit)
        steps_group.setLayout(steps_layout)
        feedrate_group.setLayout(feedrate_layout)

        scan_overlay_group = QGroupBox("")
        scan_overlay_layout = QHBoxLayout()
        scan_overlay_label = QLabel("Whole Area Scan:")
        scan_overlay_checkbox = QPushButton()
        scan_overlay_checkbox.setCheckable(True)
        scan_overlay_checkbox.setStyleSheet(
            """
            QPushButton {
                background-color: #e6e6e6;
                border: 2px solid #d4d4d4;
                border-radius: 15px;
                padding: 2px;
            }
            QPushButton:checked {
                background-color: #78c16e;
            }
            QPushButton:checked:enabled:hover {
                background-color: #84d174;
            }
            QPushButton:pressed {
                padding: 4px;
            }
            """
        )
        scan_overlay_checkbox.setFixedSize(40, 20)
        scan_overlay_layout.addWidget(scan_overlay_label)
        scan_overlay_layout.addWidget(scan_overlay_checkbox, alignment= Qt.AlignRight)
        scan_overlay_group.setLayout(scan_overlay_layout)



        row_layout.addWidget(steps_group)
        row_layout.addWidget(feedrate_group)
        row_layout.addWidget(scan_overlay_group)
        grbl_controller_layout.addLayout(row_layout)


        # tentative (Ask jeff)
        # homing_bump_label = QLabel ("Homing Bump:")
        # grbl_controller_layout.addWidget(homing_bump_label)


        grbl_controller_group.setLayout(grbl_controller_layout)
        left_layout.addWidget(grbl_controller_group)

        # Add the left-side layout to the main layout
        main_layout.addLayout(left_layout)

        # Right-side layout containing the Microplastics Detection Settings and General Settings
        right_layout = QVBoxLayout()

        
        # General Settings (Add other settings groups here if needed)
        general_settings_group = QGroupBox("General Settings")
        general_settings_layout = QVBoxLayout()
        general_settings_layout.addStretch()

        theme_group = QGroupBox("")
        theme_layout = QVBoxLayout()
        theme_label = QLabel("User Interface Theme: ") #options are, USC, Dark Theme, Ocean
        theme_layout.addWidget(theme_label)
        theme_dropbox = QComboBox()
        theme_options = ["USC", "Dark", "Ocean"]
        theme_dropbox.addItems(theme_options)
        theme_layout.addWidget(theme_dropbox)
        theme_group.setLayout(theme_layout)
        general_settings_layout.addWidget(theme_group,alignment=Qt.AlignTop )


        help_box = QGroupBox("")
        help_layout = QVBoxLayout()
        help_label = QLabel("Help and FAQs")
        help_layout.addWidget(help_label)
        youtube_btn = QPushButton("Youtube")
        help_layout.addWidget(youtube_btn)
        docu_btn = QPushButton("Documentation")
        help_layout.addWidget(docu_btn)
        help_box.setLayout(help_layout)
        general_settings_layout.addWidget(help_box,alignment=Qt.AlignTop)

        report_box = QGroupBox("")
        report_layout = QVBoxLayout()
        report_label = QLabel("Report bugs")
        report_layout.addWidget(report_label)
        report_btn = QPushButton("Report Issue")
        report_layout.addWidget(report_btn)
        report_box.setLayout(report_layout)


        general_settings_layout.addWidget(report_box)
        sound_checkbox = QCheckBox ("Alarm user of detected microplastic")
        general_settings_layout.addWidget(sound_checkbox)
        reset_btn = QPushButton("Reset to default")
        general_settings_layout.addWidget(reset_btn ,alignment=Qt.AlignBottom)
        general_settings_layout.addStretch(1)

        general_settings_group.setLayout(general_settings_layout)

        right_layout.addWidget(general_settings_group)

        # Add the right-side layout to the main layout
        main_layout.addLayout(right_layout)

        # Apply final enclosure
        mother_layout.addLayout(main_layout)
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.setFixedSize(100,28)
        self.apply_button.clicked.connect(self.applySettings)
        self.close_button = QPushButton("Close")
        self.close_button.setFixedSize(100,28)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.apply_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        button_layout.addStretch(1)
        button_layout.addWidget(self.apply_button,  alignment=Qt.AlignRight)
        button_layout.addWidget(self.close_button,  alignment=Qt.AlignRight)
        mother_layout.addLayout(button_layout)
        mother_layout.addStretch(1)
        self.setLayout(mother_layout)

    def applySettings(self):
        # Implement the logic to apply the settings here
        print("Settings applied")

def main():
    app = QApplication(sys.argv)
    settings_ui = SettingsUI()
    settings_ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()





