from PyQt6.QtCore import QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSlider, QVBoxLayout, QHBoxLayout, QWidget,
)


class RangeSlider(QWidget):
    valuesChanged = pyqtSignal(int, int)

    def __init__(self, minimum=0, maximum=10_000_000, lower=0, upper=10_000_000):
        super().__init__()
        self.minimum_value = minimum
        self.maximum_value = maximum
        self.lower = lower
        self.upper = upper
        self.active = None
        self.setMinimumHeight(28)

    def _x_for_value(self, value):
        return 10 + (self.width() - 20) * (value - self.minimum_value) / (self.maximum_value - self.minimum_value)

    def _value_for_x(self, x):
        ratio = max(0.0, min(1.0, (x - 10) / max(1, self.width() - 20)))
        return round(self.minimum_value + ratio * (self.maximum_value - self.minimum_value))

    def paintEvent(self, event):
        painter = QPainter(self)
        y = self.height() / 2
        painter.setPen(QPen(Qt.GlobalColor.lightGray, 4))
        painter.drawLine(QPointF(10, y), QPointF(self.width() - 10, y))
        painter.setPen(QPen(Qt.GlobalColor.darkCyan, 5))
        painter.drawLine(QPointF(self._x_for_value(self.lower), y), QPointF(self._x_for_value(self.upper), y))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(QPointF(self._x_for_value(self.lower), y), 7, 7)
        painter.drawEllipse(QPointF(self._x_for_value(self.upper), y), 7, 7)

    def mousePressEvent(self, event):
        value = self._value_for_x(event.position().x())
        self.active = "lower" if abs(value - self.lower) <= abs(value - self.upper) else "upper"
        self._set_active(value)

    def mouseMoveEvent(self, event):
        if self.active:
            self._set_active(self._value_for_x(event.position().x()))

    def mouseReleaseEvent(self, event):
        self.active = None

    def _set_active(self, value):
        if self.active == "lower":
            self.lower = min(value, self.upper)
        else:
            self.upper = max(value, self.lower)
        self.valuesChanged.emit(self.lower, self.upper)
        self.update()

    def setValues(self, lower, upper):
        self.lower = max(self.minimum_value, min(lower, upper))
        self.upper = min(self.maximum_value, max(lower, upper))
        self.update()


class NodeChip(QWidget):
    removed = pyqtSignal(str)

    def __init__(self, node):
        super().__init__()
        self.node = node
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 1, 2, 1)
        layout.addWidget(QLabel(node))
        close = QPushButton("×")
        close.setFixedSize(20, 20)
        close.setToolTip(f"Remove {node}")
        close.clicked.connect(lambda: self.removed.emit(self.node))
        layout.addWidget(close)


class NodeFilter(QWidget):
    def __init__(self, logic, included):
        super().__init__()
        self.logic = logic
        self.included = included
        self.nodes = []
        self.chips_layout = QVBoxLayout()
        self.chips_layout.setContentsMargins(0, 0, 0, 0)
        group = QGroupBox("Included node types" if included else "Excluded node types")
        outer = QVBoxLayout(group)
        row = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.addItems(logic.all_nodes)
        add = QPushButton("Add")
        add.clicked.connect(self.add_node)
        row.addWidget(self.combo)
        row.addWidget(add)
        outer.addLayout(row)
        chips = QWidget()
        chips.setLayout(self.chips_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(100)
        scroll.setWidget(chips)
        outer.addWidget(scroll)
        self.group = group

    def add_node(self):
        node = self.combo.currentText().strip().lower()
        if node and node not in self.nodes and node in self.logic.all_nodes:
            self.nodes.append(node)
            chip = NodeChip(node)
            chip.removed.connect(self.remove_node)
            self.chips_layout.addWidget(chip)
            target = self.logic.included_nodes if self.included else self.logic.excluded_nodes
            target.append(node)
            self.window().refresh_table()

    def remove_node(self, node):
        if node not in self.nodes:
            return
        self.nodes.remove(node)
        target = self.logic.included_nodes if self.included else self.logic.excluded_nodes
        if node in target:
            target.remove(node)
        for i in range(self.chips_layout.count()):
            widget = self.chips_layout.itemAt(i).widget()
            if widget and widget.node == node:
                widget.deleteLater()
                break
        self.window().refresh_table()


class FilterPanel(QWidget):
    def __init__(self, window):
        super().__init__(window)
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
        self.max_params = QLineEdit(str(int(1e7)))
        self.range_slider = RangeSlider()
        self.range_slider.valuesChanged.connect(self.update_range_fields)
        form.addRow("Min:", self.min_params)
        form.addRow("Max:", self.max_params)
        form.addRow(self.range_slider)
        apply_params = QPushButton("Apply")
        apply_params.clicked.connect(self.update_params)
        form.addRow(apply_params)
        layout.addWidget(params)

        self.include_nodes = NodeFilter(self.logic, True)
        self.exclude_nodes = NodeFilter(self.logic, False)
        layout.addWidget(self.include_nodes.group)
        layout.addWidget(self.exclude_nodes.group)

        benchmarks = QGroupBox("Benchmarks")
        benchmark_layout = QVBoxLayout(benchmarks)
        benchmark_content = QWidget()
        content_layout = QVBoxLayout(benchmark_content)
        self.benchmark_checks = {}
        for name in sorted(self.logic.possible_origins):
            check = QCheckBox(name)
            check.setChecked(True)
            check.stateChanged.connect(self.update_benchmarks)
            self.benchmark_checks[name] = check
            content_layout.addWidget(check)
        content_layout.addStretch()
        benchmark_scroll = QScrollArea()
        benchmark_scroll.setWidgetResizable(True)
        benchmark_scroll.setMinimumHeight(150)
        benchmark_scroll.setWidget(benchmark_content)
        benchmark_layout.addWidget(benchmark_scroll)
        layout.addWidget(benchmarks, 1)

    def update_range_fields(self, lower, upper):
        self.min_params.setText(str(lower))
        self.max_params.setText(str(upper))

    def update_params(self):
        try:
            lower = max(0, int(self.min_params.text()))
            upper = max(lower, int(self.max_params.text()))
            self.range_slider.setValues(lower, upper)
            self.min_params.setText(str(lower))
            self.max_params.setText(str(upper))
            self.logic.min_params = lower
            self.logic.max_params = upper
            self.window().refresh_table()
        except ValueError:
            pass

    def update_architectures(self):
        self.logic.included_architectures = [name for name, check in self.arch_checks.items() if check.isChecked()]
        self.window().refresh_table()

    def update_benchmarks(self):
        self.logic.incuded_benchmarks = [name for name, check in self.benchmark_checks.items() if check.isChecked()]
        self.window().refresh_table()
