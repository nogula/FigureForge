from copy import deepcopy
import select
import numpy as np

from PySide6.QtWidgets import (
    QGraphicsSceneMouseEvent,
    QWidget,
    QScrollArea,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QColorDialog,
    QPushButton,
    QMenu,
    QMessageBox,
    QFrame,
    QDialog,
    QGraphicsRectItem,
    QGraphicsItem,
    QGraphicsView,
    QGraphicsScene,
    QHBoxLayout,
    QRubberBand,
    QSizePolicy,
    QSpacerItem,

)
from PySide6.QtGui import QFocusEvent, QFont, QColor, QDrag, QPen, QBrush, QPainter
from PySide6.QtCore import Qt, Signal, QMimeData, QRectF, QSizeF, Slot, QRect, QPoint, QObject

import pickle
import json

import matplotlib as mpl

mpl.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.colors as mcolors
import matplotlib.text as mtext
from matplotlib.gridspec import GridSpec


class FigureManager(QWidget):
    def __init__(self):
        super().__init__()

        self.pi = PropertyInspector()
        self.fe = FigureExplorer()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.unsaved_changes = False
        self.file_name = None

        self.new_figure()
        self.figure.subplots()
        self.figure.axes[0].plot([1, 2, 3, 4], [1, 4, 9, 16])
        self.convert_to_gridspec(self.figure)
        self.canvas.draw()
        self.fe.build_tree(self.figure)

        self.fe.itemSelected.connect(self.on_item_selected)
        self.pi.propertyChanged.connect(self.on_property_changed)

        self.selected_item = None

        with open("FigureForge/structure.json", "r") as file:
            self.structure = json.load(file)

    def load_figure(self, file_name):
        self.new_figure()
        with open(file_name, "rb") as file:
            data = pickle.load(file)
        self.figure.__dict__.update(data.__dict__)
        self.convert_to_gridspec(self.figure)
        self.canvas.draw()

        self.unsaved_changes = False

        self.fe.build_tree(self.figure)

    def save_figure(self, file_name):
        with open(file_name, "wb") as file:
            pickle.dump(self.figure, file)
        self.unsaved_changes = False

    def new_figure(self):
        self.figure.clear()
        self.convert_to_gridspec(self.figure)
        self.canvas.draw()

        self.fe.build_tree(self.figure)

    def on_item_selected(self, item):
        self.selected_item = item
        self.pi.clear_properties()
        properties = self.structure[item.__class__.__name__]["attributes"]
        for property in properties:
            name = property
            value_type = properties[name]["type"]
            value_options = (
                properties[name]["value_options"]
                if "value_options" in properties[name]
                else None
            )
            if "get_index" in properties[name]:
                value = getattr(self.selected_item, properties[name]["get"])()
                try:
                    value = value[
                        properties[name]["get_index"]
                    ]
                except TypeError:
                    value = value
            else:
                value = getattr(self.selected_item, properties[name]["get"])()
            print(property, value)
            self.pi.add_property(name, value_type, value, value_options)

    def on_property_changed(self, property_name, value):
        item = self.selected_item
        item_class = item.__class__.__name__
        set_method = self.structure[item_class]["attributes"][
            property_name
        ]["set"]
        if "set_parameter" in self.structure[item_class]["attributes"][property_name]:
            parameter = self.structure[item_class]["attributes"][property_name][
                "set_parameter"
            ]
            value = {parameter: value}
            getattr(item, set_method)(**value)
        else:
            getattr(item, set_method)(value)
        self.canvas.draw()
        self.unsaved_changes = True
        # self.fe.build_tree(self.figure)
        self.unsaved_changes = True

    def delete_item(self):
        if self.selected_item is None:
            return

        self.attempt_delete(self.selected_item)
        self.canvas.draw()
        self.unsaved_changes = True

        self.fe.build_tree(self.figure)
        self.selected_item = None

    def attempt_delete(self,item):
        try:
            item.remove()
        except NotImplementedError:
            QMessageBox.critical(self, "Error", "Cannot delete this item.")

    def convert_to_gridspec(self, figure):
        
        pass
        # axs = figure.get_axes()
        # if isinstance(axs, np.ndarray):
        #     rows, cols = axs.shape
        # else:
        #     rows, cols = 1, 1

        # self.gs = GridSpec(rows, cols, figure)
        # if isinstance(axs,np.ndarray):
        #     for i in range(rows):
        #         for j in range(cols):
        #             axs[i,j].set_position(self.gs[i,j].get_position(figure))
        #             axs[i,j].set_subplotspec(self.gs[i,j])
        # else:
        #     axs.set_position(self.gs[0,0].get_position(figure))
        #     axs.set_subplotspec(self.gs[0,0])

    def configure_gridspec(self):
        raise NotImplementedError


class PropertyInspector(QWidget):
    propertyChanged = Signal(str, object)

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)

        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_widget.setLayout(self.content_layout)

        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

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

    def add_property(self, name, value_type, value, value_options=None):
        row = self.content_layout.rowCount()
        self.content_layout.addWidget(QLabel(name), row, 0)
        self.content_layout.addWidget(QLabel(value_type), row, 1)

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
            value_widget = QDoubleSpinBox()
            value_widget.setMinimum(-999999999)
            value_widget.setMaximum(999999999)
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

    def on_value_changed(self, name, widget):
        if widget.__class__.__name__ == "QCheckBox":
            value = widget.isChecked()
        elif widget.__class__.__name__ == "QComboBox":
            value = widget.currentText()
        elif widget.__class__.__name__ == "QLineEdit":
            value = widget.text()
        elif widget.__class__.__name__ == "QDoubleSpinBox":
            value = widget.value()
        elif widget.__class__.__name__ == "ColorButton":
            value = widget.color.getRgbF()
        elif widget.__class__.__name__ == "QSpinBox":
            value = widget.value()
        else:
            value = None

        index = self.content_layout.indexOf(widget)
        label_widget = self.content_layout.itemAt(index - 2).widget()
        property_name = label_widget.text()
        self.propertyChanged.emit(property_name, value)


class FigureExplorer(QTreeWidget):
    itemSelected = Signal(object)

    def __init__(self):
        super().__init__()
        self.itemClicked.connect(self.on_item_clicked)

        self.init_ui()

    def init_ui(self):
        # self.setHeaderItem(QTreeWidgetItem(["Figure Explorer"]))
        self.header().hide()
        pass

    def build_tree(self, figure):
        self.clear()
        self.addTopLevelItem(QTreeWidgetItem(["Figure"]))
        root = self.topLevelItem(0)
        root.reference = figure
        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item)

    def add_item(self, parent, child):
        class_name = child.__class__.__name__
        if child.get_label() != "":
            label = f"{class_name} - {child.get_label()}"
        else:
            label = class_name
        parent.addChild(QTreeWidgetItem([label]))
        root = parent.child(parent.childCount() - 1)
        root.reference = child

        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item)

    def on_item_clicked(self, item):
        self.itemSelected.emit(item.reference)


class ColorButton(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, initial_color=None, parent=None):
        super().__init__(parent)
        self.setText("Choose Color")
        self.color = initial_color if initial_color else QColor(255, 255, 255)
        self.setObjectName("color_button")
        self.update_button_color()

        self.clicked.connect(self.open_color_dialog)

    def open_color_dialog(self):
        color = QColorDialog.getColor(self.color, self, "Select Color")

        if color.isValid():
            self.color = color
            self.update_button_color()
            self.colorChanged.emit(self.color)  # Emit the signal

    def update_button_color(self):
        self.setStyleSheet(
            f"#color_button {{ background-color: {self.color.name()}; }}"
        )