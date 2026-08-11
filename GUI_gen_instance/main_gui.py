from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout

from .filter_gui import FilterPanel
from .front_gui import BenchmarkPanel
from .support_gui import SupportPanel


class GUI(QMainWindow):
    def __init__(self, logic_instance):
        super().__init__()
        self.logic_instance = logic_instance
        self.setWindowTitle("Instances Generator")
        self.resize(1000, 650)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(SupportPanel(self))
        splitter = QSplitter()
        splitter.addWidget(FilterPanel(self))
        splitter.addWidget(BenchmarkPanel(self))
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        self.setCentralWidget(root)

    def refresh_table(self):
        self.findChild(BenchmarkPanel).refresh()
