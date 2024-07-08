import os

from PySide6.QtWidgets import QMessageBox

from matplotlib.axes import Axes
from matplotlib.patches import Polygon


class SetSpineBounds:
    name = "Set Spine Bounds"
    tooltip = "Set the bounds of the selected spine(s) to max and min of data."
    icon = os.path.join(os.path.dirname(__file__), "set_spine_bounds.png")

    def run(self, ax):
        print(ax)
        if not isinstance(ax, Axes):
            msg_failure = QMessageBox()
            msg_failure.setText(f"Invalid item type: {type(ax)}.")
            msg_failure.setIcon(QMessageBox.Warning)
            msg_failure.exec()
            return
        all_x = []
        all_y = []
        for line in ax.get_lines():
            x_data, y_data = line.get_xdata(), line.get_ydata()
            all_x.extend(x_data)
            all_y.extend(y_data)

        for path_collection in ax.collections:
            offsets = path_collection.get_offsets()
            if offsets is not None:
                x_data, y_data = offsets[:, 0], offsets[:, 1]
                all_x.extend(x_data)
                all_y.extend(y_data)

        for patch in ax.patches:
            if isinstance(patch, Polygon):
                path = patch.get_path()
                x_data, y_data = path.vertices[:, 0], path.vertices[:, 1]
                all_x.extend(x_data)
                all_y.extend(y_data)
            else:
                x_data, y_data = patch.get_x(), patch.get_y()
                all_x.append(x_data)
                all_y.append(y_data)

        if len(all_x) > 0 and len(all_y) > 0:
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            (min_x, max_x), (min_y, max_y)
        else:
            return

        for spine in ax.spines:
            if spine == "left":
                ax.spines[spine].set_bounds(min_y, max_y)
            elif spine == "bottom":
                ax.spines[spine].set_bounds(min_x, max_x)

        print(min_x, max_x, min_y, max_y)
