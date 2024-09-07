import os
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QApplication,
)

from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtCore import QUrl

from FigureForge.__init__ import __version__, ASSETS_DIR


class NewPluginDialog(QDialog):
    def __init__(self, filename, plugin_dir):
        super().__init__()

        self.setWindowTitle("New Plugin Created")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "logo.ico")))
        layout = QVBoxLayout()
        message = QLabel(f"New plugin created at:\n{filename}")
        layout.addWidget(message)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        copy_button = QPushButton("Copy Path")
        open_button = QPushButton("Open Folder")
        for button in [copy_button, open_button, ok_button]:
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            button.setFixedWidth(100)
            button.clicked.connect(self.close)
            button_layout.addWidget(button)
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(filename))
        open_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(plugin_dir))
        )
        ok_button.setDefault(True)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.exec()
