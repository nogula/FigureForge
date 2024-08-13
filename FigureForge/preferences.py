import os
import json
import re
from appdirs import user_config_dir

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QFormLayout,
    QDialogButtonBox,
)

import qdarktheme

from FigureForge.__init__ import CURRENT_DIR
from FigureForge import __version__


class Preferences:
    def __init__(self, app_name=__version__, app_author="FigureForge"):
        self.app_name = app_name
        self.app_author = app_author
        self.config_dir = user_config_dir(app_name, app_author)
        self.config_file = os.path.join(self.config_dir, "preferences.json")
        self.defaults = {
            "plugin_directory": os.path.join(CURRENT_DIR, "plugins"),
            "plugin_requirements": os.path.join(
                CURRENT_DIR, "plugins", "requirements.txt"
            ),
            "theme": "dark",
            "last_export_path": "",
            "debug": False,
            "show_welcome": True,
            "recent_files": [],
        }
        self.preferences = self.load_preferences()

    def load_preferences(self):
        """Loads preferences JSON from file. If file does not exist, creates default
        preferences."""
        if not os.path.exists(self.config_file):
            self.create_default_preferences()
            return self.preferences
        with open(self.config_file, "r") as file:
            return json.load(file)

    def save_preferences(self):
        """Writes preferences JSON to file."""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, "w") as file:
            json.dump(self.preferences, file, indent=4)

    def create_default_preferences(self):
        self.preferences = self.defaults.copy()
        previous_preferences = self.check_previous_preferences()
        print(previous_preferences)
        if previous_preferences is not None:
            for key in self.preferences:
                if key in previous_preferences:
                    self.preferences[key] = previous_preferences[key]
        
        self.save_preferences()
        print(f"Created default preferences file at {self.config_file}")

    def check_previous_preferences(self):
        """This method checks for previous preferences files in sibling directories of
        config_dir, and if found, returns the most recent one. Otherwise, returns None."""
        previous_preferences = None
        previous_pref_files = []
        # Get list of previous preference files from sibling directories of config_dir
        for root, dirs, files in os.walk(os.path.dirname(self.config_dir)):
            for file in files:
                if file == "preferences.json":
                    previous_pref_files.append(os.path.join(root, file))
        # Get the most recent preferences file based on version number in directory name
        if previous_pref_files:
            previous_pref_files.sort()
            with open(previous_pref_files[-1], "r") as file:
                previous_preferences = json.load(file)
        return previous_preferences

    def get(self, key):
        return self.preferences.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.preferences[key] = value
        if key == "theme":
            qdarktheme.setup_theme(value)
        self.save_preferences()


class PreferencesDialog(QDialog):
    def __init__(self, preferences, parent=None):
        super().__init__(parent)
        self.preferences = preferences

        self.setWindowTitle("Preferences")
        form_layout = QFormLayout()

        self.plugin_directory_edit = QLineEdit(self)
        self.plugin_directory_edit.setText(self.preferences.get("plugin_directory"))
        plugin_directory_layout = QHBoxLayout()
        plugin_directory_layout.addWidget(self.plugin_directory_edit)
        browse_plugin_dir_button = QPushButton("Browse")
        browse_plugin_dir_button.clicked.connect(self.browse_plugin_directory)
        plugin_directory_layout.addWidget(browse_plugin_dir_button)

        form_layout.addRow(QLabel("Plugin Directory:"), plugin_directory_layout)

        self.plugin_requirements_edit = QLineEdit(self)
        self.plugin_requirements_edit.setText(
            self.preferences.get("plugin_requirements")
        )
        plugin_requirements_layout = QHBoxLayout()
        plugin_requirements_layout.addWidget(self.plugin_requirements_edit)
        browse_requirements_button = QPushButton("Browse")
        browse_requirements_button.clicked.connect(self.browse_plugin_requirements_file)
        plugin_requirements_layout.addWidget(browse_requirements_button)

        form_layout.addRow(
            QLabel("Plugin Requirements File:"), plugin_requirements_layout
        )

        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["auto", "light", "dark"])
        self.theme_combo.setCurrentText(self.preferences.get("theme"))
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(self.theme_combo)
        form_layout.addRow(QLabel("Theme:"), theme_layout)

        self.debug_checkbox = QCheckBox(self)
        self.debug_checkbox.setChecked(self.preferences.get("debug"))
        form_layout.addRow(QLabel("Debug Mode:"), self.debug_checkbox)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_preferences)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def browse_plugin_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Plugin Directory")
        if directory:
            self.plugin_directory_edit.setText(directory)

    def browse_plugin_requirements_file(self):
        file = QFileDialog.getOpenFileName(
            self, "Select Plugin Requirements File", filter="Text Files (*.txt)"
        )[0]
        if file:
            self.plugin_requirements_edit.setText(file)

    def save_preferences(self):
        self.preferences.set("plugin_directory", self.plugin_directory_edit.text())
        self.preferences.set(
            "plugin_requirements", self.plugin_requirements_edit.text()
        )
        self.preferences.set("theme", self.theme_combo.currentText())
        self.preferences.set("debug", self.debug_checkbox.isChecked())
        self.accept()
