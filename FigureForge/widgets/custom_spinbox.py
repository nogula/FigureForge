from PySide6.QtWidgets import (
    QDoubleSpinBox,
)


class SpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDecimals(16)
        self.setMinimum(-1e16)
        self.setMaximum(1e16)

    def textFromValue(self, value):
        return str(value)

    def valueFromText(self, text):
        return float(text)
