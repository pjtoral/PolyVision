import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
import csv
import pandas as pd
from openpyxl import Workbook
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sqlite3
from Database import *

class PieChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)
        self.pie_chart = None

    def update_chart(self, labels, sizes):
        # Check if the sizes list is empty or contains only non-positive values
        if not sizes or all(size <= 0 for size in sizes):
            # Handle empty or invalid data scenario (e.g., display a message)
            print("Invalid data for pie chart")
            return

        if self.pie_chart:
            # Remove the previous pie chart
            self.figure.clear()
            self.pie_chart = None

        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off') 
        text_props = {'fontsize': 10, 'color': 'black'}
        self.pie_chart = self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops=text_props)
        self.ax.axis('equal')
        self.canvas.draw()

class BarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

    def update_plot(self, data_dict):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.clear()

        if not data_dict or len(data_dict) == 0:
            return

        categories = list(data_dict.keys())
        counts = list(data_dict.values())
        max_value = max(counts)
        if max_value == 0:
            return

        chart_width = len(data_dict)  # Adjusting the width for better spacing between bars
        chart_height = max_value
        bar_width = 0.8
        bar_height_scale = chart_height / max_value

        # Draw the bars
        for i, category in enumerate(categories):
            x = i
            y = 0
            bar_height = data_dict[category] * bar_height_scale

            ax.bar(x, bar_height, width=bar_width, bottom=y, color='green')

        # Set X and Y-axis limits
        ax.set_xlim(-0.5, chart_width - 0.5)
        ax.set_ylim(0, chart_height)

        # Draw X-axis and Y-axis
        ax.axhline(y=0, color='k')
        ax.axvline(x=-0.5, color='k')

        # Set X-axis and Y-axis labels
        ax.set_xticks([i for i in range(len(data_dict))])
        ax.set_xticklabels(categories)
        ax.set_xlabel("Categories")
        ax.set_ylabel("Values")

        self.canvas.draw()

class BoxPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def update_plot(self, data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Rotate the plot to be horizontal
        box_plot = ax.boxplot(data, vert=False, widths=0.25, patch_artist=True)

        
        for box in box_plot['boxes']:
            box.set(facecolor='green')
        for whisker in box_plot['whiskers']:
            whisker.set(color='black', linewidth=1.5) 
        for median in box_plot['medians']:
            median.set(color='red', linewidth=2)  

        ax.set_xlabel("Measurement")
        self.canvas.draw()


class StatisticsUI(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle("Statistics")
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        layout = QHBoxLayout()
        self.tabs = QTabWidget()


        shape_content_widget = QWidget()
        shape_content_widget.setStyleSheet("background-color: #FFFFFF;")
        self.shape_layout = QVBoxLayout(shape_content_widget)
        shape_label = QLabel("Shape Statistics")
        shape_label.setStyleSheet("font: bold 25px; color:rgba(0, 133, 63, 255); padding-top: 25px;")
        self.shape_layout.addWidget(shape_label, alignment=Qt.AlignHCenter | Qt.AlignBottom)
        self.shape_layout.setSpacing(1)
        self.pie_chart_widget = PieChartWidget(self)
        self.shape_layout.addWidget(self.pie_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.shape_layout.addStretch()


        color_content_widget = QWidget()
        color_content_widget.setStyleSheet("background-color: #FFFFFF;")
        self.color_layout = QVBoxLayout(color_content_widget)
        color_label = QLabel("Color Statistics")
        color_label.setStyleSheet("font: bold 25px; color:rgba(0, 133, 63, 255); padding-top: 25px;")
        self.color_layout.addWidget(color_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.color_layout.setSpacing(1)
        self.bar_chart_widget = BarChartWidget(self)
        self.color_layout.addWidget(self.bar_chart_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.color_layout.addStretch()


        length_content_widget = QWidget()
        length_content_widget.setStyleSheet("background-color: #FFFFFF;")
        self.length_layout = QVBoxLayout(length_content_widget)
        length_label = QLabel("Length Statistics")
        length_label.setStyleSheet("font: bold 25px; color:rgba(0, 133, 63, 255); padding-top: 25px;")
        self.length_layout.addWidget(length_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.length_layout.setSpacing(1)
        self.box_plot_widget_length = BoxPlotWidget(self)
        self.length_layout.addWidget(self.box_plot_widget_length, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.length_layout.addStretch()

        width_content_widget = QWidget()
        width_content_widget.setStyleSheet("background-color: #FFFFFF;")
        self.width_layout = QVBoxLayout(width_content_widget)
        width_label = QLabel("Width Statistics")
        width_label.setStyleSheet("font: bold 25px; color:rgba(0, 133, 63, 255); padding-top: 25px;")
        self.width_layout.addWidget(width_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.width_layout.setSpacing(1)
        self.box_plot_widget_width = BoxPlotWidget(self)
        self.width_layout.addWidget(self.box_plot_widget_width, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.width_layout.addStretch()

        self.tabs.addTab(shape_content_widget,"Shape")   # Add to Shape Tab
        self.tabs.addTab(color_content_widget, "Color")   # Add to Color Tab
        self.tabs.addTab(length_content_widget, "Length")  # Add to Length Tab
        self.tabs.addTab(width_content_widget, "Width")


        layout.addWidget(self.tabs)
        self.setFixedSize(1600, 600)

        # Create the table and populate it with data
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(20)
        self.table_widget.setColumnCount(5)
        self.table_widget.setColumnWidth(7,348)
        self.table_widget.setHorizontalHeaderLabels(["Particle Name","Length","Width", "Color", "Shape"])


        left_button_layout = QVBoxLayout()
        left_button_layout.setSpacing(1)
        export_button = QPushButton("Export")
        database_button = QPushButton("Database")
        left_button_layout.addWidget(database_button)
        left_button_layout.addWidget(export_button)
        #left_button_layout.addStretch(10)


        right_button_layout = QVBoxLayout()
        right_button_layout.setSpacing(1)
        update_button = QPushButton("Update")
        close_button = QPushButton("Close")
        right_button_layout.addWidget(database_button)
        right_button_layout.addWidget(export_button)
        right_button_layout.addWidget(update_button)
        right_button_layout.addWidget(close_button)
        #right_button_layout.addStretch(10)
        database_button.clicked.connect(self.change_database)
        export_button.clicked.connect(self.export)
        update_button.clicked.connect(self.update)
        close_button.clicked.connect(self.close)
        database_button.setMinimumSize(100, 40)
        export_button.setMinimumSize(100, 40)
        update_button.setMinimumSize(100, 40)
        close_button.setMinimumSize(100, 40)
        database_button.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        export_button.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        update_button.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")
        close_button.setStyleSheet("QPushButton {\n""    background-color: #fbbf16;\n""    color: #FFFFFF;\n""    font: bold 15px;\n""    border-radius: 5px;\n""    border-color: #fbbf16;\n""}\n""QPushButton:hover {\n""    background-color: #9e780e;\n""}")

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.table_widget, 0, 0)
        grid_layout.addLayout(right_button_layout, 0, 1, alignment=Qt.AlignBottom)

        layout.addLayout(grid_layout)
        self.setLayout(layout)
        self.initializeStats()

    def update_pie_chart_data(self, sizes):
        labels = ['Filaments', 'Fragments', 'Film']
        self.pie_chart_widget.update_chart(labels, sizes)

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
            self.table_widget.setHorizontalHeaderLabels(["Particle Name","Length","Width", "Color", "Shape"])

        fragments_count = 0
        filaments_count = 0
        films_count = 0
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
                        fragments_count += 1
                    elif 'filament' in shape:
                        filaments_count += 1
                    elif 'film' in shape:
                        films_count += 1

                if column_index in [1, 2, 3, 4, 5]:
                    self.table_widget.setItem(row_index, column_index - 1, QTableWidgetItem(str(cell_value)))

        
        #For Length statistics
        self.box_plot_widget_length.update_plot(data_length)
        #For Width statistics
        self.box_plot_widget_width.update_plot(data_width)
        #For color statistics
        self.bar_chart_widget.update_plot(color_dict)
        #For shape statistics 
        sizes = [filaments_count, fragments_count, films_count]
        self.update_pie_chart_data(sizes)

    def export(self):
        if self.file_path:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            export_path, file_type = QFileDialog.getSaveFileName(self, "Export to CSV or Excel", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
            print(file_type)
            print(export_path)
            if export_path:
                data = get_data(self.file_path)

                if file_type == 'CSV Files (*.csv)':
                    with open(export_path, "w", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(["Image Location", "Particle Name", "Length", "Width", "Color", "Shape", "Magnification", "Note"])
                        writer.writerows(data)
                elif file_type == 'Excel Files (*.xlsx)':
                    df = pd.DataFrame(data, columns=["Image Location", "Particle Name", "Length", "Width", "Color", "Shape", "Magnification", "Note"])
                    export_path = export_path + ".xlsx"
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
                print(particle_name, length, width, color, shape)
                update_table_data(self.file_path, particle_name, length, width, color, shape, row+1)
            else:
                pass
        self.initializeStats()

