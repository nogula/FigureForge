import copy
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QLabel,
    QCheckBox,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPlainTextEdit,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

from FigureForge.widgets.ff_widgets import (
    ColorButton,
    SpinBox,
    TupleProperty,
    DictProperty,
)
import matplotlib.colors as mcolors
import matplotlib.font_manager as mpl_fm


class PropertyInspector(QWidget):
    propertyChanged = Signal(str, object)

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("Property Inspector"))
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        # self.scroll_area.setStyleSheet("background-color: #ffffff")
        self.scroll_area.setWidget(self.content_widget)

        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_widget.setLayout(self.content_layout)

        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        property_label = QLabel("Property")
        font = property_label.font()
        font.setBold(True)
        property_label.setFont(font)
        type_label = QLabel("Type")
        type_label.setFont(font)
        value_label = QLabel("Value")
        value_label.setFont(font)

        self.content_layout.addWidget(property_label, 0, 0)
        self.content_layout.addWidget(type_label, 0, 1)
        self.content_layout.addWidget(value_label, 0, 2)

    def clear_properties(self):
        while self.content_layout.count() > 3:
            item = self.content_layout.takeAt(3)
            if item.widget():
                item.widget().deleteLater()

    def add_property(self, name, value_type, value, value_options=None, types=None):
        row = self.content_layout.rowCount()
        self.content_layout.addWidget(QLabel(name), row, 0, Qt.AlignTop)
        self.content_layout.addWidget(QLabel(value_type), row, 1, Qt.AlignTop)

        if value_type == "bool":
            value_widget = QCheckBox()
            try:
                value_widget.setChecked(value)
            except TypeError:
                value_widget.setChecked(False)
            value_widget.stateChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "string":
            value_widget = QLineEdit()
            value_widget.setText(value)
            value_widget.textChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "multiline":
            value_widget = QPlainTextEdit()
            value_widget.setPlainText(value)
            value_widget.textChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "choice":
            value_widget = QComboBox()
            value_widget.addItems(value_options)
            if isinstance(value, list):
                value = value[0]
            value_widget.setCurrentText(str(value))
            value_widget.currentTextChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "color":
            c = mcolors.to_hex(value)
            value_widget = ColorButton(initial_color=QColor(c))
            value_widget.colorChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "float":
            value_widget = SpinBox()
            try:
                value_widget.setValue(value)
            except TypeError:
                value_widget.setValue(0.0)
            value_widget.valueChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "int":
            value_widget = QSpinBox()
            value_widget.setMinimum(-999999999)
            value_widget.setMaximum(999999999)
            try:
                value_widget.setValue(value)
            except TypeError:
                value_widget.setValue(0)
            value_widget.valueChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "tuple":
            value_widget = TupleProperty(types=types, values=value)
            value_widget.valueChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "dict":
            value_widget = DictProperty(types=types, values=value)
            value_widget.valueChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)
        elif value_type == "font":
            value_widget = QComboBox()
            font_names = sorted(set(f.name for f in mpl_fm.fontManager.ttflist))
            for font_name in font_names:
                value_widget.addItem(font_name)
                font = QFont(font_name)
                value_widget.setItemData(value_widget.count() - 1, font, Qt.FontRole)
            value_widget.setCurrentText(value)
            value_widget.currentTextChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self.content_layout.addWidget(value_widget, row, 2)

    def on_value_changed(self, name, widget):
        if widget.__class__.__name__ == "QCheckBox":
            value = widget.isChecked()
        elif widget.__class__.__name__ == "QComboBox":
            value = widget.currentText()
        elif widget.__class__.__name__ == "QLineEdit":
            value = widget.text()
        elif widget.__class__.__name__ == "QPlainTextEdit":
            value = widget.toPlainText()
        elif widget.__class__.__name__ == "SpinBox":
            value = widget.value()
        elif widget.__class__.__name__ == "ColorButton":
            value = widget.color.getRgbF()
        elif widget.__class__.__name__ == "QSpinBox":
            value = widget.value()
        elif widget.__class__.__name__ == "TupleProperty":
            value = widget.get_values()
        elif widget.__class__.__name__ == "DictProperty":
            value = widget.get_values()
        else:
            value = None

        index = self.content_layout.indexOf(widget)
        label_widget = self.content_layout.itemAt(index - 2).widget()
        property_name = label_widget.text()
        self.propertyChanged.emit(property_name, value)
