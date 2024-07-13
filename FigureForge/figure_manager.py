import os
import pickle
import json

from PySide6.QtWidgets import (
    QWidget,
    QMessageBox,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

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
        self.figure.__dict__.update(create_default_figure().__dict__)
        self.canvas.draw()
        self.fe.build_tree(self.figure)

        self.fe.itemSelected.connect(self.on_item_selected)
        self.pi.propertyChanged.connect(self.on_property_changed)

        self.selected_item = None

        self.load_json_structure()

    def load_json_structure(self):
        with open(os.path.join(CURRENT_DIR, "structure.json")) as file:
            self.structure = json.load(file)

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
        arrowprops=dict(facecolor="black", shrink=0.05),
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
