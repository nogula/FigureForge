import os

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.spines import Spine

from PySide6.QtWidgets import QMessageBox, QDialog

from .utils.select_spines_dialog import SelectSpinesDialog


class ExamplePlugin:
    name = "Remove Spines"
    tooltip = "Remove spines from the selected item."
    icon = os.path.join(os.path.dirname(__file__),"remove_spines.png")

    def run(self, item):
        msg_success = QMessageBox()
        msg_success.setText("Spines removed successfully.")
        msg_success.setIcon(QMessageBox.Information)
        if isinstance(item, Spine):
            item.set_visible(False)
            msg_success.exec()

        elif isinstance(item, (Figure, Axes)):
            dialog = SelectSpinesDialog()
            if dialog.exec() == QDialog.Accepted:
                selected_spines = dialog.get_selected_spines()
                if isinstance(item, Figure):
                    for ax in item.axes:
                        for spine, remove in selected_spines.items():
                            if remove:
                                ax.spines[spine].set_visible(False)
                elif isinstance(item, Axes):
                    for spine, remove in selected_spines.items():
                        if remove:
                            item.spines[spine].set_visible(False)
                msg_success.exec()
        else:
            msg_failure = QMessageBox()
            msg_failure.setText(f"Invalid item type: {type(item)}.")
            msg_failure.setIcon(QMessageBox.Warning)
            msg_failure.exec()
