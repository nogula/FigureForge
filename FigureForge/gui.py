import sys
import os
import subprocess
import importlib
import inspect
from io import BytesIO
from copy import deepcopy

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QSplitter,
    QFileDialog,
    QVBoxLayout,
    QMainWindow,
    QMessageBox,
    QMenu,
    QTabWidget,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QAction, QPixmap

import qdarktheme

from FigureForge.__init__ import (
    __version__,
    ICONS_DIR,
    CURRENT_DIR,
    ASSETS_DIR,
)
from FigureForge.dialogs.ff_dialogs import (
    check_for_updates,
    NewPluginDialog,
    ExportFigureDialog,
    BugReportDialog,
    AboutDialog,
    SaveWorkDialog,
    WelcomeDialog,
)
from FigureForge.figure_manager import FigureManager
from FigureForge.preferences import Preferences, PreferencesDialog


class MainWindow(QMainWindow):
    def __init__(self, splash, figure):
        super().__init__()
        self.setWindowTitle("FigureForge")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "logo.ico")))
        self.setMinimumSize(800, 600)

        self.splash = splash

        self.preferences = Preferences()
        qdarktheme.setup_theme(self.preferences.get("theme"))

        self.create_menus()
        self.init_ui(figure)

        self.show()
        if self.preferences.get("show_welcome"):
            res = WelcomeDialog()
            if res.display_at_startup.isChecked():
                self.preferences.set("show_welcome", True)
            else:
                self.preferences.set("show_welcome", False)
            if res.check_for_updates.isChecked():
                self.preferences.set("check_for_updates", True)
            else:
                self.preferences.set("check_for_updates", False)
        if self.preferences.get("check_for_updates"):
            res = check_for_updates()
            if res is not None:
                self.preferences.set("check_for_updates", res)

    def create_menus(self):
        """Creates the menubar at the top of the main window."""
        self.splash.showMessage("Creating Menus...", Qt.AlignBottom | Qt.AlignLeft)
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setIcon(QIcon(os.path.join(ICONS_DIR, "new_icon.png")))
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setIcon(QIcon(os.path.join(ICONS_DIR, "open_icon.png")))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        self.open_recent_menu = QMenu("Open Recent", self)
        file_menu.addMenu(self.open_recent_menu)
        self.get_recent_files()

        save_action = QAction("Save", self)
        save_action.setIcon(QIcon(os.path.join(ICONS_DIR, "save_icon.png")))
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setIcon(QIcon(os.path.join(ICONS_DIR, "save_as_icon.png")))
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_figure)
        export_action.setIcon(QIcon(os.path.join(ICONS_DIR, "export_icon.png")))
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        quit_action.setIcon(QIcon(os.path.join(ICONS_DIR, "quit_icon.png")))
        quit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(quit_action)

        edit_menu = menubar.addMenu("Edit")

        open_plt_action = QAction("Open in Matplotlib", self)
        open_plt_action.triggered.connect(self.try_open_matplotlib)
        open_plt_action.setIcon(QIcon(os.path.join(ICONS_DIR, "open_icon.png")))
        edit_menu.addAction(open_plt_action)

        copy_figure_action = QAction("Copy Figure", self)
        copy_figure_action.triggered.connect(self.copy_figure)
        copy_figure_action.setIcon(QIcon(os.path.join(ICONS_DIR, "copy_icon.png")))
        copy_figure_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_figure_action)

        delete_item_action = QAction("Delete Item", self)
        delete_item_action.triggered.connect(lambda: self.fm.delete_item())
        delete_item_action.setIcon(QIcon(os.path.join(ICONS_DIR, "delete_icon.png")))
        delete_item_action.setShortcut("Del")
        edit_menu.addAction(delete_item_action)

        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(
            lambda: PreferencesDialog(self.preferences, self)
        )
        preferences_action.setIcon(
            QIcon(os.path.join(ICONS_DIR, "preferences_icon.png"))
        )
        edit_menu.addAction(preferences_action)

        self.plugin_menu = menubar.addMenu("Plugins")
        self.plugin_menu.setToolTipsVisible(True)

        self.load_plugins()
        self.plugin_menu.addSeparator()
        open_plugins_folder_action = QAction("Open Plugins Folder...", self)
        open_plugins_folder_action.triggered.connect(
            lambda: QDesktopServices.openUrl(
                QUrl.fromLocalFile(self.preferences.get("plugin_directory"))
            )
        )
        open_plugins_folder_action.setIcon(
            QIcon(os.path.join(ICONS_DIR, "folder_icon.png"))
        )
        self.plugin_menu.addAction(open_plugins_folder_action)
        reload_plugins_action = QAction("Reload Plugins", self)
        reload_plugins_action.triggered.connect(self.reload_plugins)
        reload_plugins_action.setIcon(
            QIcon(os.path.join(ICONS_DIR, "refresh_icon.png"))
        )
        self.plugin_menu.addAction(reload_plugins_action)
        plugins_documentation_action = QAction("Plugins Documentation", self)
        plugins_documentation_action.triggered.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/nogula/FigureForge/wiki/Plugins")
            )
        )
        plugins_documentation_action.setIcon(
            QIcon(os.path.join(ICONS_DIR, "documentation_icon.png"))
        )
        self.plugin_menu.addAction(plugins_documentation_action)
        new_plugin_action = QAction("New Plugin", self)
        new_plugin_action.triggered.connect(self.new_plugin)
        new_plugin_action.setIcon(QIcon(os.path.join(ICONS_DIR, "new_icon.png")))
        self.plugin_menu.addAction(new_plugin_action)

        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(lambda: AboutDialog())
        about_action.setIcon(QIcon(os.path.join(ICONS_DIR, "about_icon.png")))
        help_menu.addAction(about_action)

        help_action = QAction("Help", self)
        help_action.triggered.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/nogula/FigureForge/wiki")
            )
        )
        help_action.setIcon(QIcon(os.path.join(ICONS_DIR, "documentation_icon.png")))
        help_menu.addAction(help_action)

        bug_action = QAction("Report Bug", self)
        bug_action.triggered.connect(lambda: BugReportDialog(self))
        bug_action.setIcon(QIcon(os.path.join(ICONS_DIR, "bug_icon.png")))
        help_menu.addAction(bug_action)

    def init_ui(self, figure):
        """Initializes the main window."""
        self.splash.showMessage("Initializing UI...", Qt.AlignBottom | Qt.AlignLeft)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)

        self.fm = FigureManager(self.preferences, figure)
        self.figure_managers = [self.fm]
        self.tab_widget = QTabWidget(tabsClosable=True)
        self.tab_widget.currentChanged.connect(self.change_tab)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        figure_widget = QWidget()
        figure_layout = QVBoxLayout(figure_widget)
        figure_layout.setContentsMargins(5, 0, 0, 0)
        figure_layout.addWidget(self.fm.canvas)
        self.tab_widget.addTab(figure_widget, "New Figure")

        self.fe = self.fm.fe
        self.pi = self.fm.pi

        self.left_splitter = QSplitter(Qt.Vertical)
        self.left_splitter.setContentsMargins(0, 0, 5, 0)
        self.left_splitter.addWidget(self.fe)

        self.left_splitter.addWidget(self.pi)
        splitter.addWidget(self.left_splitter)
        splitter.addWidget(self.tab_widget)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

    def new_file(self):
        new_fm = FigureManager(self.preferences, None)
        self.figure_managers.append(new_fm)

        self.tab_widget.addTab(new_fm.canvas, "New Figure")
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        new_fm.updateLabel.connect(
            lambda label: self.tab_widget.setTabText(
                self.tab_widget.currentIndex(), label
            )
        )

    def open_file(self):
        if not self.check_for_save(self.fm):
            return
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Figure Files (*.pkl)", options=options
        )
        if file_name:
            self.fm.file_name = file_name
            self.fm.load_figure(self.fm.file_name)
            tab_title = (
                self.fm.file_name.split("/")[-1]
                if self.fm.file_name is not None
                else "New Figure"
            )
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab_title)

    def save_file(self):
        if self.fm.file_name is None:
            self.save_as_file()
        else:
            self.fm.save_figure(self.fm.file_name)
        self.update_recent_files()
        self.tab_widget.setTabText(
            self.tab_widget.currentIndex(),
            (
                self.fm.file_name.split("/")[-1]
                if self.fm.file_name is not None
                else "New Figure"
            ),
        )

    def save_as_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Figure Files (*.pkl)", options=options
        )
        if file_name:
            self.fm.file_name = file_name
            self.fm.save_figure(self.fm.file_name)
        self.update_recent_files()

    def export_figure(self):
        old_dpi = self.fm.figure.get_dpi()
        ExportFigureDialog(self.preferences, self.fm.figure)
        if self.preferences.get("debug"):
            print("Exported figure")
        self.fm.figure.set_dpi(old_dpi)
        self.fm.canvas.draw()

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
                                lambda _, obj=cls: self.run_plugin(obj)
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
            self.fm.fe.build_tree(self.fm.figure, selected_obj)

    def reload_plugins(self):
        actions = self.plugin_menu.actions()
        total_actions = len(actions)
        actions_to_remove = actions[: total_actions - 4]

        for action in actions_to_remove:
            self.plugin_menu.removeAction(action)

        self.load_plugins(reload=True)

    def new_plugin(self):
        """Creates a new plugin file from the template and opens it in the default app."""
        template_filename = os.path.join(
            CURRENT_DIR, "resources/templates/plugin_template.py"
        )
        plugin_dir = self.preferences.get("plugin_directory")
        new_plugin_filename = os.path.join(plugin_dir, "new_plugin.py")
        with open(template_filename, "r") as template_file:
            template = template_file.read()
        with open(new_plugin_filename, "w") as new_plugin_file:
            new_plugin_file.write(template)
        self.reload_plugins()

        NewPluginDialog(new_plugin_filename, plugin_dir)

    def copy_figure(self):
        buf = BytesIO()
        self.fm.figure.savefig(buf, format="png")
        buf.seek(0)
        image = QPixmap()
        image.loadFromData(buf.getvalue(), "PNG")

        clipboard = QApplication.clipboard()
        clipboard.setPixmap(image)
        buf.close()

    def get_recent_files(self):
        self.open_recent_menu.clear()
        for file in self.preferences.get("recent_files"):
            action = QAction(file, self)
            action.triggered.connect(lambda _, file=file: self.open_recent_file(file))
            self.open_recent_menu.addAction(action)

    def open_recent_file(self, file):
        if not self.check_for_save(self.fm):
            return
        self.fm.file_name = file
        self.fm.load_figure(self.fm.file_name)
        tab_title = (
            self.fm.file_name.split("/")[-1]
            if self.fm.file_name is not None
            else "New Figure"
        )
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab_title)

    def update_recent_files(self):
        recent_files = self.preferences.get("recent_files")
        if self.fm.file_name in recent_files:
            recent_files.remove(self.fm.file_name)
        else:
            if len(recent_files) >= 5:
                recent_files.pop()
        recent_files.insert(0, self.fm.file_name)
        self.preferences.set("recent_files", recent_files)
        self.get_recent_files()

        print(f"Updated recent files: {recent_files}")

    def change_tab(self, index):
        try:
            self.fm = self.figure_managers[index]
            self.fe = self.fm.fe
            self.pi = self.fm.pi
            self.left_splitter.replaceWidget(0, self.fe)
            self.left_splitter.replaceWidget(1, self.pi)
        except AttributeError:
            pass

    def close_tab(self, index):
        if not self.check_for_save(self.figure_managers[index]):
            return
        self.figure_managers.pop(index)
        self.tab_widget.removeTab(index)

    def quit(self):
        if not self.check_for_save(self.fm):
            return
        else:
            self.close()

    def closeEvent(self, event):
        for fm in self.figure_managers:
            if not self.check_for_save(fm):
                event.ignore()
                return
        event.accept()

    def check_for_save(self, fm):
        if fm.unsaved_changes:
            res = SaveWorkDialog(fm.file_name)
            if res == QMessageBox.Save:
                self.save_file()
            elif res == QMessageBox.Discard:
                pass
            elif res == QMessageBox.Cancel:
                return False
        return True
    
    def try_open_matplotlib(self):
        try:
            # import matplotlib.pyplot as plt
            # plt.show()
            figure = deepcopy(self.fm.figure)
            figure.show()
        except Exception as e:
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle("Matplotlib Error")
            msgbox.setText("Failed to open Matplotlib.")
            msgbox.setInformativeText(str(e))
            msgbox.exec_()
