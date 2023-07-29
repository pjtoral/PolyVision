import sys
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout
from settings_ui import SettingsUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QDialog()
    main_window.setWindowTitle("Main UI")

    settings_button = QPushButton("Settings", main_window)
    settings_button.clicked.connect(lambda: SettingsUI(main_window).exec_())

    layout = QVBoxLayout(main_window)
    layout.addWidget(settings_button)
    
    main_window.setLayout(layout)
    main_window.resize(1000, 800)
    main_window.show()
    sys.exit(app.exec_())
