from PySide6.QtWidgets import (
    QPushButton,
    QColorDialog,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor


class ColorButton(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, initial_color=None, parent=None):
        super().__init__(parent)
        self.setText("Choose Color")
        self.color = initial_color if initial_color else QColor(255, 255, 255)
        self.setObjectName("color_button")
        self.update_button_color()

        self.clicked.connect(self.open_color_dialog)

    def open_color_dialog(self):
        color = QColorDialog.getColor(self.color, self, "Select Color")

        if color.isValid():
            self.color = color
            self.update_button_color()
            self.colorChanged.emit(self.color)  # Emit the signal

    def update_button_color(self):
        self.setStyleSheet(
            f"#color_button {{ background-color: {self.color.name()}; }}"
        )
