import os
import sys
import traceback

from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from FigureForge.gui import MainWindow
from FigureForge.__init__ import CURRENT_DIR


def create_splash():
    pixmap = QPixmap(os.path.join(CURRENT_DIR, "resources", "assets", "splash.png"))
    splash = QSplashScreen(pixmap)
    splash.showMessage("Loading FigureForge...", Qt.AlignBottom | Qt.AlignLeft)
    splash.show()
    return splash


def main():
    try:
        app = QApplication(sys.argv)
        splash = create_splash()
        window = MainWindow(splash)
        window.show()
        splash.finish(window)
        sys.exit(app.exec_())
    except Exception as e:
        error_message = str(e)
        detailed_error = traceback.format_exc()
        with open("error.log", "w") as f:
            f.write(detailed_error)
        print(detailed_error)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("An error occurred")
        msg.setInformativeText(error_message)
        msg.setDetailedText(detailed_error)
        msg.setWindowTitle("Error")
        msg.exec_()


if __name__ == "__main__":
    main()
