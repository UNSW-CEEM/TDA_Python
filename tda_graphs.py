from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy
from numpy import arange, sin, pi
import pandas as pd

class StandardCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        #self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class DualVariablePlot(StandardCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)


class LoadPlot(StandardCanvas):
    """Simple canvas with a sine plot."""
    def __init__(self, type, get_data_function):
        super().__init__()
        self.types = {'Annual Average Profile': self.annual_average}
        self.data = None
        if get_data_function is not None:
            self.types[type](get_data_function)

    def annual_average(self, get_data_function):
        data = get_data_function()
        if data is not None:
            load_ids = [column for column in data.columns if column != 'TimeStamp']
            self.data = pd.melt(data, id_vars='TimeStamp', value_vars=load_ids, var_name='IDs', value_name='Load')
            print('grouping')
            self.data = self.data.groupby('TimeStamp', as_index=False).mean()
            print('ploting')
            self.axes.plot(self.data['TimeStamp'].iloc[:], self.data['Load'].iloc[:])
            print('done')