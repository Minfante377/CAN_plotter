from PyQt5.QtWidgets import QWidget, QPushButton, QMainWindow, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFileDialog
import os

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
        layout.addLayout(control_panel.layout)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


class ControlPanel(QWidget):

    def __init__(self):
        import_layout = QVBoxLayout()
        self.import_label = QLabel("Select a file to import")
        self.import_button = QPushButton("Browse...")
        self.import_button.clicked.connect(self.browse)
        self.filename = None
        import_layout.addWidget(self.import_label)
        import_layout.addWidget(self.import_button)
        export_layout = QVBoxLayout()
        self.export_button = QPushButton("Export!")
        self.plot_button = QPushButton("Plot!")
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.plot_button)
        self.layout = QVBoxLayout()
        self.layout.addLayout(import_layout)
        self.layout.addLayout(export_layout)

    def browse(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select tcr file", os.getcwd(),
                                                  "tcr files(*.tcr)")
        if filename:
            self.filename = filename
            self._parse_tcr_file(self.filename)

    def _parse_tcr_file(self, filename):
        self.import_label.setText(filename)
        pass
