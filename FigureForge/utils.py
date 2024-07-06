import ast

from PySide6.QtWidgets import (
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
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal

import pickle

import matplotlib as mpl

mpl.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
        self.figure.axes[0].scatter([1, 2, 3, 4], [1, 4, 9, 16])
        self.canvas.draw()
        self.fe.build_tree(self.figure)

        self.fe.itemSelected.connect(self.on_item_selected)
        self.pi.propertyChanged.connect(self.on_property_changed)

        self.selected_item = None

    def load_figure(self, file_name):
        self.new_figure()
        with open(file_name, "rb") as file:
            data = pickle.load(file)
        self.figure.__dict__.update(data.__dict__)
        self.canvas.draw()

        self.unsaved_changes = False

        self.fe.build_tree(self.figure)

    def save_figure(self, file_name):
        with open(file_name, "wb") as file:
            pickle.dump(self.figure, file)
        self.unsaved_changes = False

    def new_figure(self):
        self.figure.clear()
        self.canvas.draw()

        self.fe.build_tree(self.figure)

    def on_item_selected(self, item):
        self.selected_item = item
        properties = self.get_item_properties(item)
        self.pi.update_properties(properties)

    def on_property_changed(self, property, value):
        self.apply_property_change(property, value)

    def get_item_properties(self, item):
        inspector = mpl.artist.ArtistInspector(item)
        properties = inspector.properties()
        return properties

    def apply_property_change(self, property, value):
        # setattr(self.fe.selected_item, name, value)
        # self.canvas.draw()
        print(f"Setting {property} to {value}")
        item = self.selected_item
        inspector = mpl.artist.ArtistInspector(item)
        value = ast.literal_eval(value)
        mpl.artist.setp(item, **{property: value})
        self.canvas.draw()
        self.unsaved_changes = True

class PropertyInspector(QWidget):
    propertyChanged = Signal(str, object)

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)

        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_widget.setLayout(self.content_layout)

        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

        property_label = QLabel("Property")
        property_label.setFont(QFont("Arial", -1, QFont.Bold))
        type_label = QLabel("Type")
        type_label.setFont(QFont("Arial", -1, QFont.Bold))
        value_label = QLabel("Value")
        value_label.setFont(QFont("Arial", -1, QFont.Bold))

        self.content_layout.addWidget(property_label, 0, 0)
        self.content_layout.addWidget(type_label, 0, 1)
        self.content_layout.addWidget(value_label, 0, 2)

    def update_properties(self, properties):
        while self.content_layout.count() > 3:
            item = self.content_layout.takeAt(3)
            if item.widget():
                item.widget().deleteLater()

        for name, value in properties.items():
            self.add_property(name, value)

    def add_property(self, name, value):
        row = self.content_layout.rowCount()
        self.content_layout.addWidget(QLabel(name), row, 0)
        self.content_layout.addWidget(QLabel(str(type(value).__name__)), row, 1)

        value_widget = QLineEdit(str(value))
        value_widget.editingFinished.connect(
            lambda n=name, w=value_widget: self.on_value_changed(n, w)
        )
        self.content_layout.addWidget(value_widget, row, 2)

    def on_value_changed(self, name, widget):
        value = widget.text()
        self.propertyChanged.emit(name, value)


class FigureExplorer(QTreeWidget):
    itemSelected = Signal(object)

    def __init__(self):
        super().__init__()

        self.itemClicked.connect(self.on_item_clicked)

        self.init_ui()

    def init_ui(self):
        self.setHeaderItem(QTreeWidgetItem(["Figure Explorer"]))

    def build_tree(self, figure):
        self.clear()
        self.addTopLevelItem(QTreeWidgetItem(["Figure"]))
        root = self.topLevelItem(0)
        root.reference = figure
        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item)

    def add_item(self, parent, child):
        parent.addChild(QTreeWidgetItem([child.__class__.__name__]))
        root = parent.child(parent.childCount() - 1)
        root.reference = child
        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item)

    def on_item_clicked(self, item):
        self.itemSelected.emit(item.reference)
        print(f"Selected {item.reference}")
