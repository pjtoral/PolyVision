import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal

class MainApplication(QApplication):
    about_to_close = pyqtSignal()

    def __init__(self, sys_argv):
        super(MainApplication, self).__init__(sys_argv)
        self.confirmation_shown = False

    def notify(self, receiver, event):
        if event.type() == event.Close and not self.confirmation_shown:
            reply = QMessageBox.question(None, 'Confirmation', 'Are you sure you want to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.confirmation_shown = True  # Set the flag to prevent showing the dialog again
                self.about_to_close.emit()
                return super(MainApplication, self).notify(receiver, event)
            else:
                return False
        return super(MainApplication, self).notify(receiver, event)

class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Close Event Example')

        close_button = QPushButton('Close', self)
        close_button.setGeometry(150, 150, 100, 30)
        close_button.clicked.connect(self.close)

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Application')
        self.setGeometry(100, 100, 400, 300)

        self.main_window = MyMainWindow()

        layout = QVBoxLayout()
        layout.addWidget(self.main_window)
        self.setLayout(layout)

if __name__ == '__main__':
    app = MainApplication(sys.argv)
    main_app = MainWidget()
    app.about_to_close.connect(main_app.close)
    main_app.show()
    sys.exit(app.exec_())
