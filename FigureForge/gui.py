from math import e
from msilib.schema import Property
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QSplitter,
    QFileDialog,
    QTreeView,
    QVBoxLayout,
    QMenuBar,
    QMainWindow,
    QMessageBox,
    QStatusBar,
)
from PySide6.QtCore import Qt, QUrl, QObject
from PySide6.QtGui import QFont, QDesktopServices, QIcon, QAction, QCursor

import matplotlib.pyplot as plt
import pandas as pd

from .utils import FigureExplorer, FigureManager, PropertyInspector
import os
import importlib
import inspect


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FigureForge")
        self.setMinimumSize(800, 600)

        self.create_menus()
        self.setup_ui()

        self.show()

    def create_menus(self):
        """Creates the menubar at the top of the main window."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setIcon(QIcon("FigureForge/resources/icons/new_icon.png"))
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setIcon(QIcon("FigureForge/resources/icons/open_icon.png"))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setIcon(QIcon("FigureForge/resources/icons/save_icon.png"))
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setIcon(QIcon("FigureForge/resources/icons/save_as_icon.png"))
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_figure)
        export_action.setIcon(QIcon("FigureForge/resources/icons/export_icon.png"))
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        quit_action.setIcon(QIcon("FigureForge/resources/icons/quit_icon.png"))
        quit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(quit_action)

        edit_menu = menubar.addMenu("Edit")

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
        about_action.setIcon(QIcon("FigureForge/resources/icons/about_icon.png"))
        help_menu.addAction(about_action)

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.help_pressed)
        help_action.setIcon(QIcon("FigureForge/resources/icons/documentation_icon.png"))
        help_menu.addAction(help_action)

        bug_action = QAction("Report Bug", self)
        bug_action.triggered.connect(self.bug_pressed)
        bug_action.setIcon(QIcon("FigureForge/resources/icons/bug_icon.png"))
        help_menu.addAction(bug_action)

    def setup_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        self.fm = FigureManager()
        self.fe = self.fm.fe
        self.pi = self.fm.pi

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.fe)
        left_splitter.addWidget(self.pi)

        splitter.addWidget(left_splitter)
        splitter.addWidget(self.fm.canvas)

        main_widget = QWidget()
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
        path = os.path.join(os.path.dirname(__file__), "plugins")
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def plugins_documentation(self):
        url = QUrl("https://github.com/nogula/FigureForge/wiki/Plugins")
        QDesktopServices.openUrl(url)

    def about_pressed(self):
        """Open the GitHub page for this project."""
        url = QUrl("https://github.com/nogula/FigureForge")
        QDesktopServices.openUrl(url)

    def help_pressed(self):
        """Goes to the Wiki on the GitHub page."""
        url = QUrl("https://github.com/nogula/FigureForge/wiki")
        QDesktopServices.openUrl(url)

    def bug_pressed(self):
        """Open the issues page for the GitHub project."""
        url = QUrl("https://github.com/nogula/FigureForge/issues/new")
        QDesktopServices.openUrl(url)

    def load_plugins(self):

        plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
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
