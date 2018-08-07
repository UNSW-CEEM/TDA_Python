import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QLabel, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QComboBox, QTableWidget
from PyQt5.QtWidgets import QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QAction, qApp, QSizePolicy
from PyQt5 import QtGui, QtCore
import images


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
        self.init_results_window()
        self.init_select_tariffs()
        self.centralWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding, )
        self.show()

    def init_menu(self):
        menu_bar = self.menuBar()
        project = menu_bar.addMenu('Project')
        save_project = QAction('Save Project', self)
        save_project.setShortcut('Ctrl+S')
        project.addAction(save_project)

    def init_logos(self):
        self.ceem_logo = QLabel(self)
        image = QtGui.QPixmap(':/CEEMLogo.png')
        self.ceem_logo.setPixmap(image)
        self.ceem_logo.setMinimumSize(50, 50)
        self.ceem_logo.setMaximumSize(250, 100)
        self.ceem_logo.setScaledContents(True)
        self.gridlayout.addWidget(self.ceem_logo, 0, 0, 1, 1)

        self.unsw_logo2 = QLabel(self)
        image = QtGui.QPixmap(':/UNSWLogo.png')
        #image = image.scaledToWidth(250)
        self.unsw_logo2.setPixmap(image)
        self.unsw_logo2.setScaledContents(True)
        self.unsw_logo2.setMinimumSize(50, 50)
        self.unsw_logo2.setMaximumSize(200, 100)
        self.gridlayout.addWidget(self.unsw_logo2, 0, 1 , 1, 1)

    def init_select_load(self):

        self.select_load = QGroupBox('Select Load')

        load_list = QComboBox()
        load_list.addItem('test')
        load_list.addItem('test2')

        set_button = QPushButton('Set')
        set_button.setFixedWidth(50)

        top_bar = QHBoxLayout()
        top_bar.addWidget(load_list, alignment=QtCore.Qt.AlignLeft)
        top_bar.addWidget(set_button)
        top_bar.setAlignment(QtCore.Qt.AlignTop)

        self.demographics = QGroupBox()
        self.demographics.setFlat(True)

        self.plot = QGroupBox()
        self.plot.setFlat(True)

        layout = QVBoxLayout()
        layout.addLayout(top_bar, 0)
        layout.addWidget(self.demographics, 1)
        layout.addWidget(self.plot, 1)
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.select_load.setLayout(layout)
        self.select_load.setMaximumWidth(500)
        self.gridlayout.addWidget(self.select_load, 1, 0, 2, 2)

    def init_results_window(self):
        self.results_window = QGroupBox('Results')
        self.gridlayout.addWidget(self.results_window, 0, 2, 2, 1)

    def init_select_tariffs(self):
        self.select_tariffs = QGroupBox('Select Tarifffs')
        table = QTableWidget( 3, 5)
        gridlayout = QGridLayout()
        gridlayout.addWidget(table)
        self.select_tariffs.setLayout(gridlayout)
        self.gridlayout.addWidget(self.select_tariffs, 2, 2, 1, 1)



app = QApplication(sys.argv)
writer = Tda()
sys.exit(app.exec_())