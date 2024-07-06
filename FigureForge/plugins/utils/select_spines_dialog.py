from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QCheckBox, QDialogButtonBox, QDialog

class SelectSpinesDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Select Spines to Remove")
        self.layout = QVBoxLayout(self)
        self.spines = [
            "top",
            "bottom",
            "left",
            "right",
        ]
        self.checkboxes = []
        for spine in self.spines:
            checkbox = QCheckBox(spine)
            self.checkboxes.append(checkbox)
            self.layout.addWidget(checkbox)
        self.checkboxes[0].setChecked(True)
        self.checkboxes[3].setChecked(True)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_selected_spines(self):
        return {
            spine: checkbox.isChecked()
            for spine, checkbox in zip(self.spines, self.checkboxes)
        }