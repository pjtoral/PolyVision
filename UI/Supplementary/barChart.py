import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

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

if __name__ == '__main__':
    # Sample data for the bar chart as a dictionary containing category and count
    data_dict = {'A': 15, 'B': 30, 'C': 45, 'D': 20, 'E': 60}

    app = QApplication(sys.argv)
    widget = BarChartWidget()
    widget.resize(400, 300)
    widget.show()

    # Update the data and call update_plot after showing the widget
    widget.update_plot(data_dict)

    sys.exit(app.exec_())
