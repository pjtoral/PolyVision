import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QIcon
class TabBar(QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

class VerticalTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar())
        self.setTabPosition(QtWidgets.QTabWidget.West)

class SettingsUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon("res/PolyVisionLogo.png"))
        layout = QVBoxLayout()

        
        tabs = VerticalTabWidget()
        tabs.addTab(QWidget(), "General")
        tabs.addTab(QWidget(), "Images")
        tabs.addTab(QWidget(), "GRBL")
        layout.addWidget(tabs)

        self.setLayout(layout)
        self.resize(1000, 800)
        # Apply and Close buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.applySettings)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addStretch(1)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.close_button)


    def applySettings(self):
        # Implement the logic to apply the settings here
        print("Settings applied")
