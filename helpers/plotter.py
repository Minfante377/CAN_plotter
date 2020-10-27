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
    def plot(self, data, excluded):
        if data[2] in excluded:
            return
        self.axes.set_xlabel("Time offset [ms]")
        x = data[0]
        y = data[1]
        name = data[2]
        self.axes.plot(x, y, label=name)
        self.axes.set_ylabel(name)
        self.axes.legend()


class HistogramCanvas(Canvas):
    def plot(self, x, y, x_label, y_label, from_x, to_x, step_x, from_y, to_y, step_y):
        x_unit = config.get_unit(x_label)
        y_unit = config.get_unit(y_label)
        self.axes.set_xlabel("{} [{}]".format(x_label, x_unit))
        self.axes.set_ylabel("{} [{}]".format(y_label, y_unit))
        h = self.axes.hist2d(x, y, bins=[step_x, step_y], density = True,
                             range=[[from_x, to_x], [from_y, to_y]])
        self.fig.colorbar(h[3], ax=self.axes)
