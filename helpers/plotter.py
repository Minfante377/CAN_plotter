import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
matplotlib.use('Qt5Agg')


class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlabel("Time offset [ms]")
        super(Canvas, self).__init__(self.fig)


class PlotCanvas(Canvas):
    def plot(self, data):
        x = data[0]
        y = data[1]
        name = data[2]
        self.axes.plot(x, y, label=name)
        self.axes.set_ylabel(name)
        self.axes.legend()
