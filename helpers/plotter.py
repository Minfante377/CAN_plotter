import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from helpers import config
matplotlib.use('Qt5Agg')


class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(Canvas, self).__init__(self.fig)


class PlotCanvas(Canvas):
    def plot(self, data):
        self.axes.set_xlabel("Time offset [ms]")
        x = data[0]
        y = data[1]
        name = data[2]
        self.axes.plot(x, y, label=name)
        self.axes.set_ylabel(name)
        self.axes.legend()

    def plot_x_y(self, x, y, x_label, y_label):
        x_unit = config.get_unit(x_label)
        y_unit = config.get_unit(y_label)
        self.axes.set_xlabel("{} [{}]".format(x_label, x_unit))
        self.axes.set_ylabel("{} [{}]".format(y_label, y_unit))
        self.axes.plot(x, y)
