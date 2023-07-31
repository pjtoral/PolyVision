import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QResizeEvent, QTransform
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QResizeEvent, QCursor
from PyQt5.QtCore import Qt, pyqtSlot, QUrl
from PyQt5.QtGui import QDesktopServices
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
from Database import *
from functools import partial
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt
import sqlite3
import csv
import pandas as pd
from openpyxl import Workbook
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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
            self.ax.patches.clear()
            self.pie_chart = None

        self.ax = self.figure.add_subplot(111)

        # Workaround: Set text properties to avoid divide-by-zero bug
        text_props = {'fontsize': 8, 'color': 'black'}

        self.pie_chart = self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops=text_props)
        self.ax.axis('equal')
        self.canvas.draw()


class StatisticsUI(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistics UI Widget")
        self.setFixedSize( 1400, 900)

        layout = QVBoxLayout()

        # Current file path label
        self.file_path_label = QLabel("Current File Path:")
        layout.addWidget(self.file_path_label)

        # Button to change current path
        self.change_path_button = QPushButton("Change Path")
        self.change_path_button.clicked.connect(self.change_path)
        layout.addWidget(self.change_path_button)

        # Current database label
        self.database_label = QLabel("Current Database:")
        layout.addWidget(self.database_label)

        # Button to export database to CSV
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_to_csv)
        layout.addWidget(self.export_button)

        # Button to change current database
        self.change_db_button = QPushButton("Change Database")
        self.change_db_button.clicked.connect(self.change_database)
        layout.addWidget(self.change_db_button)

        # Summary statistics labels
        self.summary_label = QLabel("Summary Statistics:")
        layout.addWidget(self.summary_label)

        self.filaments_label = QLabel("Filaments:")
        layout.addWidget(self.filaments_label)

        self.fragments_label = QLabel("Fragments:")
        layout.addWidget(self.fragments_label)

        self.film_count_label = QLabel("Films:")
        layout.addWidget(self.film_count_label)

         # Create the PieChartWidget instance
        self.pie_chart_widget = PieChartWidget(self)

        # Add PieChartWidget to the layout
        
        # ... add other widgets to the layout ...
        layout.addWidget(self.pie_chart_widget)  # Add the PieChartWidget here
        self.setLayout(layout)
        self.update_pie_chart_button = QPushButton("Update Pie Chart")
        self.update_pie_chart_button.clicked.connect(self.update_pie_chart_data)
        layout.addWidget(self.update_pie_chart_button)
        self.setLayout(layout)
       
        # Placeholder variables for file path and database name
        self.current_file_path = ""
        self.current_database = ""

    def update_pie_chart(self, labels, sizes):
        print("Labels:", labels)
        print("sizes", sizes)
        self.pie_chart_widget.update_chart(labels, sizes)


    def update_pie_chart_data(self):
        # Replace this example data with your summary statistics data
        labels = ['Filaments', 'Fragments', 'Film']
        sizes = [650, 300, 100]
        self.update_pie_chart(labels, sizes)

    def change_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        new_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if new_path:
            self.current_file_path = new_path
            self.file_path_label.setText("Current File Path: " + new_path)

    def change_database(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        new_db, _ = QFileDialog.getOpenFileName(self, "Select Database", "", "SQLite Database (*.db *.sqlite)", options=options)
        if new_db:
            self.current_database = new_db
            self.database_label.setText("Current Database: " + new_db)

    def export_to_csv(self):
        if self.current_database:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            export_path, file_type = QFileDialog.getSaveFileName(self, "Export to CSV or Excel", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
            print(file_type)
            print(export_path)
            if export_path:
                conn = sqlite3.connect(self.current_database)
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM microplastics")
                data = cursor.fetchall()

                conn.close()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatisticsUI()
    window.show()
    sys.exit(app.exec_())