from PySide6.QtWidgets import (
    QWidget,
    QSplitter,
    QFileDialog,
    QVBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QDialog,
    QGridLayout,
)
from PySide6.QtCore import Qt, QUrl, QObject, QSize
from PySide6.QtGui import QFont, QDesktopServices, QIcon, QAction, QCursor, QPixmap

import matplotlib.pyplot as plt
import pandas as pd

from .utils import FigureExplorer, FigureManager, PropertyInspector
from .__init__ import __version__
import os
import importlib
import inspect

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FigureForge")
        self.setWindowIcon(QIcon(os.path.join(CURRENT_DIR, "resources/icons/logo.png")))
        self.setMinimumSize(800, 600)

        self.create_menus()
        self.init_ui()

        self.show()

    def create_menus(self):
        """Creates the menubar at the top of the main window."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/new_icon.png"))
        )
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/open_icon.png"))
        )
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/save_icon.png"))
        )
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/save_as_icon.png"))
        )
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_figure)
        export_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/export_icon.png"))
        )
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        quit_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/quit_icon.png"))
        )
        quit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(quit_action)

        edit_menu = menubar.addMenu("Edit")
        configure_gridspec_action = QAction("Configure Gridspec", self)
        configure_gridspec_action.triggered.connect(self.configure_gridspec)
        configure_gridspec_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/gridspec_icon.png"))
        )
        configure_gridspec_action.setShortcut("Ctrl+G")
        edit_menu.addAction(configure_gridspec_action)

        edit_menu.addSeparator()

        delete_item_action = QAction("Delete Item", self)
        delete_item_action.triggered.connect(self.delete_item)
        delete_item_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/delete_icon.png"))
        )
        delete_item_action.setShortcut("Del")
        edit_menu.addAction(delete_item_action)

        self.plugin_menu = menubar.addMenu("Plugins")
        self.load_plugins()
        self.plugin_menu.addSeparator()
        open_plugins_folder_action = QAction("Open Plugins Folder...", self)
        open_plugins_folder_action.triggered.connect(self.open_plugins_folder)
        self.plugin_menu.addAction(open_plugins_folder_action)
        plugins_documentation_action = QAction("Plugins Documentation", self)
        plugins_documentation_action.triggered.connect(self.plugins_documentation)
        self.plugin_menu.addAction(plugins_documentation_action)

        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about_pressed)
        about_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/about_icon.png"))
        )
        help_menu.addAction(about_action)

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.help_pressed)
        help_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/documentation_icon.png"))
        )
        help_menu.addAction(help_action)

        bug_action = QAction("Report Bug", self)
        bug_action.triggered.connect(self.bug_pressed)
        bug_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/bug_icon.png"))
        )
        help_menu.addAction(bug_action)

    def init_ui(self):
        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setStyleSheet(
            """
                QSplitter::handle {
                    background: lightgray;
                }
                QSplitter::handle:vertical {
                    width: 2px;
                }
            """
        )

        self.fm = FigureManager()
        self.fe = self.fm.fe
        self.pi = self.fm.pi

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.setContentsMargins(0, 0, 5, 0)
        left_splitter.setStyleSheet(
            """
            QSplitter::handle {
                background: lightgray;
            }
            QSplitter::handle:vertical {
                height: 2px;
            }
            """
        )

        fe_header_layout = QHBoxLayout()
        fe_header_layout.setContentsMargins(0, 0, 0, 0)
        fe_header_widget = QWidget()

        fe_header_label = QLabel("Figure Explorer")

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_display)
        refresh_button.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/refresh_icon.png"))
        )

        fe_header_layout.addWidget(fe_header_label)
        fe_header_layout.addStretch()
        fe_header_layout.addWidget(refresh_button)
        fe_header_widget.setLayout(fe_header_layout)

        fe_layout = QVBoxLayout()
        fe_layout.setContentsMargins(0, 0, 0, 5)
        fe_widget = QWidget()
        fe_layout.addWidget(fe_header_widget)
        fe_layout.addWidget(self.fe)

        fe_widget.setLayout(fe_layout)
        left_splitter.addWidget(fe_widget)

        # left_splitter.addWidget(self.fe)
        pi_layout = QVBoxLayout()
        pi_layout.setContentsMargins(0, 5, 5, 0)
        pi_header_widget = QLabel("Property Inspector")
        pi_layout.addWidget(pi_header_widget)
        pi_layout.addWidget(self.pi)
        pi_widget = QWidget()
        pi_widget.setLayout(pi_layout)

        left_splitter.addWidget(pi_widget)

        splitter.addWidget(left_splitter)

        figure_widget = QWidget()
        figure_layout = QVBoxLayout(figure_widget)
        figure_layout.setContentsMargins(5, 0, 0, 0)
        figure_layout.addWidget(self.fm.canvas)
        splitter.addWidget(figure_widget)

        main_widget = QWidget()
        # main_widget.setStyleSheet("border: 2px solid red;")
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

    def save_work_dialog(self):
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Question)
        dialog.setWindowTitle("Save Work")
        dialog.setText("Do you want to save your work?")
        dialog.setStandardButtons(
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        dialog.setDefaultButton(QMessageBox.Save)
        button = dialog.exec()
        return button

    def new_file(self):
        if self.fm.unsaved_changes:
            res = self.save_work_dialog()
            if res == QMessageBox.Save:
                self.save_file()
            elif res == QMessageBox.Discard:
                pass
            elif res == QMessageBox.Cancel:
                return
        self.fm.new_figure()

    def open_file(self):
        if self.fm.unsaved_changes:
            res = self.save_work_dialog()
            if res == QMessageBox.Save:
                self.save_file()
            elif res == QMessageBox.Discard:
                pass
            elif res == QMessageBox.Cancel:
                return
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Figure Files (*.pkl)", options=options
        )
        if file_name:
            self.fm.file_name = file_name
            self.fm.load_figure(self.fm.file_name)

    def save_file(self):
        if self.fm.file_name is None:
            self.save_as_file()
        else:
            self.fm.save_figure(self.fm.file_name)

    def save_as_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Figure Files (*.pkl)", options=options
        )
        if file_name:
            self.fm.file_name = file_name
            self.fm.save_figure(self.fm.file_name)

    def export_figure(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Figure", "", "PNG Files (*.png)", options=options
        )
        if file_name:
            self.fm.figure.savefig(file_name)

    def quit(self):
        if self.fm.unsaved_changes:
            res = self.save_work_dialog()
            if res == QMessageBox.Save:
                self.save_file()
            elif res == QMessageBox.Discard:
                self.close()
            elif res == QMessageBox.Cancel:
                return
        else:
            self.close()

    def open_plugins_folder(self):
        path = os.path.join(CURRENT_DIR, "plugins")
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def plugins_documentation(self):
        url = QUrl("https://github.com/nogula/FigureForge/wiki/Plugins")
        QDesktopServices.openUrl(url)

    def about_pressed(self):
        dialog = QDialog()
        dialog.setWindowTitle("About FigureForge")
        dialog.setWindowIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/logo.png"))
        )
        layout = QGridLayout()

        logo = QLabel()
        logo.setPixmap(
            QPixmap(os.path.join(CURRENT_DIR, "resources/assets/logo_color_text.png"))
        )
        # scale logo to 1" by 1"
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

        # Add a spacer between the second label and the third label
        text_layout.addSpacing(10)

        text_layout.addWidget(label3)
        text_layout.addWidget(label4)
        layout.addWidget(text_widget, 0, 1, Qt.AlignTop)

        dialog.setLayout(layout)
        dialog.exec()

    # def about_pressed(self):

    # """Open the GitHub page for this project."""
    # url = QUrl("https://github.com/nogula/FigureForge")
    # QDesktopServices.openUrl(url)

    def help_pressed(self):
        """Goes to the Wiki on the GitHub page."""
        url = QUrl("https://github.com/nogula/FigureForge/wiki")
        QDesktopServices.openUrl(url)

    def bug_pressed(self):
        """Open the issues page for the GitHub project."""
        url = QUrl("https://github.com/nogula/FigureForge/issues/new")
        QDesktopServices.openUrl(url)

    def load_plugins(self):

        plugin_dir = os.path.join(CURRENT_DIR, "plugins")
        if not os.path.exists(plugin_dir):
            return

        for file_name in os.listdir(plugin_dir):
            if file_name.endswith(".py"):
                module_name = file_name[:-3]
                module_path = os.path.join(plugin_dir, file_name)
                try:
                    module = importlib.import_module(
                        f"FigureForge.plugins.{module_name}"
                    )
                    classes = [
                        cls
                        for cls in inspect.getmembers(module, inspect.isclass)
                        if cls[1].__module__ == module.__name__
                    ]
                    for cls in classes:
                        cls = cls[1]
                        if isinstance(cls, type):
                            action = QAction(cls.name, self)
                            if hasattr(cls, "tooltip"):
                                action.setToolTip(cls.tooltip)
                            if hasattr(cls, "icon"):
                                action.setIcon(QIcon(cls.icon))
                            action.triggered.connect(
                                lambda checked, obj=cls: self.run_plugin(obj)
                            )
                            self.plugin_menu.addAction(action)
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")

    def run_plugin(self, plugin_class):
        selected_item = self.fm.selected_item
        if selected_item:
            plugin = plugin_class()
            plugin.run(selected_item)
            self.fm.canvas.draw()
            self.fm.unsaved_changes = True
            self.fm.fe.build_tree(self.fm.figure)

    def delete_item(self):
        self.fm.delete_item()

    def configure_gridspec(self):
        self.fm.configure_gridspec()

    def refresh_display(self):
        self.fm.canvas.draw()
        self.fm.fe.build_tree(self.fm.figure)
