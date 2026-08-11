from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHeaderView, QTabWidget, QTableView, QVBoxLayout, QWidget


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


class SeparatorHeader(QHeaderView):
    """Show a resize cursor only while the pointer is on a section divider."""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)
        self.setSectionsMovable(True)
        self.setSectionsClickable(True)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    def mouseMoveEvent(self, event):
        position = event.position().toPoint()
        section = self.logicalIndexAt(position)
        near_separator = False
        if section >= 0:
            coordinate = position.x() if self.orientation() == Qt.Orientation.Horizontal else position.y()
            # Keep a forgiving hit zone around the divider so resizing does
            # not require pixel-perfect pointer placement.
            start = self.sectionViewportPosition(section)
            end = start + self.sectionSize(section)
            near_separator = min(abs(coordinate - start), abs(coordinate - end)) <= 7
        if near_separator:
            cursor = (Qt.CursorShape.SizeHorCursor if self.orientation() == Qt.Orientation.Horizontal
                      else Qt.CursorShape.SizeVerCursor)
        else:
            cursor = Qt.CursorShape.ArrowCursor
        self.setCursor(cursor)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)


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
            header = SeparatorHeader(Qt.Orientation.Horizontal, table)
            table.setHorizontalHeader(header)
            vertical_header = SeparatorHeader(Qt.Orientation.Vertical, table)
            table.setVerticalHeader(vertical_header)
            table.setFont(QFont("Sans Serif", 12))
            header.setFont(QFont("Sans Serif", 13, QFont.Weight.Bold))
            vertical_header.setFont(QFont("Sans Serif", 13, QFont.Weight.Bold))
            table.setStyleSheet(
                "QTableView { gridline-color: #777777; }"
                "QHeaderView::section { border: 1px solid #777777; padding: 5px; }"
            )
            header.setStretchLastSection(False)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            vertical_header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
            vertical_header.setDefaultSectionSize(28)
            for column, width in enumerate((220, 140, 180, 120, 320)):
                header.resizeSection(column, width)
            self.tabs.addTab(table, f"Tab {start // self.PAGE_SIZE}")
