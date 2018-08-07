import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QLabel, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QComboBox, QTableWidget
from PyQt5.QtWidgets import QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QAction, qApp, QSizePolicy
from PyQt5 import QtGui, QtCore
from matplotlib.figure import Figure
import images
import tda_graphs


class Tda(QMainWindow):
    def __init__(self):
        # Load in info needed at start to create gui, e.g Tariff types


        # Create widget to conatain all the subwidgets and give it a grid layout.
        super().__init__()
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.gridlayout = QGridLayout()
        self.centralWidget.setLayout(self.gridlayout)

        #
        self.load_data = 0

        # Create subsection of gui, and pass them any information needed.
        self.init_menu()
        self.gridlayout.addWidget(Logo('CEEMLogo.png'), 0, 0, 1, 1)
        self.gridlayout.addWidget(Logo('UNSWLogo.png'), 0, 1, 1, 1)
        self.load_selection = LoadSelectionPanel('Select Load', self.set_load_data)
        self.gridlayout.addWidget(self.load_selection, 1, 0, 2, 2)
        self.tariff_select_panel = TariffSelectionPanel('Select Tariff')
        self.gridlayout.addWidget(self.tariff_select_panel, 2, 2, 1, 1)
        self.results_panel = ResultsPanel('Results', load_data_getter=self.give_load)
        self.gridlayout.addWidget(self.results_panel, 0, 2, 2, 1)

        # Finalise the Gui settings
        self.setGeometry(300, 300, 1000, 600)
        self.centralWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.show()

    def init_menu(self):
        menu_bar = self.menuBar()
        project = menu_bar.addMenu('Project')
        save_project = QAction('Save Project', self)
        save_project.setShortcut('Ctrl+S')
        project.addAction(save_project)

    def set_load_data(self):
        # load the data
        self.load_data += 1
        # Update demographics options
        self.demographic_options = None
        print(self.load_data)

    def give_load(self):
        return self.load_data


class Logo(QLabel):
    def __init__(self, name):
        super().__init__()
        self.setPixmap(QtGui.QPixmap(':/{}'.format(name)))
        self.setMinimumSize(50, 50)
        self.setMaximumSize(250, 100)
        self.setScaledContents(True)


class LoadSelectionPanel(QGroupBox):
    def __init__(self, name, update_load_function):
        super().__init__(name)
        load_list = QComboBox()
        load_list.addItem('test')
        load_list.addItem('test2')

        set_button = QPushButton('Set')
        set_button.clicked.connect(update_load_function)
        set_button.setFixedWidth(50)

        self.top_bar = QHBoxLayout()
        self.top_bar.addWidget(load_list, alignment=QtCore.Qt.AlignLeft)
        self.top_bar.addWidget(set_button)
        self.top_bar.setAlignment(QtCore.Qt.AlignTop)

        self.demographics = QGroupBox()
        self.demographics.setFlat(True)

        self.plot = QGroupBox()
        self.plot.setFlat(True)

        layout = QVBoxLayout()
        layout.addLayout(self.top_bar, 0)
        layout.addWidget(self.demographics, 1)
        layout.addWidget(self.plot, 1)
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.setLayout(layout)
        self.setMaximumWidth(500)


class ResultsPanel(QGroupBox):
    def __init__(self, panel_name, load_data_getter):
        super().__init__(panel_name)
        set_button = QPushButton('report load')
        set_button.clicked.connect(self.print_load)
        set_button.setFixedWidth(100)
        dual_variable_canvas = tda_graphs.DualVariablePlot()
        layout = QVBoxLayout()
        layout.addWidget(set_button)
        layout.addWidget(dual_variable_canvas)
        self.setLayout(layout)
        self.load_data_getter = load_data_getter

    def print_load(self):
        # load the data
        self.load_data = None
        # Update demographics options
        self.demographic_options = None
        print(self.load_data_getter())
        pass


class TariffSelectionPanel(QGroupBox):
    def __init__(self, name):
        super().__init__(name)
        table = QTableWidget(3, 5)
        gridlayout = QGridLayout()
        gridlayout.addWidget(table)
        self.setLayout(gridlayout)
        self.cases = None


app = QApplication(sys.argv)
x = Tda()
sys.exit(app.exec_())