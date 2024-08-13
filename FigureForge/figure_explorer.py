import os

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QLabel,
    QWidget,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon

from FigureForge.__init__ import CURRENT_DIR


class FigureExplorer(QWidget):
    itemSelected = Signal(object)
    refreshTree = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Figure Explorer"))
        header_layout.addStretch()
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/refresh_icon.png"))
        )
        refresh_button.clicked.connect(self.refreshTree.emit)
        header_layout.addWidget(refresh_button)
        layout.addLayout(header_layout)
        self.tree = QTreeWidget()
        self.tree.header().hide()
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def build_tree(self, figure):
        self.tree.clear()
        self.tree.addTopLevelItem(QTreeWidgetItem(["Figure"]))
        root = self.tree.topLevelItem(0)
        root.reference = figure
        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item)
        self.tree.expandItem(root)

    def add_item(self, parent, child):
        class_name = child.__class__.__name__
        if child.get_label() != "":
            label = f"{class_name} - {child.get_label()}"
        else:
            label = class_name
        parent.addChild(QTreeWidgetItem([label]))
        root = parent.child(parent.childCount() - 1)
        root.reference = child

        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item)

    def on_item_clicked(self, item):
        self.itemSelected.emit(item.reference)
