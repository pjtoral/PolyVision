import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QCheckBox, QGroupBox, QRadioButton, QButtonGroup

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        vboxLayout = QVBoxLayout(centralWidget)

        # Create radio buttons for "Label" group
        self.shape_radio = QRadioButton("Shape")
        self.color_radio = QRadioButton("Color")
        self.length_radio = QRadioButton("Length")
        self.width_radio = QRadioButton("Width")

        type_box = QGroupBox("Label")
        filters = QVBoxLayout()
        filters.addWidget(self.shape_radio)
        filters.addWidget(self.color_radio)
        filters.addWidget(self.length_radio)
        filters.addWidget(self.width_radio)
        type_box.setLayout(filters)

        # Create radio buttons for "Chart" group
        self.pie_radio = QRadioButton("Pie Chart")
        self.histo_radio = QRadioButton("Histogram")
        self.box_radio = QRadioButton("Box Plot")
        self.bar_radio = QRadioButton("Bar Graph")

        chart_box = QGroupBox("Chart")
        filters = QVBoxLayout()
        filters.addWidget(self.pie_radio)
        filters.addWidget(self.histo_radio)
        filters.addWidget(self.box_radio)
        filters.addWidget(self.bar_radio)
        chart_box.setLayout(filters)

        # Set up button groups to ensure exclusive selection within each group
        self.label_button_group = QButtonGroup()
        self.label_button_group.addButton(self.shape_radio)
        self.label_button_group.addButton(self.color_radio)
        self.label_button_group.addButton(self.length_radio)
        self.label_button_group.addButton(self.width_radio)

        self.chart_button_group = QButtonGroup()
        self.chart_button_group.addButton(self.pie_radio)
        self.chart_button_group.addButton(self.histo_radio)
        self.chart_button_group.addButton(self.box_radio)
        self.chart_button_group.addButton(self.bar_radio)

        vboxLayout.addWidget(type_box)
        vboxLayout.addWidget(chart_box)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MyMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
