from PyQt5.QtWidgets import QWidget, QPushButton, QMainWindow, QLabel, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QTabWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from helpers.parser import Parser
from helpers.plotter import PlotCanvas
from helpers import config
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
        config.init_config()
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
        self.message = QMessageBox()
        import_layout = QHBoxLayout()
        self.import_label = QLabel("Select a trc file to import")
        self.import_button = QPushButton("Browse...")
        self.import_button.clicked.connect(self.browse)
        self.parse_button = QPushButton("Parse")
        self.parse_button.clicked.connect(self._parse_tcr_file)
        self.filename = None
        import_layout.addWidget(self.import_label)
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.parse_button)
        export_layout = QVBoxLayout()
        export_layout.SetMaximumSize = 150
        self.ts_input = QLineEdit(self)
        self.ts_input.setPlaceholderText("Average Time Step (ms)")
        export_layout.addWidget(self.ts_input)
        export_layout.addLayout(import_layout)
        self.export_button = QPushButton("Export!")
        self.export_button.clicked.connect(self.export_to_csv)
        self.plot_button = QPushButton("Plot!")
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.plot_button)
        parameters_layout = QVBoxLayout()
        self.table = self._init_table()
        parameters_layout.addWidget(self.table)
        self.update_button = QPushButton("Update parameters")
        self.update_button.clicked.connect(self.update_parameters)
        parameters_layout.addWidget(self.update_button)
        layout = QHBoxLayout()
        layout.addLayout(export_layout)
        layout.addLayout(parameters_layout)
        self.parser = None
        self.setLayout(layout)

    def browse(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select trc file", os.getcwd(),
                                                  "Tcr files(*.trc)")
        if filename:
            self.filename = filename
            self.import_label.setText(filename.rsplit(SEPARATOR, 1)[1])

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
            self.message.setWindowTitle("Information!")
            self.message.setText("Data exported to CSV file.")
            self.message.show()
        else:
            self.message.setWindowTitle("Information!")
            self.message.setText("There is no file to export.")
            self.message.show()


    def update_parameters(self):
        rows = self._get_table_rows(self.table.rowCount(), self.table.columnCount())
        config.update_parameters(rows)
        self.message.setWindowTitle("Information!")
        self.message.setText("Parameters updated correctly.")
        self.message.show()

    def _get_table_rows(self, nrows, ncols):
        rows = []
        for i in range(1, nrows):
            row = []
            for j in range (0, ncols):
                item = self.table.item(i, j)
                if item:
                    if not item.text() == '':
                        row.append(item.text())
                else:
                    break
            if len(row) == ncols:
                rows.append(row)
        return rows

    def _parse_tcr_file(self, filename):
        print("Parsing...")
        if not self.filename:
            self.message.setWindowTitle("Information!")
            self.message.setText("There is no file to parse!")
            self.message.show()
            return
        self.parser = Parser(filename)
        self.parsed_file = self.parser.parse_file()
        if self.ts_input.text() == '':
            ts = 1000
        else:
            ts = float(self.ts_input.text())
        self.parsed_file = self._average(ts)
        self.message.setWindowTitle("Information!")
        self.message.setText("File parsed correctly.")
        self.message.show()

    def _average(self, ts):
        parameters = config.get_parameters()
        avg_parameters = []
        for pgn in parameters.keys():
            for parameter in parameters[pgn].keys():
                last_time = 0
                value_sum = 0
                count = 0
                for d in self.parsed_file:
                    if d[0] == parameter:
                        if float(d[1]) - last_time < ts:
                            value_sum = value_sum + float(d[2])
                            count = count + 1
                            last_time = float(d[1])
                        else:
                            if count == 0:
                                value_sum = float(d[2])
                                count = 1
                            avg_parameters.append((d[0], str(last_time), str(value_sum / count),
                                                   d[3]))
                            value_sum = 0
                            count = 0
                            last_time = float(d[1])
        return avg_parameters

    def _init_table(self):
        table = QTableWidget()
        table.setColumnCount(7)
        table.setRowCount(11)
        table.setItem(0, 0, QTableWidgetItem("Name"))
        table.setItem(0, 1, QTableWidgetItem("PGN"))
        table.setItem(0, 2, QTableWidgetItem("Multiplier"))
        table.setItem(0, 3, QTableWidgetItem("Offset"))
        table.setItem(0, 4, QTableWidgetItem("Units"))
        table.setItem(0, 5, QTableWidgetItem("Lenght"))
        table.setItem(0, 6, QTableWidgetItem("Start"))
        parameters = config.get_parameters()
        i = 1
        for pgn in parameters.keys():
            for name in parameters[pgn].keys():
                bits = parameters[pgn][name]['Bits']
                bits = bits.split("-")
                if len(bits) == 1:
                    length = "1"
                else:
                    length = str(int(bits[1]) - int(bits[0]))
                start = bits[0]
                table.setItem(i, 0, QTableWidgetItem(name))
                table.setItem(i, 1, QTableWidgetItem(pgn))
                table.setItem(i, 2, QTableWidgetItem(parameters[pgn][name]['Rate']))
                table.setItem(i, 3, QTableWidgetItem(str(parameters[pgn][name]['Offset'])))
                table.setItem(i, 4, QTableWidgetItem(parameters[pgn][name]['Measure']))
                table.setItem(i, 5, QTableWidgetItem(length))
                table.setItem(i, 6, QTableWidgetItem(start))
                i = i+1
        return table 

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
        self.message = QMessageBox()

    def plot(self, parameters):
        self.canvas.axes.clear()
        if parameters:
            for parameter in parameters:
                self.canvas.plot(parameter)
        self.message.setWindowTitle("Information!")
        self.message.setText("Plot ready!")
        self.message.show()
