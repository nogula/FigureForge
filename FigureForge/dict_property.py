from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QLineEdit,
    QCheckBox,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal

from .tuple_property import TupleProperty
from .color_button import ColorButton


class DictProperty(QWidget):
    valueChanged = Signal(object)

    def __init__(self, types, values):
        super().__init__()

        self.num_values = len(types)
        self.types = types
        self.values = values

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.widgets = []
        for k in self.types:
            label = QLabel(k)
            if self.types[k] == "float":
                widget = QDoubleSpinBox()
                widget.setRange(-1e6, 1e6)
                widget.valueChanged.connect(self.valueChanged.emit)
            elif self.types[k] == "int":
                widget = QSpinBox()
                widget.setRange(-1e6, 1e6)
                widget.valueChanged.connect(self.valueChanged.emit)
            elif self.types[k] == "string":
                widget = QLineEdit()
                widget.textChanged.connect(self.valueChanged.emit)
            elif self.types[k] == "bool":
                widget = QCheckBox()
                widget.stateChanged.connect(self.valueChanged.emit)
            elif self.types[k] == "color":
                widget = ColorButton()
                widget.colorChanged.connect(self.valueChanged.emit)
            else:
                raise ValueError(f"Invalid type: {self.types[k]}")
            self.layout.addWidget(label)
            self.layout.addWidget(widget)
            self.widgets.append(widget)
        self.set_values(self.values)

    def set_values(self, values):
        for i, k in enumerate(self.types):
            if self.types[k] == "bool":
                try:
                    self.widgets[i].setChecked(values[k])
                except KeyError:
                    self.widgets[i].setChecked(False)
            elif self.types[k] == "string":
                try:
                    self.widgets[i].setText(values[k])
                except KeyError:
                    self.widgets[i].setText("")
            elif self.types[k] == "int":
                try:
                    self.widgets[i].setValue(values[k])
                except KeyError:
                    self.widgets[i].setValue(0)
            elif self.types[k] == "float":
                try:
                    self.widgets[i].setValue(values[k])
                except KeyError:
                    self.widgets[i].setValue(0.0)
            elif self.types[k] == "color":
                try:
                    self.widgets[i].color = values[k]
                    self.widgets[i].update_button_color()
                except KeyError:
                    self.widgets[i].color = QColor(255, 255, 255)
                    self.widgets[i].update_button_color()

    def get_values(self):
        values = {}
        for i, k in enumerate(self.types):
            if self.types[k] == "bool":
                values[k] = self.widgets[i].isChecked()
            elif self.types[k] == "string":
                values[k] = self.widgets[i].text()
            elif self.types[k] == "int":
                values[k] = self.widgets[i].value()
            elif self.types[k] == "float":
                values[k] = self.widgets[i].value()
            elif self.types[k] == "color":
                values[k] = self.widgets[i].color
        return values
