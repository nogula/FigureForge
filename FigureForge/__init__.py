import os


def run(figure=None):
    from .main import main

    main(figure)


__version__ = "0.3.0"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
