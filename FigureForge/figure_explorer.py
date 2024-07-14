from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
)
from PySide6.QtCore import Signal


class FigureExplorer(QTreeWidget):
    itemSelected = Signal(object)

    def __init__(self):
        super().__init__()
        self.itemClicked.connect(self.on_item_clicked)

        self.init_ui()

    def init_ui(self):
        self.header().hide()
        pass

    def build_tree(self, figure):
        self.clear()
        self.addTopLevelItem(QTreeWidgetItem(["Figure"]))
        root = self.topLevelItem(0)
        root.reference = figure
        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item)

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
