from typing import Type
from qtpy.QtGui import QPixmap, QIcon, QDrag
from qtpy.QtCore import QSize, Qt, QByteArray, QDataStream, QMimeData, QIODevice, QPoint
from qtpy.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem

from qfloweditor.alg_node import AlgNode
from qnodeeditor.utils import dumpException


class QDMDragListbox(QListWidget):
    def __init__(self, node_types: list[Type[AlgNode]], parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        for node_type in node_types:
            self.addMyItem(node_type.label, node_type.node_type)

    def addMyItem(self, name, node_type: str, icon=None):
        item = QListWidgetItem(name, self) # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.ItemDataRole.UserRole, node_type)

    def startDrag(self, *args, **kwargs):
        try:
            item = self.currentItem()
            if not item:
                return
            node_type: str = item.data(Qt.ItemDataRole.UserRole)

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.OpenModeFlag.WriteOnly)
            dataStream.writeQString(node_type)
            mimeData = QMimeData()
            mimeData.setData("application/x-item", itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)

            drag.exec(Qt.DropAction.MoveAction)

        except Exception as e: dumpException(e)