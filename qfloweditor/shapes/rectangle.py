from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QGraphicsItem
from qtpy.QtGui import QPainterPath
from qtpy.QtCore import Qt
from qnodeeditor.graphics.node import QDMGraphicsNode
from qnodeeditor.serializable.node import Node


class RectangleGNode(QDMGraphicsNode):
    def __init__(self, node: Node, parent: QGraphicsItem | None = None):
        super().__init__(node, parent)
        fm = QFontMetrics(self._title_font)
        size = fm.height()
        width = (len(self.title_item.toPlainText())) / 2 * size
        self.title_item.setPos((self.width - width) / 2, self.height / 2 - size / 2)

    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 74
        self.edge_roundness = 0
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def paint(self, painter, option, widget=None):
        if not painter:
            return
        self.initAssets()
        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(0, 0, self.width, self.height,
                                    self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())


        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(-1, -1, self.width+2, self.height+2,
                                    self.edge_roundness, self.edge_roundness)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())