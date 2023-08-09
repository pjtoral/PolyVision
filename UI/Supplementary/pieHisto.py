import matplotlib.pyplot as plt
import numpy as np

def create_pie_chart(data, num_bins=5):
    # Calculate the minimum and maximum values in the data
    data_min = int(np.floor(data.min()))
    data_max = int(np.ceil(data.max()))

    # Create evenly spaced bins with whole numbers
    bin_edges = np.linspace(data_min, data_max, num_bins + 1, dtype=int)

    # Count the number of data points in each bin
    bin_counts, _ = np.histogram(data, bins=bin_edges)

    # Calculate the proportions for each bin
    bin_proportions = bin_counts / len(data)

    # Create labels with bin ranges
    bin_labels = [f'{bin_edges[i]} to {bin_edges[i + 1]}' for i in range(len(bin_proportions))]

    # Create the pie chart
    plt.figure()
    plt.pie(bin_proportions, labels=bin_labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Pie Chart for Continuous Data')
    plt.show()

if __name__ == '__main__':
    # Example usage
    data = np.random.randn(1000)  # Sample continuous data
    create_pie_chart(data, num_bins=5)
