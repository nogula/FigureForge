import os

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.spines import Spine

from PySide6.QtWidgets import QMessageBox, QDialog

from .utils.add_annotations_dialog import AddAnnotationsDialog


class AddAnnotation:
    name = "Add Annotation"
    tooltip = "Add an annotation to an axes."
    icon = os.path.join(os.path.dirname(__file__), "add_annotation.png")
    submenu = "Annotations"

    def run(self, obj):
        if not isinstance(obj, Axes):
            msg_failure = QMessageBox()
            msg_failure.setText(f"Invalid obj type: {type(obj)}.")
            msg_failure.setIcon(QMessageBox.Warning)
            msg_failure.exec()
            return

        dialog = AddAnnotationsDialog()
        if dialog.exec() == QDialog.Accepted:
            annotation = dialog.get_annotation()
            print(annotation)
            obj.annotate(**annotation)
