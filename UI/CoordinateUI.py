import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QDialog, QLabel
from PyQt5.QtGui import *
from PyQt5.QtCore import *



class RectangleWidget(QWidget):
    def __init__(self):
        super().__init__()
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.highlighted = False
        self.setMinimumSize(550, 550)
        self.circle_center = QPointF((self.width() / 2) + 30, (self.height() / 2) + 45)  # Center the circle
        self.circle_radius = 260  # Circle radius (adjust as needed)
        self.setMouseTracking(True) 
        self.sub_rectangles = []  # List to store sub-rectangles
        self.sub_rectangles_highlighted = [False] * (23 * 36)  # List to store sub-rectangle highlights

        self.smallest_x = None
        self.smallest_y = None
        self.largest_x = None
        self.largest_y = None
        self.created_rectangles = []
        self.red_points = []
        self.drawing_rectangle = False
        self.temp_rectangle = None
        self.first_point = None
        self.second_point = None

        # Calculate the number of sub-rectangles
        num_rectangles_x = 23  # Adjust the number of rectangles horizontally
        num_rectangles_y = 36  # Adjust the number of rectangles vertically

        rectangle_width = self.width() / num_rectangles_x
        rectangle_height = self.height() / num_rectangles_y

        self.coordinates = []  # List to store grid coordinates


        for row in range(num_rectangles_y):
            for col in range(num_rectangles_x):
                x = 30 + col * rectangle_width
                y = 25 + row * rectangle_height
                sub_rect = QRectF(x, y, rectangle_width, rectangle_height)
                self.sub_rectangles.append(sub_rect)

                # Calculate the coordinates
                x_coord = col * (-5)  # Adjust the scaling factor as needed
                y_coord = row * (-3)  # Adjust the scaling factor as needed
                self.coordinates.append((x_coord, y_coord))

    def toggle_highlight(self):
        self.highlighted = not self.highlighted
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if self.highlighted:
            painter.fillRect(rect, QBrush(QColor(255, 255, 255)))  # Yellow
        else:
            painter.fillRect(rect, QBrush(QColor(255, 255, 255)))  # White
        pen = QPen()
        for i, sub_rect in enumerate(self.sub_rectangles):
            pen.setColor(QColor(230, 230, 230))  # Black
            painter.setPen(pen)
            if self.sub_rectangles_highlighted[i]:
                painter.fillRect(sub_rect, QBrush(QColor(150, 255, 150)))  # Green
            else:
                painter.drawRect(sub_rect)

            x, y = self.coordinates[i]

            # Draw X coordinates above the top row and below the bottom row
            if y == 0:
                pen.setColor(QColor(150, 150, 150))  # Black
                painter.setPen(pen)
                painter.drawText(sub_rect.topLeft() + QPointF(sub_rect.width() / 2 - 15, -5), f'{abs(x)}')
            elif y == -114:
                pen.setColor(QColor(150, 150, 150))  # Black
                painter.setPen(pen)
                painter.drawText(sub_rect.bottomLeft() + QPointF(sub_rect.width() / 2 - 15, +15), f'{abs(x)}')

            # Draw Y coordinates to the left and right of the outer rectangles
            if x == 0:
                pen.setColor(QColor(150, 150, 150))  # Black
                painter.setPen(pen)
                painter.drawText(sub_rect.topLeft() + QPointF(-22, sub_rect.height() / 2 + 3), f'{abs(y)}')
            elif x == -115:
                pen.setColor(QColor(150, 150, 150))  # Black
                painter.setPen(pen)
                painter.drawText(sub_rect.topRight() + QPointF(8, sub_rect.height() / 2 + 5), f'{abs(y)}')

        # Draw the circle
        pen.setColor(QColor(255, 220, 30))  # Yellow
        painter.setPen(pen)

        # Set the circle's fill color
        fill_color = QColor(255, 220, 30, 76)  # Yellow with 30% opacity (255 * 0.3 = 76)
        brush = QBrush(fill_color)
        painter.setBrush(brush)

        # Draw the filled circle
        painter.drawEllipse(self.circle_center, self.circle_radius, self.circle_radius)

       

        # Set the circle's fill color
        fill_color = QColor(255, 0, 0)  # Yellow with 30% opacity (255 * 0.3 = 76)
        brush = QBrush(fill_color)
        painter.setBrush(brush)

        pen.setColor(QColor(255, 0, 0))  # Red color
        painter.setPen(pen)
        for point in self.red_points:
            painter.drawRect(point)
        

         # Set the circle's fill color
        fill_color = QColor(150, 255, 150, 76)  # Yellow with 30% opacity (255 * 0.3 = 76)
        brush = QBrush(fill_color)
        painter.setBrush(brush)

        if self.drawing_rectangle:
            pen.setColor(QColor(0, 0, 0))
            painter.setPen(pen)
            painter.drawRect(self.temp_rectangle)

        # Draw the created rectangles
        for rect in self.created_rectangles:
            pen.setColor(QColor(0, 0, 0))  # Black
            painter.setPen(pen)
            painter.drawRect(rect)
            self.created_rectangles = []
            self.red_points = []


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print('here first')
            index = self.find_sub_rectangle_index(event.pos())
            if index is not None:
                if self.first_point is None:
                    print('first point')
                    self.add_red_point(self.coordinates[index])
                    self.drawing_rectangle = True
                    self.temp_rectangle = QRectF(self.first_point, self.first_point)
                    self.update()
                else:
                    print('here 3')
                    self.drawing_rectangle = False
                    self.add_red_point(self.coordinates[index])
                    self.create_rectangle()
            self.update()

            x, y = self.coordinates[index]
            print(f'''Grid at ({x},{y}) is highlighted.''')
            if self.smallest_x is None or x < self.smallest_x:
                self.smallest_x = x
            if self.smallest_y is None or y < self.smallest_y:
                self.smallest_y = y
            if self.largest_x is None or x > self.largest_x:
                self.largest_x = x
            if self.largest_y is None or y > self.largest_y:
                self.largest_y = y
            print(self.smallest_x, self.smallest_y)
            print(self.largest_x, self.largest_y)
    
    def mouseMoveEvent(self, event):
        if self.drawing_rectangle:
            self.second_point = event.pos()
            self.temp_rectangle = QRectF(self.first_point, self.second_point)
            self.update()

    def find_sub_rectangle_index(self, pos):
        for i, sub_rect in enumerate(self.sub_rectangles):
            if sub_rect.contains(pos):
                return i
        return None

    def add_red_point(self, position):
        if len(self.red_points) < 3:
            if len(self.red_points) == 1:
                print('here 2')
                x, y = position
                print(x,y)
                pos_x = (30 + 27.826086956521735) + (x / 5) * -1 * 27.8261
                pos_y = (25 + 15.277777777777779) + (y / 3) * -1 * 15.2778
                self.second_point = QPointF(pos_x, pos_y)
                red_point = QRectF(self.second_point.x() , self.second_point.y(), -3, -3)
                self.red_points.append(red_point)
            if len(self.red_points) == 0:
                self.smallest_x = None
                self.smallest_y = None
                self.largest_x = None
                self.largest_y = None
                self.created_rectangles = []
                print('here')
                x, y = position
                print(x,y)
                pos_x = 30 + (x / 5) * -1 * 27.8261
                pos_y = 25 + (y / 3) * -1 * 15.2778
                self.first_point = QPointF(pos_x, pos_y)
                red_point = QRectF(self.first_point.x() , self.first_point.y(), 3, 3)
                self.red_points.append(red_point)


    def create_rectangle(self):
        if self.first_point is not None and self.second_point is not None:
            x1, y1 = self.first_point.x(), self.first_point.y()
            x2, y2 = self.second_point.x(), self.second_point.y()

            # Ensure that x1 < x2 and y1 < y2
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)

            # Create a QRectF representing the rectangle
            rectangle = QRectF(x1, y1, x2 - x1, y2 - y1)

            # Store the created rectangle
            self.created_rectangles.append(rectangle)

            # Clear the selected points
            self.first_point = None
            self.second_point = None
            # Update the widget to draw the new rectangle
            self.update()

    def refresh_highlights(self):
        for i in range(len(self.sub_rectangles_highlighted)):
            self.sub_rectangles_highlighted[i] = False
        self.update()
        self.smallest_x = None
        self.smallest_y = None
        self.largest_x = None
        self.largest_y = None
        self.created_rectangles = []


    def highlight_all_rectangles(self):
        for i in range(len(self.sub_rectangles_highlighted)):
            self.sub_rectangles_highlighted[i] = True
        self.update()
        self.smallest_x = -120
        self.smallest_y = -115
        self.largest_x = 0
        self.largest_y = 0

class CoordinateUI(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.smallest_x = None
        self.smallest_y = None
        self.largest_x = None
        self.largest_y = None
        self.distance_x = None
        self.distance_y = None

    def initUI(self):
        layout = QVBoxLayout()  # Use QVBoxLayout for buttons

        self.rectangle_widget = RectangleWidget()
        layout.addWidget(self.rectangle_widget)
        self.rectangle_widget.setWhatsThis("Highlight a grid you want to scan.\nHighlight 4 grids (that form a square) to scan a specific area.")


        button_layout = QHBoxLayout()

        refresh_button = QPushButton("Refresh Highlights")
        refresh_button.clicked.connect(self.rectangle_widget.refresh_highlights)
        refresh_button.setWhatsThis("Click this button to refresh the highlights.")
        button_layout.addWidget(refresh_button)

        highlight_all_button = QPushButton("Highlight All")
        highlight_all_button.clicked.connect(self.rectangle_widget.highlight_all_rectangles)
        highlight_all_button.setWhatsThis("Click this button to scan whole area")
        button_layout.addWidget(highlight_all_button)

        okay_button = QPushButton("Finished")
        okay_button.clicked.connect(self.close_app)
        button_layout.addWidget(okay_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setWindowTitle("Grid Coordinates")
        self.setMinimumSize(713, 650)


    def close_app(self):
        self.smallest_x = self.rectangle_widget.smallest_x
        self.smallest_y = self.rectangle_widget.smallest_y
        self.largest_x = self.rectangle_widget.largest_x
        self.largest_y = self.rectangle_widget.largest_y
        print("here")
        print(self.smallest_x, self.smallest_y)
        print(self.largest_x, self.largest_y)
        self.distance_x = (abs(self.largest_x - self.smallest_x) / 5) + 1  # Assuming 5 units per rectangle in X-axis PLUS margin of error 1
        self.distance_y = (abs(self.largest_y - self.smallest_y) / 3) + 1  # Assuming 3 units per rectangle in Y-axis PLUS margin of error 1

        print(f"Distance in terms of rectangles (X): {self.distance_x}")
        print(f"Distance in terms of rectangles (Y): {self.distance_y}")
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    square_app = CoordinateUI()
    square_app.show()
    sys.exit(app.exec_())
