import os

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.spines import Spine

from PySide6.QtWidgets import QMessageBox, QDialog

from .utils.add_legend_dialog import AddLegendDialog


class AddLegend:
    name = "Add Legend"
    tooltip = "Add a legend to an axes."
    icon = os.path.join(os.path.dirname(__file__), "add_legend.png")
    submenu = "Legends"

    def run(self, obj):
        if not isinstance(obj, Axes):
            msg_failure = QMessageBox()
            msg_failure.setText(f"Invalid obj type: {type(obj)}.")
            msg_failure.setIcon(QMessageBox.Warning)
            msg_failure.exec()
            return

        dialog = AddLegendDialog()
        if dialog.exec() == QDialog.Accepted:
            legend = dialog.get_legend()
            print(legend)
            obj.legend(**legend)
