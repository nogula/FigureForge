import os

def run(figure = None):
    from .main import main
    main(figure)

__version__ = "0.2.1"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
