from PyQt5.QtWidgets import QWidget, QPushButton, QMainWindow, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QTabWidget
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from helpers.parser import Parser
from helpers.plotter import PlotCanvas
import os
import platform

if platform.system() == "Windows":
    SEPARATOR = "\\"
else:
    SEPARATOR = "/"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'CAN plotter tool'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.control_panel = ControlPanel()
        self.tabs.addTab(self.control_panel, "Control Panel")
        self.plot_interface = PlotInterface()
        self.control_panel.plot_button.clicked.connect(self.start_plot)
        self.tabs.addTab(self.plot_interface, "Plots")
        layout.addWidget(self.tabs)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_plot(self):
        if self.control_panel.parser:
            self.plot_interface.plot(self.control_panel.parser.get_plotting_data(
                self.control_panel.parsed_file))


class ControlPanel(QWidget):

    def __init__(self):
        super().__init__()
        import_layout = QHBoxLayout()
        self.import_label = QLabel("Select a trc file to import")
        self.import_button = QPushButton("Browse...")
        self.import_button.clicked.connect(self.browse)
        self.filename = None
        import_layout.addWidget(self.import_label)
        import_layout.addWidget(self.import_button)
        export_layout = QVBoxLayout()
        self.export_button = QPushButton("Export!")
        self.export_button.clicked.connect(self.export_to_csv)
        self.plot_button = QPushButton("Plot!")
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.plot_button)
        layout = QVBoxLayout()
        layout.addLayout(import_layout)
        layout.addLayout(export_layout)
        self.parser = None
        self.setLayout(layout)

    def browse(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select trc file", os.getcwd(),
                                                  "Tcr files(*.trc)")
        if filename:
            self.filename = filename
            self._parse_tcr_file(self.filename)

    def export_to_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Select CSV file location", os.getcwd(),
                                                  "*.csv")
        if filename:
            csv_file = open(filename, "w")
            header = "NAME, TIME OFFSET, VALUE, UNIT\n"
            csv_file.write(header)
            for data in self.parsed_file:
                line = "{},{},{},{}\n".format(data[0], data[1], data[2], data[3])
                csv_file.write(line)
            csv_file.close()

    def _parse_tcr_file(self, filename):
        self.parser = Parser(filename)
        self.parsed_file = self.parser.parse_file()
        self.import_label.setText(filename.rsplit(SEPARATOR, 1)[1])


class PlotInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.parameters = None
        self.canvas = PlotCanvas()
        self.navigation_bar = NavigationToolbar(self.canvas, self)
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addWidget(self.navigation_bar)
        self.setLayout(canvas_layout)

    def plot(self, parameters):
        self.canvas.axes.clear()
        if parameters:
            for parameter in parameters:
                self.canvas.plot(parameter)
