import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
import numpy as np
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

    def update_chart(self, data_dict):
        sizes = data_dict.values()
        if not sizes or all(size <= 0 for size in sizes):
            print("Invalid data for pie chart")
            return

        labels = list(data_dict.keys())

        if self.pie_chart:
            self.figure.clear()
            self.pie_chart = None

        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')
        text_props = {'fontsize': 10, 'color': 'black'}
        self.pie_chart = self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops=text_props)
        self.ax.axis('equal')
        self.canvas.draw()

    def update_chart_cont(self, data, num_bins = 5):
        # Calculate the minimum and maximum values in the data
        data_min = int(np.floor(min(data)))
        data_max = int(np.ceil(max(data)))

        # Create evenly spaced bins with whole numbers
        bin_edges = np.linspace(data_min, data_max, num_bins + 1, dtype=int)

        # Count the number of data points in each bin
        bin_counts, _ = np.histogram(data, bins=bin_edges)

        # Calculate the proportions for each bin
        bin_proportions = bin_counts / len(data)

        # Create labels with bin ranges
        bin_labels = [f'{bin_edges[i]} to {bin_edges[i + 1]} mm' for i in range(len(bin_proportions))]

        if self.pie_chart:
            self.figure.clear()
            self.pie_chart = None

        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')
        text_props = {'fontsize': 10, 'color': 'black'}
        self.pie_chart = self.ax.pie(bin_proportions, labels=bin_labels, autopct='%1.1f%%', startangle=90, textprops=text_props)
        self.ax.axis('equal')
        self.canvas.draw()

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

    def update_histogram(self, data, bins=10):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.clear()

        if not data:
            return

        # Plot the histogram
        ax.hist(data, bins=bins, alpha=0.75, edgecolor='black')

        # Set labels and title
        ax.set_xlabel('Values')
        ax.set_ylabel('Frequency')
        ax.set_title('Histogram')

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

    def update_plot_cont(self, data, num_bins=10):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.clear()

        if not data:
            return

        # Create evenly spaced bins with whole numbers
        bin_edges = np.linspace(min(data), max(data), num_bins + 1)

        # Count the number of data points in each bin
        bin_counts, _ = np.histogram(data, bins=bin_edges)

        # Calculate the proportions for each bin
        bin_height_scale = max(bin_counts)

        # Draw the bars
        for i, bin_count in enumerate(bin_counts):
            x = i
            y = 0
            bar_height = bin_count * bin_height_scale / max(bin_counts)

            ax.bar(x, bar_height, width=1.0, bottom=y, color='green')

        # Set X and Y-axis limits
        ax.set_xlim(-0.5, len(bin_counts) - 0.5)
        ax.set_ylim(0, max(bin_counts))

        # Draw X-axis and Y-axis
        ax.axhline(y=0, color='k')
        ax.axvline(x=-0.5, color='k')

        # Set X-axis and Y-axis labels
        bin_labels = [f'{int(bin_edges[i])} to {int(bin_edges[i + 1])}' for i in range(len(bin_counts))]
        ax.set_xticks([i for i in range(len(bin_counts))])
        ax.set_xticklabels(bin_labels, rotation=45, ha='right')
        ax.set_xlabel("Bins")
        ax.set_ylabel("Frequency")

        self.canvas.draw()
        

class BoxPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def update_plot_cont(self, data):
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

    def update_plot_disc(self, data_dict):
        # Clear the previous plot
        self.figure.clear()

        # Create a new subplot
        ax = self.figure.add_subplot(111)

        # Extract the categories and counts from the data_dict
        categories = list(data_dict.keys())
        category_counts = list(data_dict.values())

        # Create the box-and-whisker plot
        box_plot = ax.boxplot(category_counts, vert=False, widths=0.25, patch_artist=True)

        # Customizing the box plot colors and style
        box_color = 'green'
        whisker_color = 'black'
        median_color = 'red'
        for box in box_plot['boxes']:
            box.set(facecolor=box_color)
        for whisker in box_plot['whiskers']:
            whisker.set(color=whisker_color, linewidth=1.5)
        for median in box_plot['medians']:
            median.set(color=median_color, linewidth=2)

        # Set labels for x and y axes
        ax.set_xlabel('Frequency')


        # Set the y-axis ticks and labels
        ax.set_yticks(range(1, len(categories) + 1))
        ax.set_yticklabels(categories)

        # Center the plot in the figure
        #self.figure.tight_layout()

        # Redraw the canvas to update the plot
        self.canvas.draw()


