import sys
import os
import subprocess
import importlib
import inspect
from io import BytesIO

from PySide6.QtWidgets import (
    QApplication,
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
    QMenu,
)
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QDesktopServices, QIcon, QAction, QPixmap

import qdarktheme

from FigureForge.__init__ import __version__, CURRENT_DIR
from FigureForge.figure_manager import FigureManager
from FigureForge.bug_report_dialog import BugReportDialog
from FigureForge.export_figure_dialog import ExportFigureDialog
from FigureForge.preferences import Preferences, PreferencesDialog


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):
    def __init__(self, splash):
        super().__init__()
        self.setWindowTitle("FigureForge")
        self.setWindowIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/assets/logo.ico"))
        )
        self.setMinimumSize(800, 600)

        self.splash = splash

        self.preferences = Preferences()
        qdarktheme.setup_theme(self.preferences.get("theme"))

        self.create_menus()
        self.init_ui()

        self.show()

    def create_menus(self):
        """Creates the menubar at the top of the main window."""
        self.splash.showMessage("Creating Menus...", Qt.AlignBottom | Qt.AlignLeft)
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

        copy_figure_action = QAction("Copy Figure", self)
        copy_figure_action.triggered.connect(self.copy_figure)
        copy_figure_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/copy_icon.png"))
        )
        copy_figure_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_figure_action)

        delete_item_action = QAction("Delete Item", self)
        delete_item_action.triggered.connect(self.delete_item)
        delete_item_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/delete_icon.png"))
        )
        delete_item_action.setShortcut("Del")
        edit_menu.addAction(delete_item_action)

        reload_structure_action = QAction("Reload Structure", self)
        reload_structure_action.triggered.connect(self.reload_json_structure)
        reload_structure_action.setShortcut("Ctrl+R")
        edit_menu.addAction(reload_structure_action)

        debug_mode_action = QAction("Debug Mode", self)
        debug_mode_action.setCheckable(True)
        debug_mode_action.triggered.connect(self.toggle_debug_mode)
        debug_mode_action.setShortcut("Ctrl+D")
        debug_mode_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/debug_icon.png"))
        )
        edit_menu.addAction(debug_mode_action)

        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.show_preferences_dialog)
        preferences_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/preferences_icon.png"))
        )
        edit_menu.addAction(preferences_action)

        self.plugin_menu = menubar.addMenu("Plugins")
        self.plugin_menu.setToolTipsVisible(True)

        self.load_plugins()
        self.plugin_menu.addSeparator()
        open_plugins_folder_action = QAction("Open Plugins Folder...", self)
        open_plugins_folder_action.triggered.connect(self.open_plugins_folder)
        self.plugin_menu.addAction(open_plugins_folder_action)
        reload_plugins_action = QAction("Reload Plugins", self)
        reload_plugins_action.triggered.connect(self.reload_plugins)
        reload_plugins_action.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/refresh_icon.png"))
        )
        self.plugin_menu.addAction(reload_plugins_action)
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
        """Initializes the main window."""
        self.splash.showMessage("Initializing UI...", Qt.AlignBottom | Qt.AlignLeft)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)

        self.fm = FigureManager(self.preferences, self.setWindowTitle)
        self.fe = self.fm.fe
        self.pi = self.fm.pi

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.setContentsMargins(0, 0, 5, 0)

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
        dialog = ExportFigureDialog(self.preferences, self.fm.figure)
        dialog.exec()
        self.fm.canvas.draw()
        if self.fm.debug:
            print("Exported figure")

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
            QIcon(os.path.join(CURRENT_DIR, "resources/assets/logo.ico"))
        )
        layout = QGridLayout()

        logo = QLabel()
        logo.setPixmap(
            QPixmap(os.path.join(CURRENT_DIR, "resources/assets/logo_color_text.png"))
        )
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

        dialog.setLayout(layout)
        dialog.exec()

    def help_pressed(self):
        """Goes to the Wiki on the GitHub page."""
        url = QUrl("https://github.com/nogula/FigureForge/wiki")
        QDesktopServices.openUrl(url)

    def bug_pressed(self):
        dialog = BugReportDialog(self)
        dialog.exec()

    def load_plugins(self, reload=False):
        self.splash.showMessage("Loading Plugins...", Qt.AlignBottom | Qt.AlignLeft)
        if reload:
            actions = self.plugin_menu.actions()
            total_actions = len(actions)
            actions_to_remove = actions[: total_actions - 3]

            for action in actions_to_remove:
                self.plugin_menu.removeAction(action)

        plugin_dir = self.preferences.get("plugin_directory")
        plugin_requirements_filepath = self.preferences.get("plugin_requirements")
        if os.path.exists(plugin_requirements_filepath):
            try:
                subprocess.check_call(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        plugin_requirements_filepath,
                    ]
                )
            except Exception as e:
                msgbox = QMessageBox()
                msgbox.setIcon(QMessageBox.Critical)
                msgbox.setWindowTitle("Plugin Error")
                msgbox.setText("Failed to install plugin requirements.")
                msgbox.setInformativeText(str(e))
                msgbox.exec_()

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
                    if reload:
                        module = importlib.reload(module)
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
                            if reload:
                                if hasattr(cls, "submenu"):
                                    submenu_exists = False
                                    for submenu in self.plugin_menu.actions():
                                        if submenu.text() == cls.submenu:
                                            submenu_exists = True
                                            break
                                    if not submenu_exists:
                                        submenu = self.plugin_menu.insertMenu(
                                            self.plugin_menu.actions()[
                                                len(self.plugin_menu.actions()) - 3
                                            ],
                                            QMenu(cls.submenu),
                                        )
                                        # submenu.setToolTipsVisible(True)
                                        submenu.menu().addAction(action)
                                    else:
                                        submenu.menu().addAction(action)
                                else:
                                    self.plugin_menu.insertAction(
                                        self.plugin_menu.actions()[
                                            len(self.plugin_menu.actions()) - 3
                                        ],
                                        action,
                                    )
                            else:
                                if hasattr(cls, "submenu"):
                                    submenu_exists = False
                                    for submenu in self.plugin_menu.actions():
                                        if submenu.text() == cls.submenu:
                                            submenu_exists = True
                                            break
                                    if not submenu_exists:
                                        submenu = self.plugin_menu.addMenu(cls.submenu)
                                        submenu.setToolTipsVisible(True)
                                        submenu.addAction(action)
                                    else:
                                        submenu.menu().addAction(action)
                                else:
                                    self.plugin_menu.addAction(action)
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")

        if reload:
            self.plugin_menu.insertSeparator(
                self.plugin_menu.actions()[len(self.plugin_menu.actions()) - 3]
            )

    def run_plugin(self, plugin_class):
        selected_obj = self.fm.selected_obj
        if selected_obj:
            plugin = plugin_class()
            plugin.run(selected_obj)
            self.fm.canvas.draw()
            self.fm.unsaved_changes = True
            self.fm.fe.build_tree(self.fm.figure)

    def delete_item(self):
        self.fm.delete_obj()

    def configure_gridspec(self):
        raise NotImplementedError

    def refresh_display(self):
        self.fm.canvas.draw()
        self.fm.fe.build_tree(self.fm.figure)

    def reload_plugins(self):
        actions = self.plugin_menu.actions()
        total_actions = len(actions)
        actions_to_remove = actions[: total_actions - 3]

        for action in actions_to_remove:
            self.plugin_menu.removeAction(action)

        self.load_plugins(reload=True)

    def reload_json_structure(self):
        self.fm.load_json_structure()
        print("Reloaded JSON structure.")

    def toggle_debug_mode(self):
        self.fm.toggle_debug_mode()

    def show_preferences_dialog(self):
        dialog = PreferencesDialog(self.preferences, self)
        dialog.exec_()

    def copy_figure(self):
        buf = BytesIO()
        self.fm.figure.savefig(buf, format="png")
        buf.seek(0)
        image = QPixmap()
        image.loadFromData(buf.getvalue(), "PNG")

        clipboard = QApplication.clipboard()
        clipboard.setPixmap(image)
