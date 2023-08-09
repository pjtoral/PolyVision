import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

    def update_histogram(self, data, bins=5):
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

if __name__ == '__main__':
    # Example usage for continuous data (list)
    data = [1.2, 2.5, 3.1, 2.8, 4.0, 2.3, 1.9, 3.5, 2.7, 1.5]  # Sample data for the histogram

    app = QApplication([])
    widget = HistogramWidget()
    widget.update_histogram(data)
    widget.show()
    app.exec_()
