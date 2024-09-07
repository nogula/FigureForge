from PySide6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QDialog,
    QLineEdit,
    QComboBox,
    QLabel,
    QFormLayout,
    QHBoxLayout,
)
from PySide6.QtGui import QColor

from .color_button import ColorButton
from .custom_spinbox import SpinBox


class AddAnnotationsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Annotations")
        layout = QFormLayout(self)

        self.text = QLineEdit()
        layout.addRow(QLabel("Text:"), self.text)
        self.text_color = ColorButton(initial_color=QColor(0, 0, 0))
        layout.addRow(QLabel("Text Color:"), self.text_color)

        xy_layout = QHBoxLayout()
        self.x = SpinBox()
        self.x.setMinimum(-1e6)
        self.x.setMaximum(1e6)
        self.y = SpinBox()
        self.y.setMinimum(-1e6)
        self.y.setMaximum(1e6)
        self.xycoords = QComboBox()
        self.xycoords.addItems(
            ["data", "axes", "figure", "offset points", "offset pixels"]
        )
        xy_layout.addWidget(self.x)
        xy_layout.addWidget(self.y)
        xy_layout.addWidget(self.xycoords)
        layout.addRow(QLabel("Position (x, y):"), xy_layout)

        xytext_layout = QHBoxLayout()
        self.xtext = SpinBox()
        self.xtext.setMinimum(-1e6)
        self.xtext.setMaximum(1e6)
        self.ytext = SpinBox()
        self.ytext.setMinimum(-1e6)
        self.ytext.setMaximum(1e6)
        self.xytextcoords = QComboBox()
        self.xytextcoords.addItems(
            ["data", "axes", "figure", "offset points", "offset pixels"]
        )
        xytext_layout.addWidget(self.xtext)
        xytext_layout.addWidget(self.ytext)
        xytext_layout.addWidget(self.xytextcoords)
        layout.addRow(QLabel("Text Position (x, y):"), xytext_layout)

        self.use_arrow = QCheckBox("Use Arrow")
        self.use_arrow.setChecked(True)
        self.use_arrow.stateChanged.connect(self.arrow_changed)
        layout.addRow(self.use_arrow)

        arrowprops_layout = QFormLayout()
        self.arrowstyle = QComboBox()
        self.arrowstyle.addItems(
            [
                "->",
                "<-",
                "<->",
                "<|-",
                "-|>",
                "<|-|>",
                "-[",
                "]-",
                "]-[",
                "|-|",
                "]->",
                "<-[",
            ]
        )
        self.connectionstyle = QComboBox()
        self.connectionstyle.addItems(
            [
                "arc",
                "arc3",
                "arc",
                "angle",
                "angle3",
                "angle",
                "bar",
                "bar",
                "bar",
                "angle",
                "angle3",
                "angle",
            ]
        )
        shrink_layout = QHBoxLayout()
        self.shrinkA = SpinBox()
        self.shrinkA.setMinimum(-1e6)
        self.shrinkA.setMaximum(1e6)
        self.shrinkB = SpinBox()
        self.shrinkB.setMinimum(-1e6)
        self.shrinkB.setMaximum(1e6)
        shrink_layout.addWidget(self.shrinkA)
        shrink_layout.addWidget(self.shrinkB)
        self.linewidth = SpinBox()
        self.linewidth.setMinimum(0)
        self.linewidth.setMaximum(1e6)
        self.linewidth.setValue(0.5)
        self.color = ColorButton(initial_color=QColor(0, 0, 0))

        arrowattrs_layout = QFormLayout()
        self.arrowattrs = {
            "head_length": 0.4,
            "head_width": 0.2,
            "widthA": 1.0,
            "widthB": 1.0,
            "lengthA": 0.2,
            "lengthB": 0.2,
            "angleA": 0.0,
            "angleB": 0.0,
        }
        self.arrowattrs_widgets = {}
        for attr, value in self.arrowattrs.items():
            spinbox = SpinBox()
            spinbox.setMinimum(-1e6)
            spinbox.setMaximum(1e6)
            spinbox.setValue(value)
            self.arrowattrs_widgets[attr] = spinbox
            arrowattrs_layout.addRow(QLabel(attr), spinbox)
        connectionattrs_layout = QFormLayout()
        self.connectionattrs = {
            "rad": 0.0,
            "angleA": 0.0,
            "angleB": 0.0,
            "armA": 0.0,
            "armB": 0.0,
            "fraction": 0.3,
        }
        self.connectionattrs_widgets = {}
        for attr, value in self.connectionattrs.items():
            spinbox = SpinBox()
            spinbox.setMinimum(-1e6)
            spinbox.setMaximum(1e6)
            spinbox.setValue(value)
            self.connectionattrs_widgets[attr] = spinbox
            connectionattrs_layout.addRow(QLabel(attr), spinbox)

        arrowprops_layout.addRow(QLabel("Arrow Style:"), self.arrowstyle)
        arrowprops_layout.addRow(QLabel("Connection Style:"), self.connectionstyle)
        arrowprops_layout.addRow(QLabel("Shrink (A, B):"), shrink_layout)
        arrowprops_layout.addRow(QLabel("Linewidth:"), self.linewidth)
        arrowprops_layout.addRow(QLabel("Color:"), self.color)
        arrowprops_layout.addRow(QLabel("Arrow Attributes:"), arrowattrs_layout)
        arrowprops_layout.addRow(
            QLabel("Connection Attributes:"), connectionattrs_layout
        )

        layout.addRow(QLabel("Arrow Properties:"), arrowprops_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_annotation(self):
        arrow_params = {
            "->": [
                "head_length",
                "head_width",
                "widthA",
                "widthB",
                "angleA",
                "angleB",
                "lengthA",
                "lengthB",
            ],
            "<-": [
                "head_length",
                "head_width",
                "widthA",
                "widthB",
                "angleA",
                "angleB",
                "lengthA",
                "lengthB",
            ],
            "<->": [
                "head_length",
                "head_width",
                "widthA",
                "widthB",
                "angleA",
                "angleB",
                "lengthA",
                "lengthB",
            ],
            "<|-": [
                "head_length",
                "head_width",
                "widthA",
                "widthB",
                "angleA",
                "angleB",
                "lengthA",
                "lengthB",
            ],
            "-|>": [
                "head_length",
                "head_width",
                "widthA",
                "widthB",
                "angleA",
                "angleB",
                "lengthA",
                "lengthB",
            ],
            "<|-|>": [
                "head_length",
                "head_width",
                "widthA",
                "widthB",
                "angleA",
                "angleB",
                "lengthA",
                "lengthB",
            ],
            "]-": ["widthA", "lengthA", "angleA"],
            "-[": ["widthB", "lengthB", "angleB"],
            "]-[": ["widthA", "lengthA", "angleA", "widthB", "lengthB", "angleB"],
            "|-|": ["widthA", "angleA", "widthB", "angleB"],
            "]->": ["widthA", "angleA", "lengthA"],
            "<-[": ["widthB", "angleB", "lengthB"],
        }
        connection_params = {
            "arc": ["angleA", "angleB", "armA", "armB", "rad"],
            "arc3": ["rad"],
            "bar": ["armA", "armB", "fraction", "angle"],
            "angle": ["angleA", "angleB", "rad"],
            "angle3": ["angleA", "angleB"],
            "none": [],
        }
        if self.use_arrow.isChecked():
            arrowstyle_string = ""
            print(f"Arrowstyle: '{self.arrowstyle.currentText()}'")
            print(type(arrow_params))
            temp = str(arrow_params[self.arrowstyle.currentText()])
            print(temp)
            for param in arrow_params[self.arrowstyle.currentText()]:
                param_value = self.arrowattrs_widgets[param].value()
                arrowstyle_string += f"{param}={param_value},"
            arrowstyle_string = arrowstyle_string[:-1]
            arrowstyle_string = self.arrowstyle.currentText() + ", " + arrowstyle_string
            connectionstyle_string = ""
            for param in connection_params[self.connectionstyle.currentText()]:
                param_value = self.connectionattrs_widgets[param].value()
                connectionstyle_string += f"{param}={param_value},"
            connectionstyle_string = connectionstyle_string[:-1]
            connectionstyle_string = (
                self.connectionstyle.currentText() + ", " + connectionstyle_string
            )
            arrowprops = {
                "arrowstyle": arrowstyle_string,
                "connectionstyle": connectionstyle_string,
                "shrinkA": self.shrinkA.value(),
                "shrinkB": self.shrinkB.value(),
                "linewidth": self.linewidth.value(),
                "color": self.color.color.getRgbF(),
            }
            return {
                "text": self.text.text(),
                "xy": (self.x.value(), self.y.value()),
                "xycoords": self.xycoords.currentText(),
                "xytext": (self.xtext.value(), self.ytext.value()),
                "textcoords": self.xytextcoords.currentText(),
                "arrowprops": arrowprops,
            }
        else:
            return {
                "text": self.text.text(),
                "xy": (self.x.value(), self.y.value()),
                # "xycoords": self.xycoords.currentText(),
                # "xytext": (self.xtext.value(), self.ytext.value()),
                "textcoords": self.xytextcoords.currentText(),
            }

    def arrow_changed(self):
        if self.use_arrow.isChecked():
            self.arrowstyle.setEnabled(True)
            self.connectionstyle.setEnabled(True)
            self.shrinkA.setEnabled(True)
            self.shrinkB.setEnabled(True)
            self.linewidth.setEnabled(True)
            self.color.setEnabled(True)
            self.xtext.setEnabled(True)
            self.ytext.setEnabled(True)
            self.xytextcoords.setEnabled(True)
            for widget in self.arrowattrs_widgets.values():
                widget.setEnabled(True)
            for widget in self.connectionattrs_widgets.values():
                widget.setEnabled(True)
        else:
            self.arrowstyle.setEnabled(False)
            self.connectionstyle.setEnabled(False)
            self.shrinkA.setEnabled(False)
            self.shrinkB.setEnabled(False)
            self.linewidth.setEnabled(False)
            self.color.setEnabled(False)
            self.xtext.setEnabled(False)
            self.ytext.setEnabled(False)
            self.xytextcoords.setEnabled(False)
            for widget in self.arrowattrs_widgets.values():
                widget.setEnabled(False)
            for widget in self.connectionattrs_widgets.values():
                widget.setEnabled(False)
