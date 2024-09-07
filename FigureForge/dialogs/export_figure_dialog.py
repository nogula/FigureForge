import os

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QSpinBox,
    QScrollArea,
    QWidget,
    QSizePolicy,
    QFormLayout,
    QCheckBox,
)
from PySide6.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from FigureForge.__init__ import ASSETS_DIR
from FigureForge.widgets.custom_spinbox import SpinBox


class ExportFigureDialog(QDialog):
    def __init__(self, preferences, figure):
        super().__init__()
        self.setWindowTitle("Export Figure")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "logo.ico")))
        self.setMinimumSize(800, 600)
        self.preferences = preferences
        self.figure = figure
        self.last_export_path = preferences.get("last_export_path")
        self.init_ui()

        self.exec()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left panel for export options
        options_layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setText(self.last_export_path)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)
        form_layout.addRow(QLabel("Path:"), path_layout)

        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setRange(10, 1000)
        self.dpi_spinbox.setValue(self.figure.get_dpi())
        self.dpi_spinbox.valueChanged.connect(self.dpi_changed)
        form_layout.addRow(QLabel("DPI:"), self.dpi_spinbox)

        self.width_edit = SpinBox()
        self.width_edit.setValue(self.figure.get_size_inches()[0])
        self.width_edit.valueChanged.connect(self.size_changed)
        self.height_edit = SpinBox()
        self.height_edit.setValue(self.figure.get_size_inches()[1])
        self.height_edit.valueChanged.connect(self.size_changed)
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.width_edit)
        size_layout.addWidget(self.height_edit)
        form_layout.addRow(QLabel("Size (inches):"), size_layout)

        options_layout.addLayout(form_layout)

        self.open_file_checkbox = QCheckBox("Open file after export")
        options_layout.addWidget(self.open_file_checkbox)

        # Export and Cancel buttons
        button_layout = QHBoxLayout()
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.export_figure)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(export_button)
        button_layout.addWidget(cancel_button)

        options_layout.addLayout(button_layout)

        left_panel = QWidget()
        left_panel.setLayout(options_layout)
        left_panel.setFixedWidth(300)

        main_layout.addWidget(left_panel)

        # Right panel for figure preview
        self.canvas = FigureCanvas(self.figure)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)

    def browse(self):
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        filetypes = self.canvas.get_supported_filetypes()
        filenamefilter = []
        for filetype in filetypes:
            filenamefilter.append(f"{filetypes[filetype]} Files (*.{filetype})")
        file_dialog.setNameFilters(filenamefilter)
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            self.path_edit.setText(selected_file)

    def export_figure(self):
        path = self.path_edit.text()
        dpi = self.dpi_spinbox.value()
        width = self.width_edit.text()
        height = self.height_edit.text()

        try:
            if width and height:
                size = (float(width), float(height))
                self.figure.set_size_inches(size)
            self.figure.savefig(path, dpi=dpi)
            if self.open_file_checkbox.isChecked():
                os.startfile(path)
            self.preferences.set("last_export_path", path)
            self.accept()
        except Exception as e:
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Error")
            error_layout = QVBoxLayout()
            error_layout.addWidget(QLabel(f"Failed to export figure: {str(e)}"))
            error_button = QPushButton("OK")
            error_button.clicked.connect(error_dialog.accept)
            error_layout.addWidget(error_button)
            error_dialog.setLayout(error_layout)
            error_dialog.exec()

    def dpi_changed(self, value):
        self.figure.set_dpi(value)
        self.canvas.draw()

    def size_changed(self, value):
        width = self.width_edit.value()
        height = self.height_edit.value()
        size = (width, height)
        self.figure.set_size_inches(size)
        self.canvas.draw()

        self.scroll_area.widget().resize(self.canvas.sizeHint())
