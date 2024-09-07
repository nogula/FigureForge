import os
import requests

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QCheckBox,
    QHBoxLayout,
    QPushButton,
)

from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtCore import QUrl

from FigureForge.__init__ import __version__, ASSETS_DIR


class UpdateFoundDialog(QDialog):
    def __init__(self, latest_version: str):
        super().__init__()
        self.setWindowTitle("Update Available")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "logo.ico")))
        layout = QVBoxLayout()
        message = QLabel(
            f"An update is available. Your version: v{__version__}, Latest version: {latest_version}"
        )
        layout.addWidget(message)
        self.check = QCheckBox("Check for updates at startup")
        self.check.setChecked(True)
        layout.addWidget(self.check)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        update_button = QPushButton("Update")
        update_button.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/nogula/FigureForge/releases/latest")
            )
        )
        update_button.clicked.connect(self.close)
        button_layout.addWidget(update_button)
        update_button.setDefault(True)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.exec()


def check_for_updates():
    url = "https://api.github.com/repos/nogula/FigureForge/releases/latest"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        latest_version = data["tag_name"]
        if latest_version != "v" + __version__:
            dialog = UpdateFoundDialog(latest_version)
            return dialog.check.isChecked()
        return None
    except Exception as e:
        print(f"Failed to check for updates: {e}")
