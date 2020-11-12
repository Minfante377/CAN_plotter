import random
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from helpers import config
matplotlib.use('Qt5Agg')


class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = []
        super(Canvas, self).__init__(self.fig)


class PlotCanvas(Canvas):
    def __init(self):
        self.offset = 0
        self.axes = []

    def plot(self, parameters, excluded):
        lines = []
        self.axes = []
        self.offset = 1.0
        for data in parameters:
            if data[2] in excluded:
                continue
            x = data[0]
            y = data[1]
            name = data[2]
            if self.axes:
                ax = self.axes[0].twinx()
                ax.get_xaxis().set_visible(False)
                ax.spines['right'].set_position(("axes", self.offset))
                self.offset += 0.15
                ax.spines['right'].set_visible(True)
            else:
                ax = self.fig.add_subplot()
                ax.get_xaxis().set_visible(True)
                self.fig.subplots_adjust(right=0.75)
            color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
            self.axes.append(ax)
            p, = self.axes[-1].plot(x, y, label=name, color=color)
            self.axes[-1].set_ylabel(name)
            self.axes[-1].yaxis.label.set_color(color)
            self.axes[-1].tick_params(axis='y', colors=color)
            lines.append(p)
        self.fig.legend(lines, [l.get_label() for l in lines])
        for axe in self.axes:
            axe.autoscale()

class HistogramCanvas(Canvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def plot(self, x, y, x_label, y_label, from_x, to_x, step_x, from_y, to_y, step_y):
        self.axes = self.fig.add_subplot(111)
        x_unit = config.get_unit(x_label)
        y_unit = config.get_unit(y_label)
        self.axes.set_xlabel("{} [{}]".format(x_label, x_unit))
        self.axes.set_ylabel("{} [{}]".format(y_label, y_unit))
        h = self.axes.hist2d(x, y, bins=[step_x, step_y], density = True,
                             range=[[from_x, to_x], [from_y, to_y]])
        self.fig.colorbar(h[3], ax=self.axes)
