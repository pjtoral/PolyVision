import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont, QPixmap, QBrush
import csv
import pandas as pd
from openpyxl import Workbook
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sqlite3
from Database import *
import numpy as np
from Charts import *

class StatisticsUI(QDialog):
    close_signal = pyqtSignal()

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        #self.file_path = "microplastic.db"
        self.setWindowTitle("Statistics")
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QHBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)  # Enable tab closing
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.shape_content_widget = QWidget()
        self.shape_content_widget.setStyleSheet("background-color: #FFFFFF;")
        self.shape_layout = QVBoxLayout(self.shape_content_widget)
        self.shape_layout.setSpacing(1)
        self.shape_layout.addStretch()
        self.color_content_widget = QWidget()
        self.color_content_widget.setStyleSheet("background-color: #FFFFFF;")
        self.color_layout = QVBoxLayout(self.color_content_widget)
        self.color_layout.setSpacing(1)
        self.color_layout.addStretch()
        self.length_content_widget = QWidget()
        self.length_content_widget.setStyleSheet("background-color: #FFFFFF;")
        self.length_layout = QVBoxLayout(self.length_content_widget)
        self.length_layout.setSpacing(1)
        self.length_layout.addStretch()
        self.width_content_widget = QWidget()
        self.width_content_widget.setStyleSheet("background-color: #FFFFFF;")
        self.width_layout = QVBoxLayout(self.width_content_widget)
        self.width_layout.setSpacing(1)
        self.width_layout.addStretch()


        layout.addWidget(self.tabs)
        self.setFixedSize(1600, 600)

        # Create the table and populate it with data
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(20)
        self.table_widget.setColumnCount(5)
        self.table_widget.setColumnWidth(4,116)


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

        right_button_layout = QVBoxLayout()
        right_button_layout.setSpacing(1)
        generate_button = QPushButton("Generate")
        clear_button = QPushButton("Clear Tabs")
        update_button = QPushButton("Update")
        self.close_button = QPushButton("Close")
        export_button = QPushButton("Export Data")
        chart_button = QPushButton("Export Chart")
        database_button = QPushButton("Database")

        right_button_layout.addWidget(type_box)
        right_button_layout.addWidget(chart_box)
        spacer_item = QSpacerItem(10, 70, QSizePolicy.Minimum, QSizePolicy.Fixed)
        right_button_layout.addItem(spacer_item)
        right_button_layout.addWidget(generate_button)
        right_button_layout.addWidget(clear_button)
        right_button_layout.addWidget(database_button)
        right_button_layout.addWidget(export_button)
        right_button_layout.addWidget(chart_button)
        right_button_layout.addWidget(update_button)
        right_button_layout.addWidget(self.close_button)

        generate_button.clicked.connect(self.initializeStats)
        clear_button.clicked.connect(self.hide_all_tabs)
        database_button.clicked.connect(self.change_database)
        export_button.clicked.connect(self.export)
        chart_button.clicked.connect(self.export_stats)
        update_button.clicked.connect(self.update)
        self.close_button.clicked.connect(self.closeUI)
        generate_button.setMinimumSize(100, 35)
        clear_button.setMinimumSize(100, 35)
        database_button.setMinimumSize(100, 35)
        export_button.setMinimumSize(100, 35)
        chart_button.setMinimumSize(100, 35)
        update_button.setMinimumSize(100, 35)
        self.close_button.setMinimumSize(100, 35)
        clear_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 13px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        generate_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 13px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")   
        database_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 13px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        export_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 13px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        chart_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 13px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        update_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 13px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        self.close_button.setStyleSheet("QPushButton {\n""    background-color: #00853f;\n""    color: #FFFFFF;\n""    font: bold 13px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")


        grid_layout = QGridLayout()
        grid_layout.addWidget(self.table_widget, 0, 0)
        grid_layout.addLayout(right_button_layout, 0, 1, alignment=Qt.AlignBottom)

        layout.addLayout(grid_layout)
        self.setLayout(layout)
        self.initializeStats()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        brush = QBrush(QColor(224, 224, 212, 255))
        painter.setBrush(brush)

        # Create a rounded rectangle for the dialog's background
        rect = self.rect()
        painter.drawRoundedRect(rect, 10, 10)

    def closeUI(self):
        self.close_signal.emit()
        self.close()

    def close_tab(self, index):
        # Close the tab requested by its index
        self.tabs.removeTab(index)
        
    def hide_all_tabs(self):
      for i in range(3, -1, -1):
        self.tabs.removeTab(i)

    def change_database(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        new_db, _ = QFileDialog.getOpenFileName(self, "Select Database", self.file_path, "SQLite Database (*.db *.sqlite)", options=options)
        if new_db:
            self.file_path= new_db
            self.initializeStats()
    

    def initializeStats(self):
        data = get_data(self.file_path)

        if(len(data)<20):
            self.table_widget.setRowCount(len(data)+10)
        else:
            self.table_widget.setRowCount(len(data))

        if self.table_widget:
            self.table_widget.clear()
            self.table_widget.setHorizontalHeaderLabels(["Particle Name","Length (mm)","Width (mm)", "Color", "Shape"])

        sizes_dict = {
            'filament': 0,
            'fragment': 0,
            'film': 0
        }
        data_length = []
        data_width = []
        color_dict = {}

        for row_index, row_data in enumerate(data):
            for column_index, cell_value in enumerate(row_data):
                
                #for length
                if column_index == 2:  
                    data_length.append(cell_value)
                #for width
                if column_index == 3:  
                    data_width.append(cell_value)
                #for color
                if column_index == 4:  
                    color = str(cell_value).strip().lower()
                    if color in color_dict:
                        color_dict[color] += 1
                    else:
                        color_dict[color] = 1
                #for shape
                if column_index == 5:
                    shape = str(cell_value).lower()
                    if 'fragment' in shape:
                        sizes_dict['fragment'] += 1
                    elif 'filament' in shape:
                        sizes_dict['filament'] += 1
                    elif 'film' in shape:
                        sizes_dict['film'] += 1

                if column_index in [1, 2, 3, 4, 5]:
                    self.table_widget.setItem(row_index, column_index - 1, QTableWidgetItem(str(cell_value)))

        
        if self.label_button_group.checkedButton() is not None and self.chart_button_group.checkedButton() is not None:
       
            if self.label_button_group.checkedButton().text() == "Shape": 
                while self.shape_layout.count():
                    item = self.shape_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                shape_label = QLabel("Shape Statistics")
                shape_label.setStyleSheet("font: bold 25px; color:rgba(0, 133, 63, 255); padding-top: 25px;")
                self.shape_layout.addWidget(shape_label, alignment=Qt.AlignHCenter | Qt.AlignBottom)

                if self.chart_button_group.checkedButton().text() == "Pie Chart":  
                    self.pie_chart_widget = PieChartWidget(self)
                    self.shape_layout.addWidget(self.pie_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.shape_content_widget,"Shape")
                    self.pie_chart_widget.update_chart(sizes_dict)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)
                elif self.chart_button_group.checkedButton().text() == "Bar Graph" or self.chart_button_group.checkedButton().text() == "Histogram": 
                    self.bar_chart_widget = BarChartWidget(self)
                    self.shape_layout.addWidget(self.bar_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.shape_content_widget,"Shape")
                    self.bar_chart_widget.update_plot(sizes_dict)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)
                elif self.chart_button_group.checkedButton().text() == "Box Plot": 
                    self.box_plot_widget = BoxPlotWidget(self)
                    self.shape_layout.addWidget(self.box_plot_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.shape_content_widget,"Shape")
                    self.box_plot_widget.update_plot_disc(sizes_dict)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)

            if self.label_button_group.checkedButton().text() == "Color":
                while self.color_layout.count():
                    item = self.color_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                color_label = QLabel("Color Statistics")
                color_label.setStyleSheet("font: bold 25px; color:rgba(0, 133, 63, 255); padding-top: 25px;")
                self.color_layout.addWidget(color_label, alignment=Qt.AlignHCenter | Qt.AlignBottom)

                if self.chart_button_group.checkedButton().text() == "Bar Graph" or self.chart_button_group.checkedButton().text() == "Histogram": 
                    self.bar_chart_widget = BarChartWidget(self)
                    self.color_layout.addWidget(self.bar_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.color_content_widget, "Color")
                    self.bar_chart_widget.update_plot(color_dict)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)
                elif self.chart_button_group.checkedButton().text() == "Pie Chart":  
                    self.pie_chart_widget = PieChartWidget(self)
                    self.color_layout.addWidget(self.pie_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.color_content_widget,"Color")
                    self.pie_chart_widget.update_chart(color_dict)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)
                elif self.chart_button_group.checkedButton().text() == "Box Plot": 
                    self.box_plot_widget = BoxPlotWidget(self)
                    self.color_layout.addWidget(self.box_plot_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.color_content_widget,"Color")
                    self.box_plot_widget.update_plot_disc(color_dict)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)


            if self.label_button_group.checkedButton().text() == "Length":
                while self.length_layout.count():
                    item = self.length_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                length_label = QLabel("Length Statistics")
                length_label.setStyleSheet("font: bold 25px; color:rgba(0, 133, 63, 255); padding-top: 25px;")
                self.length_layout.addWidget(length_label, alignment=Qt.AlignHCenter | Qt.AlignBottom)

                if self.chart_button_group.checkedButton().text() == "Box Plot":
                    self.box_plot_widget = BoxPlotWidget(self)
                    self.length_layout.addWidget(self.box_plot_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.length_content_widget, "Length")
                    self.box_plot_widget.update_plot_cont(data_length)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)

                elif self.chart_button_group.checkedButton().text() == "Bar Graph": 
                    self.bar_chart_widget = BarChartWidget(self)
                    self.length_layout.addWidget(self.bar_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.length_content_widget, "Length")
                    self.bar_chart_widget.update_plot_cont(data_length)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)

                elif self.chart_button_group.checkedButton().text() == "Pie Chart":  
                    self.pie_chart_widget = PieChartWidget(self)
                    self.length_layout.addWidget(self.pie_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.length_content_widget,"Length")
                    self.pie_chart_widget.update_chart_cont(data_length)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)

                elif self.chart_button_group.checkedButton().text() == "Histogram":  
                    self.histogram_widget = HistogramWidget(self)
                    self.length_layout.addWidget(self.histogram_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.length_content_widget,"Length")
                    self.histogram_widget.update_histogram(data_length)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)



            if self.label_button_group.checkedButton().text() == "Width":

                while self.width_layout.count():
                    item = self.width_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                width_label = QLabel("Width Statistics")
                width_label.setStyleSheet("font: bold 25px; color:rgba(0, 133, 63, 255); padding-top: 25px;")
                self.width_layout.addWidget(width_label, alignment=Qt.AlignHCenter | Qt.AlignBottom)

                if self.chart_button_group.checkedButton().text() == "Box Plot":
                    self.box_plot_widget = BoxPlotWidget(self)
                    self.width_layout.addWidget(self.box_plot_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.width_content_widget, "Width")
                    self.box_plot_widget.update_plot_cont(data_width)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)

                elif self.chart_button_group.checkedButton().text() == "Bar Graph": 
                    self.bar_chart_widget = BarChartWidget(self)
                    self.width_layout.addWidget(self.bar_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.width_content_widget, "Width")
                    self.bar_chart_widget.update_plot_cont(data_width)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)

                elif self.chart_button_group.checkedButton().text() == "Pie Chart":  
                    self.pie_chart_widget = PieChartWidget(self)
                    self.width_layout.addWidget(self.pie_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.width_content_widget,"Width")
                    self.pie_chart_widget.update_chart_cont(data_width)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)

                elif self.chart_button_group.checkedButton().text() == "Histogram":  
                    self.histogram_widget = HistogramWidget(self)
                    self.width_layout.addWidget(self.histogram_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
                    self.tabs.addTab(self.width_content_widget,"Width")
                    self.histogram_widget.update_histogram(data_width)
                    self.tabs.setTabVisible(self.tabs.count()+1, True)


    def save_widget_as_png(self, widget, filename):
        pixmap = widget.grab()
        pixmap.save(filename, "PNG")

    def export_stats(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        export_path, _ = QFileDialog.getSaveFileName(self, "Export Statistics as PNG", "", "PNG Files (*.png)", options=options)

        if export_path:
            print(export_path)

            if "exported" not in export_path:
                exported_folder = os.path.join(os.path.dirname(export_path), "exported")
                os.makedirs(exported_folder, exist_ok=True)
                export_path = os.path.join(exported_folder, os.path.basename(export_path) + ".png")
            else:
                export_path = export_path + ".png"

            selected_tab_index = self.tabs.currentIndex()
            selected_widget = self.tabs.widget(selected_tab_index)
            if selected_widget:
                self.save_widget_as_png(selected_widget, export_path)


    def export(self):
        self.file_path = "E:/THESIS/PolyVision/UI/testing"
        screenshot = self.grab()
        screenshot.save("widget_screenshot.png", "PNG")  # Save the pixmap as a PNG image
        if self.file_path:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            export_path, file_type = QFileDialog.getSaveFileName(self, "Export to CSV or Excel", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options) 
            if export_path:
                data = get_data(self.file_path)

                # Create the "exported" subfolder if it doesn't exist
                exported_folder = os.path.join(os.path.dirname(export_path), "exported")
                os.makedirs(exported_folder, exist_ok=True)
                
                # Include the filename in the export path
                if file_type == 'CSV Files (*.csv)':
                    export_path = os.path.join(exported_folder, os.path.basename(export_path) + ".csv")
                    with open(export_path, "w", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(["Image Location", "Particle Name", "Length", "Width", "Color", "Shape", "Magnification", "Note"])
                        writer.writerows(data)

                elif file_type == 'Excel Files (*.xlsx)':
                    df = pd.DataFrame(data, columns=["Image Location", "Particle Name", "Length", "Width", "Color", "Shape", "Magnification", "Note"])
                    export_path = os.path.join(exported_folder, os.path.basename(export_path) + ".xlsx")
                    with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')


    def update(self):
        clear_table_data(self.file_path)
        for row in range(self.table_widget.rowCount()):
            particle_name_item = self.table_widget.item(row, 0)
            length_item = self.table_widget.item(row, 1)
            width_item = self.table_widget.item(row, 2)
            color_item = self.table_widget.item(row, 3)
            shape_item = self.table_widget.item(row, 4)

            # Check if the items are not None before accessing their text
            if particle_name_item and length_item and width_item and color_item and shape_item:
                particle_name = particle_name_item.text()
                length = length_item.text()
                width = width_item.text()
                color = color_item.text()
                shape = shape_item.text()
                update_table_data(self.file_path, particle_name, length, width, color, shape, row+1)
            else:
                pass
        self.initializeStats()


def main():
    app = QApplication(sys.argv)
    stat_ui = StatisticsUI("testing/microplastic.db")
    stat_ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

