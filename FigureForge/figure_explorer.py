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
        reload_button = QPushButton("Reload")
        reload_button.setToolTip("Reload from file")
        reload_button.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/refresh_icon.png"))
        )
        reload_button.clicked.connect(self.refreshTree.emit)
        header_layout.addWidget(reload_button)
        layout.addLayout(header_layout)
        self.tree = QTreeWidget()
        self.tree.header().hide()
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def build_tree(self, figure, last_obj = None):
        self.tree.clear()
        self.tree.addTopLevelItem(QTreeWidgetItem(["Figure"]))
        root = self.tree.topLevelItem(0)
        root.reference = figure
        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item, last_obj)
        self.tree.expandItem(root)

    def add_item(self, parent, child, last_obj):
        class_name = child.__class__.__name__
        if child.get_label() != "":
            label = f"{class_name} - {child.get_label()}"
        else:
            label = class_name
        parent.addChild(QTreeWidgetItem([label]))
        root = parent.child(parent.childCount() - 1)
        root.reference = child

        if last_obj is not None and last_obj == child:
            self.tree.setCurrentItem(root)

        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item, last_obj)

    def on_item_clicked(self, item):
        self.itemSelected.emit(item.reference)
