from PySide6.QtWidgets import (
    QMessageBox,
)


class SaveWorkDialog(QMessageBox):
    def __init__(self, filename):
        super().__init__()
        self.setWindowTitle("Save Work")
        filename = (
            filename.split("/")[-1] if filename is not None else "Untitled Figure"
        )
        self.setText(f"Do you want to save your work?\n{filename}")
        self.setStandardButtons(
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        self.setDefaultButton(QMessageBox.Save)
        self.setIcon(QMessageBox.Question)
        self.exec()
