from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy
from numpy import arange, sin, pi
import pandas as pd
import pyqtgraph
import numpy as np
import matplotlib.dates as mdates


class StandardCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class DualVariablePlot(StandardCanvas):
    def __init__(self):
        super().__init__()
        self.compute_initial_figure()

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.00001)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)


class LoadPlot(StandardCanvas):
    def __init__(self, type, get_data_function):
        super().__init__()
        # Create all the pot features that are the same for every plot.
        self.types = {'Annual Average Profile': self.annual_average}
        self.data = None
        # If a real plot type is given then create that plot.
       # self.compute_initial_figure()
        if get_data_function is not None:
            self.types[type](get_data_function)

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.00001)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)

    def annual_average(self, get_data_function):
        data = get_data_function()
        if data is not None:
            load_ids = [column for column in data.columns if column != 'TimeStamp']
            self.data = pd.melt(data, id_vars='TimeStamp', value_vars=load_ids, var_name='IDs', value_name='Load')
            print('grouping')
            self.data = self.data.groupby('TimeStamp', as_index=False).mean()
            print('ploting')
            self.data['TimeStamp'] = pd.to_datetime(self.data['TimeStamp'], format='%d/%m/%Y %H:%M')
            self.data = self.data.sort_values('TimeStamp')
            self.axes.plot(self.data['TimeStamp'], self.data['Load'])
            self.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
            self.axes.tick_params(labelsize=7)
            print('done')


class LoadPlot2():
    def __init__(self, type, get_data_function):
        # Create all the pot features that are the same for every plot.
        self.types = {'Annual Average Profile': self.annual_average,
                      'Blank': self.blank}
        self.data = None
        # If a real plot type is given then create that plot.
        if get_data_function is not None:
            self.types[type](get_data_function)

    def blank(self):
        x = np.asarray([])
        y = np.asarray([])
        return pyqtgraph.plot(x, y, pen=None, symbol='o')

    def annual_average(self, get_data_function):
        data = get_data_function()
        load_ids = [column for column in data.columns if column != 'TimeStamp']
        data = pd.melt(data, id_vars='TimeStamp', value_vars=load_ids, var_name='IDs', value_name='Load')
        data = data.groupby('TimeStamp', as_index=False).mean()
        x = np.asarray(data['TimeStamp'])
        y = np.asarray(data['Load'])
        return pyqtgraph.plot(x, y, pen=None, symbol='o')