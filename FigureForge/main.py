import os
import sys

from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from FigureForge.gui import MainWindow
from FigureForge.__init__ import CURRENT_DIR


def create_splash() -> QSplashScreen:
    """
    Creates and displays a splash screen with a loading message.

    Returns:
        QSplashScreen: The created splash screen.
    """
    pixmap = QPixmap(os.path.join(CURRENT_DIR, "resources", "assets", "splash.png"))
    splash = QSplashScreen(pixmap)
    splash.showMessage("Loading FigureForge...", Qt.AlignBottom | Qt.AlignLeft)
    splash.show()
    return splash


def main() -> None:
    """
    Entry point of the application.

    Initializes the application, creates a splash screen, creates the main window,
    shows the window, finishes the splash screen, and starts the application event loop.
    """
    app = QApplication(sys.argv)
    splash = create_splash()
    window = MainWindow(splash)
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
