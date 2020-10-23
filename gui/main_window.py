from PyQt5.QtWidgets import QWidget, QPushButton, QMainWindow, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFileDialog
from helpers.parser import Parser
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
        control_panel = ControlPanel()
        layout.addWidget(control_panel)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


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
        parser = Parser(filename)
        self.parsed_file = parser.parse_file()
        self.import_label.setText(filename.rsplit(SEPARATOR, 1)[1])
