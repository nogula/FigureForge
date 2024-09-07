import os
import sys

from PySide6.QtWidgets import (
    QWidget,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices
from PySide6.QtCore import QSize, Qt

from FigureForge.__init__ import ASSETS_DIR, __version__
from PySide6.__init__ import __version__ as pyside_version
# Build errors with nuikta when trying to get mpl version as
# "from matplotlib.__init__ import __version__ as mpl_version" so this is the workaround
import matplotlib
mpl_version = matplotlib.__version__


class BugReportDialog(QDialog):
    def __init__(self, parent=None):
        super(BugReportDialog, self).__init__(parent)

        self.setWindowTitle("FigureForge Bug Report")
        self.setWindowIcon(
            QIcon(os.path.join(ASSETS_DIR, "logo.ico"))
        )

        layout = QGridLayout()

        logo = QLabel()
        logo.setPixmap(
            QPixmap(os.path.join(ASSETS_DIR, "logo_color_text.png"))
        )
        logo.setScaledContents(True)
        logo.setFixedSize(QSize(100, 100))

        layout.addWidget(logo, 0, 0)

        text_layout = QVBoxLayout()
        text_widget = QWidget()
        text_widget.setLayout(text_layout)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        label1 = QLabel("Press Yes to report a bug on the GitHub page.")
        label2 = QLabel("Please include the following information in your report: ")
        label3 = QLabel(
            f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
        label4 = QLabel(f"Matplotlib version {mpl_version}")
        label5 = QLabel(f"PySide6 version {pyside_version}")
        label6 = QLabel(f"FigureForge version {__version__}")

        text_layout.addWidget(label1)
        text_layout.addWidget(label2)

        text_layout.addSpacing(10)

        text_layout.addWidget(label3)
        text_layout.addWidget(label4)
        text_layout.addWidget(label5)
        text_layout.addWidget(label6)
        layout.addWidget(text_widget, 0, 1, Qt.AlignTop)

        btn_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.open_issues_page)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box, 1, 0, 1, 2, Qt.AlignCenter)

        self.setLayout(layout)

        self.exec()

    def open_issues_page(self):
        url = "https://github.com/nogula/FigureForge/issues/new/choose"
        QDesktopServices.openUrl(url)
        self.accept()
