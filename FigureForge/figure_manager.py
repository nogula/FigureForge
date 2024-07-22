import os
import pickle
import json

from PySide6.QtWidgets import (
    QWidget,
    QMessageBox,
)

from PySide6 import QtCore

# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from FigureForge.__init__ import CURRENT_DIR
from FigureForge.property_inspector import PropertyInspector
from FigureForge.figure_explorer import FigureExplorer


class FigureManager(QWidget):
    def __init__(self):
        super().__init__()
        self.debug = False

        self.pi = PropertyInspector()
        self.fe = FigureExplorer()

        # Setup the figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.unsaved_changes = False
        self.file_name = None

        # Only when GUI is started, create the default figure
        self.new_figure()
        self.figure.__dict__.update(create_default_figure().__dict__)
        self.canvas.draw()
        self.fe.build_tree(self.figure)

        # Connect signals to slots
        self.fe.itemSelected.connect(self.on_item_selected)
        self.pi.propertyChanged.connect(self.on_property_changed)
        self.selected_obj = None

        # Load the JSON figure property structure as a dict
        self.load_json_structure()

    def load_json_structure(self):
        json_file = os.path.join(CURRENT_DIR, "structure.json")
        with open(json_file) as file:
            self.structure = json.load(file)
        if self.debug:
            print(f"Loaded structure: {json_file}")

    def load_figure(self, file_name):
        self.new_figure()
        with open(file_name, "rb") as file:
            data = pickle.load(file)
        self.figure.__dict__.update(data.__dict__)
        self.canvas.draw()
        self.unsaved_changes = False
        self.fe.build_tree(self.figure)
        if self.debug:
            print(f"Loaded figure from {file_name}")

    def save_figure(self, file_name):
        with open(file_name, "wb") as file:
            pickle.dump(self.figure, file)
        self.unsaved_changes = False
        if self.debug:
            print(f"Saved figure to {file_name}")

    def new_figure(self):
        self.figure.clear()
        self.file_name = None
        self.unsaved_changes = False
        self.canvas.draw()
        self.fe.build_tree(self.figure)
        if self.debug:
            print("Created new figure")

    def on_item_selected(self, obj):
        self.selected_obj = obj
        self.pi.clear_properties()
        properties = self.structure[obj.__class__.__name__]["attributes"]

        for property_name in properties:
            prop = properties[property_name]
            value_type = prop["type"]
            value_options = prop["value_options"] if "value_options" in prop else None
            types = prop["types"] if "types" in prop else None
            get_index = prop["get_index"] if "get_index" in prop else None
            value = self.get_value(obj, prop["get"], get_index)

            if value_type == "tuple" or value_type == "dict":
                types = prop["types"]

            self.pi.add_property(property_name, value_type, value, value_options, types)

        if self.debug:
            print(f"Selected {obj.__class__.__name__}")

    def on_property_changed(self, property_name, value):
        obj = self.selected_obj
        obj_class = obj.__class__.__name__
        prop = self.structure[obj_class]["attributes"][property_name]
        set_method = prop["set"]

        if "set_parameter" in prop:
            parameter = prop["set_parameter"]
            value = {parameter: value}
        self.set_value(obj, set_method, value)

        self.canvas.draw()
        self.unsaved_changes = True

        if self.debug:
            print(f"Changed {property_name} to {value} on {obj_class}")

    def delete_obj(self):
        if self.selected_obj is None:
            return

        self.attempt_delete(self.selected_obj)
        self.canvas.draw()
        self.unsaved_changes = True

        self.fe.build_tree(self.figure)
        self.selected_obj = None

        if self.debug:
            print(f"Attempting to delete {self.selected_obj}")

    def attempt_delete(self, obj):
        try:
            obj.remove()
        except NotImplementedError:
            QMessageBox.critical(self, "Error", "Cannot delete this item.")

    def toggle_debug_mode(self):
        self.debug = not self.debug
        print(f"Debug mode: {self.debug}")

    def get_value(self, obj, attr_path, index=None):
        attrs = attr_path.split(".")
        for attr in attrs:
            obj = getattr(obj, attr)
            if callable(obj):
                obj = obj()
        if callable(obj):
            value = obj()
        else:
            value = obj
        if index is not None:
            try:
                value = value[index]
            except TypeError:
                if self.debug:
                    print(f"Indexing failed on {value} for {obj}")
                value = value
        return value

    def set_value(self, obj, attr_path, value):
        attrs = attr_path.split(".")
        for attr in attrs[:-1]:
            obj = getattr(obj, attr)
            if callable(obj):
                obj = obj()
        if type(value) == dict:
            if self.debug:
                print(f"Calling {attr_path}({value}) on {obj}")
            getattr(obj, attrs[-1])(**value)
        elif callable(getattr(obj, attrs[-1])):
            if self.debug:
                print(f"Calling {attr_path}({value}) on {obj}")
            getattr(obj, attrs[-1])(value)
        else:
            if self.debug:
                print(f"Setting {attr_path} to {value} on {obj}")
            setattr(obj, attrs[-1], value)


def create_default_figure():

    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    np.random.seed(0)
    x_scatter = np.random.rand(100)
    y_scatter = np.random.rand(100)
    colors = np.random.rand(100)
    sizes = 1000 * np.random.rand(100)

    categories = ["A", "B", "C", "D"]
    values = np.random.rand(len(categories))

    data = np.random.randn(100, 4)

    # Create the figure
    fig = Figure()
    axs = fig.subplots(2, 2)
    fig.suptitle("FigureForge Demo Figure", fontsize=16, label="suptitle")

    # Line plot
    axs[0, 0].plot(x, y, marker="o", linestyle="-", color="b", label="sin(x)")
    axs[0, 0].set_label("Line Plot")
    axs[0, 0].set_title("Line Plot")
    axs[0, 0].legend()
    axs[0, 0].set_xscale("symlog")
    axs[0, 0].set_xlabel("x")
    axs[0, 0].set_ylabel("sin(x)")

    for spine in axs[0, 0].spines:
        if spine == "top" or spine == "right":
            axs[0, 0].spines[spine].set_visible(False)
        if spine == "bottom":
            axs[0, 0].spines[spine].set_bounds(min(x), max(x))
        if spine == "left":
            axs[0, 0].spines[spine].set_bounds(min(y), max(y))

    # Scatter plot
    scatter = axs[0, 1].scatter(
        x_scatter, y_scatter, c=colors, s=sizes, alpha=0.3, cmap="viridis"
    )
    axs[0, 1].set_label("Scatter Plot")
    axs[0, 1].set_title("Scatter Plot")
    axs[0, 1].annotate(
        "Example Annotation",
        xy=(0.5, 0.5),
        xytext=(0.7, 0.7),
        arrowprops=dict(
            arrowstyle="->", connectionstyle="arc3,rad=0.5", facecolor="black", lw=0.5
        ),
    )
    fig.colorbar(scatter, ax=axs[0, 1])

    # Bar chart
    axs[1, 0].bar(
        categories, values, color=["lightgray", "darkgray", "lightgray", "lightgray"]
    )
    axs[1, 0].set_label("Bar Chart")
    axs[1, 0].set_title("Bar Chart")
    axs[1, 0].grid(True, axis="y", color="white")

    for spine in axs[1, 0].spines:
        axs[1, 0].spines[spine].set_visible(False)

    # Box plot
    axs[1, 1].boxplot(data)
    axs[1, 1].set_label("Box Plot")
    axs[1, 1].set_title("Box Plot")

    return fig
