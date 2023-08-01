import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        ax.boxplot(data, vert=False)

        ax.set_title("Horizontal Box Plot and Whisker Plot")
        ax.set_xlabel("Length")
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Horizontal Box Plot and Whisker Widget Example")
        self.setGeometry(100, 100, 800, 600)

        self.box_plot_widget = BoxPlotWidget(self)

        # Example data (replace this with your own data)
        data = [1, 2, 3, 4, 5, 5, 4, 3, 5, 6, 6, 7, 8, 10, 1.2]

        self.box_plot_widget.update_plot(data)

        self.setCentralWidget(self.box_plot_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
