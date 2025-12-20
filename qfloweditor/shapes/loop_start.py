from PyQt6.QtGui import QPainterPath, QFontMetrics, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem
from qtpy.QtGui import QPolygonF
from qtpy.QtCore import Qt, QPointF
from qnodeeditor.graphics.node import QDMGraphicsNode
from qnodeeditor.serializable.node import Node
from qnodeeditor.colors import colors


class LoopStartGNode(QDMGraphicsNode):
    def __init__(self, node: Node, parent: QGraphicsItem | None = None):
        super().__init__(node, parent)
        fm = QFontMetrics(self._title_font)
        size = fm.height()
        width = (len(self.title_item.toPlainText())) / 2 * size
        self.title_item.setPos((self.width - width) / 2, self.height / 2 - size / 2 - 20)

    def initSizes(self):
        super().initSizes()
        self.content_width = 200
        self.height = 80
        self.width = self.content_width + self.height
        self.edge_roundness = 0
        self.edge_padding = 0
        self.title_horizontal_padding = 0
        self.title_vertical_padding = 0

    def paint(self, painter, option, widget=None):
        if not painter:
            return

        # content
        path_content = QPainterPath(QPointF(0, 0))
        path_content.setFillRule(Qt.FillRule.WindingFill)
        # path_content.lineTo()
        path_content.addPolygon(QPolygonF( [
            QPointF(0, self.height),
            QPointF(0, self.height / 3),
            QPointF(self.width / 2 - self.content_width / 2, 0),
            QPointF(self.width / 2 + self.content_width / 2, 0),
            QPointF(self.width, self.height / 3),
            QPointF(self.width, self.height),
        ] ))
        # path_content.lineTo(0, self.height / 2)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(colors.loop_start_bg)))
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addPolygon(QPolygonF( [
            QPointF(0, self.height),
            QPointF(0, self.height / 3),
            QPointF(self.width / 2 - self.content_width / 2, 0),
            QPointF(self.width / 2 + self.content_width / 2, 0),
            QPointF(self.width, self.height / 3),
            QPointF(self.width, self.height),
        ] ))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())
