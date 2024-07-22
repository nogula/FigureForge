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
)


class Preferences:
    def __init__(self, app_name="FigureForge", app_author="FigureForge"):
        self.app_name = app_name
        self.app_author = app_author
        self.config_dir = user_config_dir(app_name, app_author)
        self.config_file = os.path.join(self.config_dir, "preferences.json")
        self.defaults = {
            "plugin_directory": "",
            "plugin_requirements": "",
            "theme": "light",
        }
        self.preferences = self.load_preferences()

    def load_preferences(self):
        print(f"Loading preferences from: {self.config_file}")
        if not os.path.exists(self.config_file):
            print("Preferences file does not exist, creating default preferences.")
            return self.create_default_preferences()
        with open(self.config_file, "r") as file:
            print("Preferences file found, loading.")
            return json.load(file)

    def save_preferences(self):
        try:
            if not os.path.exists(self.config_dir):
                print(f"Directory does not exist, creating: {self.config_dir}")
                os.makedirs(self.config_dir, exist_ok=True)
                print(f"Directory created: {self.config_dir}")
            else:
                print(f"Directory already exists: {self.config_dir}")

            print(f"Contents of parent directory ({os.path.dirname(self.config_dir)}):")
            print(os.listdir(os.path.dirname(self.config_dir)))

            with open(self.config_file, "w") as file:
                json.dump(self.preferences, file, indent=4)
            print(f"Preferences saved to: {self.config_file}")
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def create_default_preferences(self):
        print("Creating default preferences.")
        self.preferences = self.defaults.copy()
        self.save_preferences()
        return self.preferences

    def get(self, key):
        return self.preferences.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.preferences[key] = value
        self.save_preferences()

    def print_config_path(self):
        print(f"Config file path: {self.config_file}")
        return self.config_file


class PreferencesDialog(QDialog):
    def __init__(self, preferences, parent=None):
        super().__init__(parent)
        self.preferences = preferences

        self.setWindowTitle("Preferences")
        self.setLayout(QVBoxLayout())

        self.plugin_directory_edit = QLineEdit(self)
        self.plugin_directory_edit.setText(self.preferences.get("plugin_directory"))

        plugin_directory_layout = QHBoxLayout()
        plugin_directory_layout.addWidget(QLabel("Plugin Directory:"))
        plugin_directory_layout.addWidget(self.plugin_directory_edit)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_plugin_directory)
        plugin_directory_layout.addWidget(browse_button)

        self.layout().addLayout(plugin_directory_layout)

        self.plugin_requirements_edit = QLineEdit(self)
        self.plugin_requirements_edit.setText(
            self.preferences.get("plugin_requirements")
        )
        plugin_requirements_layout = QHBoxLayout()
        plugin_requirements_layout.addWidget(QLabel("Plugin Requirements:"))
        plugin_requirements_layout.addWidget(self.plugin_requirements_edit)
        self.layout().addLayout(plugin_requirements_layout)

        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(self.preferences.get("theme"))
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme_combo)
        self.layout().addLayout(theme_layout)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_preferences)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        self.layout().addLayout(buttons_layout)

    def browse_plugin_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Plugin Directory")
        if directory:
            self.plugin_directory_edit.setText(directory)

    def save_preferences(self):
        self.preferences.set("plugin_directory", self.plugin_directory_edit.text())
        self.preferences.set(
            "plugin_requirements", self.plugin_requirements_edit.text()
        )
        self.preferences.set("theme", self.theme_combo.currentText())
        self.accept()
