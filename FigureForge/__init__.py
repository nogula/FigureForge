import os

import FigureForge.plugins as plugins


def run(figure=None):
    from .main import main

    main(figure)


__version__ = "0.3.1"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, "resources", "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "resources", "icons")
PLUGINS_DIR = os.path.join(CURRENT_DIR, "plugins")
