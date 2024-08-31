import os

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.spines import Spine

from PySide6.QtWidgets import QMessageBox, QDialog

from .utils.select_spines_dialog import SelectSpinesDialog


class ToggleSpines:
    name = "Toggles spines"
    tooltip = "Toggles spines from the selected object."
    icon = os.path.join(os.path.dirname(__file__), "toggle_spines.png")
    submenu = "Spines"

    def run(self, obj):
        if isinstance(obj, Spine):
            obj.set_visible(not obj.get_visible())

        elif isinstance(obj, (Figure, Axes)):
            dialog = SelectSpinesDialog()
            if dialog.exec() == QDialog.Accepted:
                selected_spines = dialog.get_selected_spines()
                if isinstance(obj, Figure):
                    for ax in obj.axes:
                        for spine, display in selected_spines.items():
                            if display:
                                ax.spines[spine].set_visible(False)
                            else:
                                ax.spines[spine].set_visible(True)
                elif isinstance(obj, Axes):
                    for spine, display in selected_spines.items():
                        if display:
                            obj.spines[spine].set_visible(False)
                        else:
                            obj.spines[spine].set_visible(True)
        else:
            msg_failure = QMessageBox()
            msg_failure.setText(
                f"Invalid obj type: {type(obj)}. Must be Figure, Axes, or Spine."
            )
            msg_failure.setIcon(QMessageBox.Warning)
            msg_failure.exec()
