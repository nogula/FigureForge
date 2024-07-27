import os

from PySide6.QtWidgets import QMessageBox

from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.patches import Polygon

import numpy as np


class ReduceTickLimits:
    name = "Reduce Tick Limits"
    tooltip = "Set the tick limits to max and min of data."
    icon = os.path.join(os.path.dirname(__file__), "reduce_tick_limits.png")
    submenu = "Ticks"

    def run(self, obj):
        if isinstance(obj, Axis):
            self.update_ticks(obj, *obj.get_data_interval())
        elif isinstance(obj, Axes):
            for axis in [obj.xaxis, obj.yaxis]:
                self.update_ticks(axis, *axis.get_data_interval())
        else:
            msg_failure = QMessageBox()
            msg_failure.setText(f"Invalid object type: {obj.__class__.__name__}. Must be Axes or Axis.")
            msg_failure.setIcon(QMessageBox.Warning)
            msg_failure.exec()
            return

    def update_ticks(self, axis, min_val, max_val):
        ticks = axis.get_ticklocs()
        tick_spacing = abs(ticks[1] - ticks[0])
        ticks[0] = min_val
        ticks[-1] = max_val
        if abs(ticks[1] - ticks[0]) < tick_spacing/3:
            ticks = np.delete(ticks, 1)
        if abs(ticks[-1] - ticks[-2]) < tick_spacing/3:
            ticks = np.delete(ticks, -2)
        axis.set_ticks(ticks)
