from PySide6.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QCheckBox,
    QDialogButtonBox,
    QDialog,
    QPlainTextEdit
)


class AddLegendDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Select Spines to Remove")
        self.layout = QVBoxLayout(self)
        text = QPlainTextEdit()
        text.setPlaceholderText("Enter the legend labels one per line.")
        self.layout.addWidget(text)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_legend(self):
        return {
            "labels": self.layout.itemAt(0).widget().toPlainText().split("\n")
        }