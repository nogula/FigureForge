import os

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.spines import Spine

from PySide6.QtWidgets import QMessageBox, QDialog

from .utils.select_spines_dialog import SelectSpinesDialog


class ExamplePlugin:
    name = "Remove Spines"
    tooltip = "Remove spines from the selected obj."
    icon = os.path.join(os.path.dirname(__file__), "remove_spines.png")
    submenu = "Spines"

    def run(self, obj):
        msg_success = QMessageBox()
        msg_success.setText("Spines removed successfully.")
        msg_success.setIcon(QMessageBox.Information)
        if isinstance(obj, Spine):
            obj.set_visible(False)
            msg_success.exec()

        elif isinstance(obj, (Figure, Axes)):
            dialog = SelectSpinesDialog()
            if dialog.exec() == QDialog.Accepted:
                selected_spines = dialog.get_selected_spines()
                if isinstance(obj, Figure):
                    for ax in obj.axes:
                        for spine, remove in selected_spines.items():
                            if remove:
                                ax.spines[spine].set_visible(False)
                elif isinstance(obj, Axes):
                    for spine, remove in selected_spines.items():
                        if remove:
                            obj.spines[spine].set_visible(False)
                msg_success.exec()
        else:
            msg_failure = QMessageBox()
            msg_failure.setText(f"Invalid obj type: {type(obj)}.")
            msg_failure.setIcon(QMessageBox.Warning)
            msg_failure.exec()
