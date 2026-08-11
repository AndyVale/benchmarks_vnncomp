from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QGroupBox, QLabel, QLineEdit,
    QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
)


class FilterPanel(QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.logic = window.logic_instance
        layout = QVBoxLayout(self)

        architectures = QGroupBox("Architectures")
        arch_layout = QVBoxLayout(architectures)
        self.arch_checks = {}
        for name in ("fullyconnected", "convolutional", "residual"):
            check = QCheckBox(name.capitalize())
            check.setChecked(True)
            check.stateChanged.connect(self.update_architectures)
            self.arch_checks[name] = check
            arch_layout.addWidget(check)
        layout.addWidget(architectures)

        params = QGroupBox("Number of parameters")
        form = QFormLayout(params)
        self.min_params = QLineEdit("0")
        self.max_params = QLineEdit(str(int(1e10)))
        form.addRow("Min:", self.min_params)
        form.addRow("Max:", self.max_params)
        apply_params = QPushButton("Apply")
        apply_params.clicked.connect(self.update_params)
        form.addRow(apply_params)
        layout.addWidget(params)

        self.include_nodes = self._node_group("Included node types", True)
        self.exclude_nodes = self._node_group("Excluded node types", False)
        layout.addWidget(self.include_nodes[0])
        layout.addWidget(self.exclude_nodes[0])

        benchmarks = QGroupBox("Benchmarks")
        benchmark_layout = QVBoxLayout(benchmarks)
        self.benchmark_checks = {}
        for name in sorted(self.logic.possible_origins):
            check = QCheckBox(name)
            check.setChecked(True)
            check.stateChanged.connect(self.update_benchmarks)
            self.benchmark_checks[name] = check
            benchmark_layout.addWidget(check)
        layout.addWidget(benchmarks)
        layout.addStretch()

    def _node_group(self, title, included):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(self.logic.all_nodes)
        button = QPushButton("Add")
        selected = QListWidget()
        row = QHBoxLayout()
        row.addWidget(combo)
        row.addWidget(button)
        layout.addLayout(row)
        layout.addWidget(selected)
        button.clicked.connect(lambda: self._add_node(combo, selected, included))
        return group, selected, included

    def _add_node(self, combo, selected, included):
        node = combo.currentText().strip().lower()
        if node and not selected.findItems(node, Qt.MatchFlag.MatchExactly):
            selected.addItem(node)
            target = self.logic.included_nodes if included else self.logic.excluded_nodes
            target.append(node)
            self.window.refresh_table()

    def update_architectures(self):
        self.logic.included_architectures = [name for name, check in self.arch_checks.items() if check.isChecked()]
        self.window.refresh_table()

    def update_benchmarks(self):
        self.logic.incuded_benchmarks = [name for name, check in self.benchmark_checks.items() if check.isChecked()]
        self.window.refresh_table()

    def update_params(self):
        try:
            self.logic.min_params = int(self.min_params.text())
            self.logic.max_params = int(self.max_params.text())
            self.window.refresh_table()
        except ValueError:
            pass
