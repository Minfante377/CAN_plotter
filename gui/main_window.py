from PyQt5.QtWidgets import QWidget, QPushButton, QMainWindow, QLabel, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QTabWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QCheckBox, QComboBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from helpers.parser import Parser
from helpers.plotter import PlotCanvas, HistogramCanvas
from helpers import config
import statistics
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
        self.histogram_interface = HistogramInterface()
        self.tabs.addTab(self.histogram_interface, "Histograms")
        layout.addWidget(self.tabs)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_plot(self):
        if self.control_panel.parser:
            plotting_data = self.control_panel.parser.get_plotting_data(
                    self.control_panel.parsed_file)
            x_label = self.control_panel.x_box.currentText()
            y_label = self.control_panel.y_box.currentText()
            try:
                from_x = float(self.control_panel.from_x.text())
                to_x = float(self.control_panel.to_x.text())
                step_x = int(self.control_panel.step_x.text())
                from_y = float(self.control_panel.from_y.text())
                to_y = float(self.control_panel.to_y.text())
                step_y = int(self.control_panel.step_y.text())
            except Exception as e:
                print(e)
                from_x = 0.0
                to_x = 0.0
                step_x = 0.0
                from_y = 0.0
                to_y = 0.0
                step_y = 0.0
            if self.control_panel.histogram_check.isChecked():
                selectable = self.control_panel.selectable_box.currentText()
                self.histogram_interface.get_mean_sd(self.control_panel.parsed_file, x_label,
                                                     y_label, from_x, to_x, step_x, from_y, to_y,
                                                     step_y, selectable)
            self.histogram_interface.plot_x_y(plotting_data, x_label, y_label, from_x, to_x,
                                              step_x, from_y, to_y, step_y, selectable)
            excluded = config.get_excluded_from_plotting()
            self.plot_interface.plot(plotting_data, excluded)


class ControlPanel(QWidget):

    def __init__(self):
        super().__init__()
        self.message = QMessageBox()
        import_layout = QHBoxLayout()
        self.import_label = QLabel("Select a trc file to import")
        self.import_label.setMaximumWidth(200)
        self.import_button = QPushButton("Browse...")
        self.import_button.clicked.connect(self.browse)
        self.parse_button = QPushButton("Parse")
        self.parse_button.clicked.connect(self._parse_tcr_file)
        self.filename = None
        import_layout.addWidget(self.import_label)
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.parse_button)
        export_layout = QVBoxLayout()
        self.ts_input = QLineEdit(self)
        self.ts_input.setPlaceholderText("Average Time Step (ms)")
        export_layout.addWidget(self.ts_input)
        export_layout.addLayout(import_layout)
        self.histogram_check = QCheckBox("Histogram with 3 parameters")
        self.x_box = QComboBox()
        self.y_box = QComboBox()
        self.selectable_box = QComboBox()
        self.init_combo_boxes()
        xy_plot_layout = QHBoxLayout()
        x_layout = QVBoxLayout()
        x_label = QLabel("X:")
        self.from_x = QLineEdit(self)
        self.from_x.setPlaceholderText("From:")
        self.to_x = QLineEdit(self)
        self.to_x.setPlaceholderText("To:")
        self.step_x = QLineEdit(self)
        self.step_x.setPlaceholderText("Window step")
        x_layout.addWidget(self.x_box)
        x_layout.addWidget(self.from_x)
        x_layout.addWidget(self.to_x)
        x_layout.addWidget(self.step_x)
        y_layout = QVBoxLayout()
        y_label = QLabel("Y:")
        self.from_y = QLineEdit(self)
        self.from_y.setPlaceholderText("From:")
        self.to_y = QLineEdit(self)
        self.to_y.setPlaceholderText("To:")
        self.step_y = QLineEdit(self)
        self.step_y.setPlaceholderText("Window step")
        y_layout.addWidget(self.y_box)
        y_layout.addWidget(self.from_y)
        y_layout.addWidget(self.to_y)
        y_layout.addWidget(self.step_y)
        selectable_label = QLabel("Selectable:")
        xy_plot_layout.addWidget(self.histogram_check)
        xy_plot_layout.addWidget(x_label)
        xy_plot_layout.addLayout(x_layout)
        xy_plot_layout.addWidget(y_label)
        xy_plot_layout.addLayout(y_layout)
        xy_plot_layout.addWidget(selectable_label)
        xy_plot_layout.addWidget(self.selectable_box)
        export_layout.addLayout(xy_plot_layout)
        self.export_button = QPushButton("Save!")
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
        self.init_combo_boxes()

    def init_combo_boxes(self):
        parameters = config.get_parameters()
        self.x_box.clear()
        self.y_box.clear()
        for pgn in parameters.keys():
            for parameter in parameters[pgn].keys():
                self.x_box.addItem(parameter)
                self.y_box.addItem(parameter)
                self.selectable_box.addItem(parameter)

    def _get_table_rows(self, nrows, ncols):
        rows = []
        for i in range(1, nrows):
            row = []
            for j in range(0, ncols):
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
        if not self.filename:
            self.message.setWindowTitle("Information!")
            self.message.setText("There is no file to parse!")
            self.message.show()
            return
        self.parser = Parser(self.filename)
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
                                last_time = float(d[1])
                            avg_parameters.append((d[0], str(last_time), str(value_sum / count),
                                                   d[3]))
                            value_sum = 0
                            count = 0
                            last_time = float(d[1])
        return avg_parameters

    def _init_table(self):
        table = QTableWidget()
        table.setColumnCount(8)
        table.setRowCount(11)
        table.setItem(0, 0, QTableWidgetItem("Name"))
        table.setItem(0, 1, QTableWidgetItem("PGN"))
        table.setItem(0, 2, QTableWidgetItem("Multiplier"))
        table.setItem(0, 3, QTableWidgetItem("Offset"))
        table.setItem(0, 4, QTableWidgetItem("Units"))
        table.setItem(0, 5, QTableWidgetItem("Lenght"))
        table.setItem(0, 6, QTableWidgetItem("Start"))
        table.setItem(0, 7, QTableWidgetItem("Plot"))
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
                table.setItem(i, 7, QTableWidgetItem(parameters[pgn][name]['Draw']))
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

    def plot(self, parameters, excluded):
        self.canvas.axes.clear()
        if parameters:
            for parameter in parameters:
                self.canvas.plot(parameter, excluded)
        self.message.setWindowTitle("Information!")
        self.message.setText("Plot ready!")
        self.message.show()


class HistogramInterface(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.parameters = None
        self.canvas = HistogramCanvas()
        self.navigation_bar = NavigationToolbar(self.canvas, self)
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addWidget(self.navigation_bar)
        self.table = QTableWidget()
        layout.addLayout(canvas_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.message = QMessageBox()

    def plot_x_y(self, parameters, x_label, y_label, from_x, to_x, step_x, from_y, to_y, step_y,
                 selectable):
        self.canvas.axes.clear()
        if parameters:
            for parameter in parameters:
                if x_label == parameter[2]:
                    x = parameter[1]
                if y_label == parameter[2]:
                    y = parameter[1]
            self.canvas.plot(x, y, x_label, y_label, from_x, to_x, step_x, from_y, to_y, step_y)
            self.message.setWindowTitle("Information!")
            self.message.setText("Histogram ready!")
            self.message.show()

    def get_mean_sd(self, data, x_label, y_label, from_x, to_x, step_x,
                    from_y, to_y, step_y, selectable):
        ranges_x = self._get_ranges(from_x, to_x, step_x)
        ranges_y = self._get_ranges(from_y, to_y, step_y)
        self.table.setColumnCount(len(ranges_x) + 1)
        self.table.setRowCount(len(ranges_y) + 1)
        i = 1
        for range_x in ranges_x:
            j = 1
            self.table.setItem(0, i, QTableWidgetItem("{}-{} {}".format(range_x[0], range_x[1],
                                                                        config.get_unit(x_label))))
            for range_y in ranges_y:
                x_ts = []
                y_ts = []
                for d in data:
                    if d[0] == x_label and float(d[2]) in range_x:
                        x_ts.append(float(d[1]))
                    if d[0] == y_label and float(d[2]) in range_y:
                        y_ts.append(float(d[1]))
                ts = set.intersection(set(x_ts), set(y_ts))
                values = []
                for d in data:
                    if d[0] == selectable and float(d[1]) in ts:
                        values.append(float(d[2]))
                if len(values) > 0:
                    mean = "{}".format(statistics.mean(values))
                    sd = "{}".format(statistics.stdev(values))
                else:
                    mean = ''
                    sd = ''
                self.table.setItem(j, 0, QTableWidgetItem("{}-{} {}".format(range_y[0], range_y[1],
                                                          config.get_unit(y_label))))
                self.table.setItem(j, i, QTableWidgetItem("Mean: {}, SD: {}".format(mean, sd)))
                j = j+1
            i = i+1

    def _get_ranges(self, from_data, to_data, step):
        range_data = []
        i = from_data
        while i < to_data:
            range_data.append((i, i + step - 1))
            i = i + step
        return range_data
