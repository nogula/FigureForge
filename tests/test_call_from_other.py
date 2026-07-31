import sys
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PySide6 import QtCore
import matplotlib.pyplot as plt
import numpy as np
from FigureForge.main import create_MainWindow


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PySide6 Test")

        self.button = QPushButton("Figure Forge!")
        self.button.clicked.connect(self.on_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_button_clicked(self) -> None:
        xs = np.random.normal(size=1000)
        ys = xs + np.random.normal(1, 1, 1000) + 0.1

        fig, ax = plt.subplots(figsize=[4, 3])
        fig.dpi = 150
        ax.plot(xs, ys, 'o', label='some data')

        ax.set_xlabel('x label')
        ax.set_ylabel('y label')
        ax.legend()

        window = create_MainWindow(fig)
        # window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        window.show()
        
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
