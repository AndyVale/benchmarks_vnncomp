from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtWidgets import QTabWidget, QTableView, QVBoxLayout, QWidget


class MetadataModel(QAbstractTableModel):
    def __init__(self, columns, rows):
        super().__init__()
        self.columns = columns
        self.rows = rows

    def rowCount(self, parent=None):
        return len(self.rows)

    def columnCount(self, parent=None):
        return len(self.columns)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        return self.columns[section] if orientation == Qt.Orientation.Horizontal else section + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and index.isValid():
            return str(self.rows[index.row()][index.column()])
        return None


class BenchmarkPanel(QWidget):
    PAGE_SIZE = 50

    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.columns = ['onnx', 'architecture', 'benchmark', 'n_params', 'node_types']
        self.tabs = QTabWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        self.refresh()

    def refresh(self):
        rows = self.window.logic_instance.get_benchmarks_sample()
        self.tabs.clear()
        for start in range(0, len(rows), self.PAGE_SIZE):
            table = QTableView()
            table.setModel(MetadataModel(self.columns, rows[start:start + self.PAGE_SIZE]))
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(False)
            table.horizontalHeader().setStretchLastSection(True)
            self.tabs.addTab(table, f"Tab {start // self.PAGE_SIZE}")
