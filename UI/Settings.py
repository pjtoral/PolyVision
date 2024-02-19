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
import json
import webbrowser

class SettingsUI(QDialog):
    calibration_clicked = pyqtSignal()
    apply_clicked = pyqtSignal()
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
        resolution_label = QLabel ("Image Quality: ")
        resolution_layout.addWidget(resolution_label)
        self.resolution_dropbox = QComboBox()
        resolution_options = ["Low", "Medium", "High"]
        self.resolution_dropbox.addItems(resolution_options)
        resolution_layout.addWidget(self.resolution_dropbox)
        resolution_group.setLayout(resolution_layout)
        image_acquisition_layout.addWidget(resolution_group)


        sharpness_balance_group = QGroupBox("")
        sharpness_balance_layout = QHBoxLayout()
        sharpness_balance_label = QLabel ("Sharpness: ")
        self.sharpness_balance_slider= QSlider(Qt.Horizontal)
        self.sharpness_balance_slider.setRange(1, 99)
        sharpness_balance_layout.addWidget(sharpness_balance_label)
        sharpness_balance_layout.addWidget(self.sharpness_balance_slider)
        sharpness_balance_group.setLayout(sharpness_balance_layout)
        image_acquisition_layout.addWidget(sharpness_balance_group)


        saturation_balance_group = QGroupBox("")
        saturation_balance_layout = QHBoxLayout()
        saturation_balance_label = QLabel ("Saturation: ")
        self.saturation_balance_slider= QSlider(Qt.Horizontal)
        self.saturation_balance_slider.setRange(-99, 99)
        saturation_balance_layout.addWidget(saturation_balance_label)
        saturation_balance_layout.addWidget(self.saturation_balance_slider)
        saturation_balance_group.setLayout(saturation_balance_layout)
        image_acquisition_layout.addWidget(saturation_balance_group)

      


        calibration_group = QGroupBox("")
        calibration_layout = QHBoxLayout()

        calibration_label = QLabel ("Measurement Calibration: ")
        calibration_layout.addWidget(calibration_label)
        calibration_button = QPushButton("Calibrate")
        calibration_button.clicked.connect(self.calibration)
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




        row_layout = QHBoxLayout()
        steps_group = QGroupBox("")
        feedrate_group = QGroupBox("")
        steps_layout = QHBoxLayout()
        feedrate_layout = QHBoxLayout()

        steps_label = QLabel ("Steps/mm: ")
        steps_layout.addWidget(steps_label)
        self.steps_line_edit = QLineEdit()
        self.steps_line_edit.setPlaceholderText("s/mm")
        steps_layout.addWidget(self.steps_line_edit)
        feedrate_label = QLabel ("Feedrate: ")
        feedrate_layout.addWidget(feedrate_label)
        self.feed_line_edit = QLineEdit()
        self.feed_line_edit.setPlaceholderText("rate")
        feedrate_layout.addWidget(self.feed_line_edit)
        steps_group.setLayout(steps_layout)
        feedrate_group.setLayout(feedrate_layout)

        scan_overlay_group = QGroupBox("")
        scan_overlay_layout = QHBoxLayout()
        scan_overlay_label = QLabel("Inverted Feed:")
        self.scan_overlay_checkbox = QPushButton()
        self.scan_overlay_checkbox.setCheckable(True)
        self.scan_overlay_checkbox.setStyleSheet(
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
        self.scan_overlay_checkbox.setFixedSize(40, 20)
        scan_overlay_layout.addWidget(scan_overlay_label)
        scan_overlay_layout.addWidget(self.scan_overlay_checkbox, alignment= Qt.AlignRight)
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
        theme_label = QLabel("Machine Learning Model: ") #options are, USC, Dark Theme, Ocean
        theme_layout.addWidget(theme_label)
        self.theme_dropbox = QComboBox()
        theme_options = ["Binary", "Mutliclass"]
        self.theme_dropbox.addItems(theme_options)
        theme_layout.addWidget(self.theme_dropbox)
        theme_group.setLayout(theme_layout)
        general_settings_layout.addWidget(theme_group,alignment=Qt.AlignTop )


        help_box = QGroupBox("")
        help_layout = QVBoxLayout()
        help_label = QLabel("Help and FAQs")
        help_layout.addWidget(help_label)
        youtube_btn = QPushButton("Youtube")
        youtube_btn.clicked.connect(self.redirectYoutube)
        help_layout.addWidget(youtube_btn)
        docu_btn = QPushButton("Documentation")
        docu_btn.clicked.connect(self.redirectDocumentation)
        help_layout.addWidget(docu_btn)
        help_box.setLayout(help_layout)
        general_settings_layout.addWidget(help_box,alignment=Qt.AlignTop)

        report_box = QGroupBox("")
        report_layout = QVBoxLayout()
        report_label = QLabel("Report bugs")
        report_layout.addWidget(report_label)
        report_btn = QPushButton("Report Issue")
        report_btn.clicked.connect(self.reportIssue)
        report_layout.addWidget(report_btn)
        report_box.setLayout(report_layout)


        general_settings_layout.addWidget(report_box)
        self.sound_checkbox = QCheckBox ("Alarm user of detected microplastic")
        general_settings_layout.addWidget(self.sound_checkbox)
        reset_btn = QPushButton("Reset to default")
        reset_btn.clicked.connect(self.resetToDefault)
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
        self.readSettings("user_settings.json")

    def redirectYoutube(self):
        try:
            webbrowser.open("https://www.youtube.com/@CscopeAIadmin")
        except Exception as e:
            print(f"An error occurred: {e}")

    def redirectDocumentation(self):
        try:
            webbrowser.open("https://drive.google.com/drive/folders/1ynRgDzRboQsZHpDaKJnuMKmJq-yjnt3O?usp=sharing")
        except Exception as e:
            print(f"An error occurred: {e}")

    def reportIssue(self):
        try:
            webbrowser.open("https://docs.google.com/forms/d/e/1FAIpQLSfTjx0OIVR2QpeNpzcfDlNswCdnHLNeWToTIjUAs7caHQ6bmw/viewform?usp=sf_link")
        except Exception as e:
            print(f"An error occurred: {e}")


    def resetToDefault(self):
        # Load default settings from a file
        self.setDefaultSettings("default_settings.json")


    def setDefaultSettings(self, default_file_path):
        default_settings_data = {}  # Default settings data

        if os.path.exists(default_file_path):
            with open(default_file_path, "r") as f:
                default_settings_data = json.load(f)

        # Apply default settings to the UI
        self.readSettings(default_file_path)

        # Update the settings file with the default settings
        with open("user_settings.json", "w") as f:
            json.dump(default_settings_data, f, indent=4)

    def calibration(self):
        self.calibration_clicked.emit()
        self.hide()

    def applySettings(self):

        file_path = "user_settings.json"  
        settings_data = {} 

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                settings_data = json.load(f)

        # Update the image_settings dictionary with the new image_quality
        image_settings = settings_data.get("image_settings", {})
        image_quality = self.resolution_dropbox.itemText(self.resolution_dropbox.currentIndex())
        if image_quality:
            image_settings["image_quality"] = image_quality

        image_sharpness = self.sharpness_balance_slider.value()
        if image_sharpness:
            image_settings["image_sharpness"] = image_sharpness

        image_saturation = self.saturation_balance_slider.value()
        if image_saturation:
            image_settings["image_saturation"] = image_saturation



        grbl_settings = settings_data.get("grbl_settings", {})
    
        steps_per_mm = self.steps_line_edit.text()
        if steps_per_mm:
            grbl_settings["steps_per_mm"] = float(steps_per_mm)

        max_feedrate= self.feed_line_edit.text()
        if max_feedrate:
            grbl_settings["max_feedrate"] = float(max_feedrate)

        area_scan = self.scan_overlay_checkbox.isChecked()
        if area_scan is not None:
            grbl_settings["area_scan"] = area_scan



        # For general settings
        general_features= settings_data.get("general_features", {})
        theme = self.theme_dropbox.itemText(self.theme_dropbox.currentIndex())
        if theme:
           general_features["model"] = theme

        sound = self.sound_checkbox.isChecked()
        if sound is not None:
            general_features["sound"] = sound

        # Update settings_data dictionary
        settings_data["image_settings"] = image_settings
        settings_data["grbl_settings"] = grbl_settings
        settings_data["general_features"] = general_features

        with open(file_path, "w") as f:
            json.dump(settings_data, f, indent=4) 

        self.apply_clicked.emit()

    def readSettings(self, file_path):

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                settings_data = json.load(f)

                # Image Settings
                image_settings = settings_data.get("image_settings", {})
                image_quality = image_settings.get("image_quality")
                if image_quality:
                    index = self.resolution_dropbox.findText(image_quality)
                    if index != -1:
                        self.resolution_dropbox.setCurrentIndex(index)

                image_sharpness = image_settings.get("image_sharpness")
                if image_sharpness is not None:
                    self.sharpness_balance_slider.setValue(image_sharpness)

                image_saturation = image_settings.get("image_saturation")
                if image_saturation is not None:
                    self.saturation_balance_slider.setValue(image_saturation)


                # GRBL settings
                grbl_settings = settings_data.get("grbl_settings", {})

                steps_per_mm = grbl_settings.get("steps_per_mm")
                if steps_per_mm is not None:
                    self.steps_line_edit.setText(str(steps_per_mm))

                max_feedrate = grbl_settings.get("max_feedrate")
                if max_feedrate is not None:
                    self.feed_line_edit.setText(str(max_feedrate))

                area_scan = grbl_settings.get("area_scan")
                if area_scan is not None:
                    self.scan_overlay_checkbox.setChecked(area_scan)

                # Read general features
                general_features = settings_data.get("general_features", {})
                #theme
                theme = general_features.get("model")
                if theme:
                    index = self.theme_dropbox.findText(theme)
                    if index != -1:
                        self.theme_dropbox.setCurrentIndex(index)
                #sound
                sound = general_features.get("sound", True)
                self.sound_checkbox.setChecked(sound)

def main():
    app = QApplication(sys.argv)
    settings_ui = SettingsUI()
    settings_ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()





