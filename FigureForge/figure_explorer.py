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

import matplotlib as mpl


class FigureExplorer(QWidget):
    itemSelected = Signal(object)
    refreshTree = Signal()

    # These artists should be pickable
    PICKABLE_ARTISTS = (mpl.lines.Line2D, # Line and dots
                        mpl.collections.PathCollection, # Scatter
                        # mpl.patches.Rectangle, # Barplots
                        mpl.collections.PolyCollection, # Stacked plots and fill-betweens
                        mpl.image.AxesImage, # Image
                        mpl.text.Text
                        )
    
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

    def build_tree(self, figure, last_obj=None):
        self.tree.clear()
        self.tree.addTopLevelItem(QTreeWidgetItem(["Figure"]))
        root = self.tree.topLevelItem(0)
        root.reference = figure
        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item, last_obj)
        self.tree.expandItem(root)

    def select_item_for_reference(self, target):
        item = self._find_item_by_reference_recursive(self.tree.invisibleRootItem(), target)
        if item is None:
            return None

        parent = item.parent()
        while parent is not None:
            self.tree.expandItem(parent)
            parent = parent.parent()

        self.tree.setCurrentItem(item)
        self.tree.scrollToItem(item)
        return item

    def add_item(self, parent, child, last_obj):
        class_name = child.__class__.__name__

        # Make pick-able artists that is directly under Figure or Axes pick-able
        if (
            isinstance(child, (mpl.legend.Legend, mpl.axes.Axes) + self.PICKABLE_ARTISTS)
            and isinstance(parent.reference, (mpl.axes.Axes, mpl.figure.Figure))
        ):
            child.set_picker(5)

        # This make sure 
        if isinstance(parent.reference, mpl.axis.Axis):
            child.set_picker(5)
            child.pick_parent_instead = True

        # Make drag-able artists drag-able
        if isinstance(child, mpl.text.Annotation):
            child.draggable()
        if isinstance(child, mpl.legend.Legend):
            child.set_draggable(True)


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

    def _find_item_by_reference_recursive(self, parent, target):
        for index in range(parent.childCount()):
            child = parent.child(index)
            if getattr(child, "reference", None) is target:
                return child

            match = self._find_item_by_reference_recursive(child, target)
            if match is not None:
                return match

        return None
