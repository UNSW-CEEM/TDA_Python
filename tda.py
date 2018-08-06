import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QLabel, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QAction, qApp
from PyQt5 import QtGui, QtCore


class Tda(QMainWindow):
    def __init__(self):
        super().__init__()
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.gridlayout = QGridLayout()
        self.centralWidget.setLayout(self.gridlayout)
        self.init_menu()
        self.init_logos()
        self.init_select_load()
        self.show()

    def init_menu(self):
        menu_bar = self.menuBar()
        project = menu_bar.addMenu('Project')
        save_project = QAction('Save Project', self)
        save_project.setShortcut('Ctrl+S')
        project.addAction(save_project)

    def init_logos(self):
        self.ceem_logo = QLabel(self)
        image = QtGui.QPixmap('CEEMLogo.png')
        image = image.scaledToWidth(250)
        self.ceem_logo.setPixmap(image)
        self.gridlayout.addWidget(self.ceem_logo, 0,0)

        self.unsw_logo2 = QLabel(self)
        image = QtGui.QPixmap('UNSWLogo.png')
        image = image.scaledToWidth(250)
        self.unsw_logo2.setPixmap(image)
        self.gridlayout.addWidget(self.unsw_logo2, 0,2)

    def init_select_load(self):

        self.select_load = QGroupBox('Select Load')
        self.select_load.setFixedHeight(500)

        load_list = QComboBox()
        load_list.addItem('test')
        load_list.addItem('test2')
        load_list.setFixedWidth(150)

        set_button = QPushButton('Set')
        set_button.setFixedWidth(50)

        top_bar = QHBoxLayout()
        top_bar.addWidget(load_list, alignment=QtCore.Qt.AlignLeft)
        top_bar.addWidget(set_button)
        top_bar.setAlignment(QtCore.Qt.AlignTop)

        self.demographics = QGroupBox()
        self.demographics.setFlat(True)
        self.demographics.setFixedHeight(300)

        self.plot = QGroupBox()
        self.plot.setFlat(True)
        self.plot.setFixedHeight(200)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.demographics)
        layout.addWidget(self.plot)
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.select_load.setLayout(layout)
        self.gridlayout.addWidget(self.select_load, 1, 0, 1, 3)


app = QApplication(sys.argv)
writer = Tda()
sys.exit(app.exec_())