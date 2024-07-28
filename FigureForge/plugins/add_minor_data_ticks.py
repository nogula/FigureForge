import os

from PySide6.QtWidgets import QMessageBox

from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.patches import Polygon
from matplotlib.ticker import FixedLocator

import numpy as np


class AddMinorDataTicks:
    name = "Add Minor Data Ticks"
    tooltip = "Add minor ticks for each data point."
    icon = os.path.join(os.path.dirname(__file__), "add_minor_data_ticks.png")
    submenu = "Ticks"

    def run(self, obj):
        if isinstance(obj, Axis):
            data = self.get_data(obj.axes)
            if obj.axis_name == "x":
                obj.set_minor_locator(FixedLocator(np.unique(data[0])))
            elif obj.axis_name == "y":
                obj.set_minor_locator(FixedLocator(np.unique(data[1])))
        elif isinstance(obj, Axes):
            data = self.get_data(obj)
            obj.xaxis.set_minor_locator(FixedLocator(np.unique(data[0])))
            obj.yaxis.set_minor_locator(FixedLocator(np.unique(data[1])))
                
        else:
            msg_failure = QMessageBox()
            msg_failure.setText(f"Invalid object type: {obj.__class__.__name__}. Must be Axes or Axis.")
            msg_failure.setIcon(QMessageBox.Warning)
            msg_failure.exec()
            return

    def get_data(self, ax):
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

        return all_x, all_y
