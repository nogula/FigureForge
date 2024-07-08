import os
import pickle
import json

from PySide6.QtWidgets import (
    QWidget,
    QMessageBox,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .__init__ import CURRENT_DIR
from .property_inspector import PropertyInspector
from .figure_explorer import FigureExplorer


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

        with open(os.path.join(CURRENT_DIR, "structure.json")) as file:
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
                    value = value[properties[name]["get_index"]]
                except TypeError:
                    value = value
            else:
                value = getattr(self.selected_item, properties[name]["get"])()
            self.pi.add_property(name, value_type, value, value_options)

    def on_property_changed(self, property_name, value):
        item = self.selected_item
        item_class = item.__class__.__name__
        set_method = self.structure[item_class]["attributes"][property_name]["set"]
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

    def attempt_delete(self, item):
        try:
            item.remove()
        except NotImplementedError:
            QMessageBox.critical(self, "Error", "Cannot delete this item.")

    def convert_to_gridspec(self, figure):
        pass
