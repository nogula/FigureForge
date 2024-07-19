import os

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from .gui import MainWindow
from .__init__ import CURRENT_DIR


def create_splash(app):
    pixmap = QPixmap(os.path.join(CURRENT_DIR, "resources","assets","splash.png"))
    splash = QSplashScreen(pixmap)
    splash.showMessage("Loading FigureForge...", Qt.AlignBottom | Qt.AlignLeft)
    splash.show()
    return splash

def main():
    app = QApplication([])
    splash = create_splash(app)
    window = MainWindow(splash)
    window.show()
    splash.finish(window)
    app.exec()



if __name__ == "__main__":
    main()
