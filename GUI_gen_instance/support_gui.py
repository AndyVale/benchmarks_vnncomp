import webbrowser

from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QPushButton, QWidget


class SupportPanel(QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        layout = QHBoxLayout(self)
        calculate = QPushButton("Calculate")
        calculate.clicked.connect(self.calculate)
        options = QPushButton("Options")
        options.clicked.connect(self.options)
        help_button = QPushButton("Help")
        help_button.clicked.connect(lambda: webbrowser.open(self.window.logic_instance.help_url))
        layout.addWidget(calculate)
        layout.addWidget(options)
        layout.addWidget(help_button)
        layout.addStretch()

    def calculate(self):
        logic = self.window.logic_instance
        logic.prova()

    def options(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select metadata dataset", self.window.logic_instance.path_to_dataset)
        if path:
            self.window.logic_instance.path_to_dataset = path
