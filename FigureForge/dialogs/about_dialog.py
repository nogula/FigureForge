import os

from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, Qt

from FigureForge.__init__ import __version__, ASSETS_DIR


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About FigureForge")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "logo.ico")))

        layout = QGridLayout()

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join(ASSETS_DIR, "logo_color_text.png")))
        logo.setScaledContents(True)
        logo.setFixedSize(QSize(100, 100))

        layout.addWidget(logo, 0, 0)

        text_layout = QVBoxLayout()
        text_widget = QWidget()
        text_widget.setLayout(text_layout)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        label1 = QLabel(
            "FigureForge is a GUI tool for creating and editing matplotlib figures."
        )
        label2 = QLabel(
            'Visit the <a href="https://github.com/nogula/FigureForge">project homepage</a> for more information.'
        )
        label3 = QLabel(f"Version {__version__}")
        label4 = QLabel("Copyright 2024 Noah Gula")
        text_layout.addWidget(label1)
        text_layout.addWidget(label2)

        text_layout.addSpacing(10)

        text_layout.addWidget(label3)
        text_layout.addWidget(label4)
        layout.addWidget(text_widget, 0, 1, Qt.AlignTop)

        self.setLayout(layout)

        self.exec()
