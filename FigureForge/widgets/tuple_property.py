from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QSpinBox,
    QLineEdit,
    QCheckBox,
)
from PySide6.QtCore import Signal

from FigureForge.widgets.custom_spinbox import SpinBox


class TupleProperty(QWidget):
    valueChanged = Signal(object)

    def __init__(self, types, values):
        super().__init__()

        self.columns = len(types)
        self.types = types
        self.values = values

        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.widgets = []
        for i in range(self.columns):
            if self.types[i] == "float":
                widget = SpinBox()
                widget.setRange(-1e6, 1e6)
                widget.valueChanged.connect(self.valueChanged.emit)
            elif self.types[i] == "int":
                widget = QSpinBox()
                widget.setRange(-1e6, 1e6)
                widget.valueChanged.connect(self.valueChanged.emit)
            elif self.types[i] == "string":
                widget = QLineEdit()
                widget.textChanged.connect(self.valueChanged.emit)
            elif self.types[i] == "bool":
                widget = QCheckBox()
                widget.stateChanged.connect(self.valueChanged.emit)
            else:
                raise ValueError(f"Invalid type: {self.types[i]}")

            self.layout.addWidget(widget)
            self.widgets.append(widget)

        self.set_values(self.values)

    def set_values(self, values):
        for i in range(self.columns):
            if self.types[i] == "bool":
                self.widgets[i].setChecked(values[i])
            elif self.types[i] == "string":
                self.widgets[i].setText(values[i])
            elif self.types[i] == "int":
                self.widgets[i].setValue(values[i])
            elif self.types[i] == "float":
                self.widgets[i].setValue(values[i])

    def get_values(self):
        values = []
        for i in range(self.columns):
            if self.types[i] == "bool":
                values.append(self.widgets[i].isChecked())
            elif self.types[i] == "string":
                values.append(self.widgets[i].text())
            elif self.types[i] == "int":
                values.append(self.widgets[i].value())
            elif self.types[i] == "float":
                values.append(self.widgets[i].value())
        return values
