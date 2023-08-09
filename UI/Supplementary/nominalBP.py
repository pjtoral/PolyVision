import matplotlib.pyplot as plt

# Sample nominal data
data = ['Category A', 'Category A', 'Category A', 'Category B', 'Category B', 'Category C']

# Count the occurrences of each category
categories = set(data)
category_counts = [data.count(category) for category in categories]

# Create the figure and axis (subplot)
fig, ax = plt.subplots()

# Create the box-and-whisker plot
box_plot = ax.boxplot(category_counts, vert=False, patch_artist=True)

# Customizing the box plot colors and style
box_color = 'skyblue'
whisker_color = 'black'
median_color = 'red'
box_plot['boxes'][0].set_facecolor(box_color)
box_plot['whiskers'][0].set_color(whisker_color)
box_plot['whiskers'][1].set_color(whisker_color)
box_plot['caps'][0].set_color(whisker_color)
box_plot['caps'][1].set_color(whisker_color)
box_plot['medians'][0].set_color(median_color)

# Set labels for x and y axes
ax.set_xlabel('Frequency')
ax.set_ylabel('Categories')

# Set title for the plot
ax.set_title('Box-and-Whisker Plot for Nominal Data')

# Set the y-axis ticks and labels
ax.set_yticks(range(1, len(categories) + 1))
ax.set_yticklabels(categories)

# Center the plot in the figure
fig.tight_layout()

# Show the plot
plt.show()
