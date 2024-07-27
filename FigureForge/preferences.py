import os
import json
from appdirs import user_config_dir, user_data_dir

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
        }
        self.preferences = self.load_preferences()

    def load_preferences(self):
        if not os.path.exists(self.config_file):
            self.create_default_preferences()
            return self.preferences
        with open(self.config_file, "r") as file:
            return json.load(file)

    def save_preferences(self):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, "w") as file:
            json.dump(self.preferences, file, indent=4)

    def create_default_preferences(self):
        print("Creating default preferences.")
        self.preferences = self.defaults.copy()
        self.save_preferences()

    def get(self, key):
        return self.preferences.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.preferences[key] = value
        if key == "theme":
            qdarktheme.setup_theme(value)
        self.save_preferences()

    def print_config_path(self):
        print(f"Config file path: {self.config_file}")
        return self.config_file


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
        self.accept()
