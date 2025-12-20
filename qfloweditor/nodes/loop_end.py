from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QHBoxLayout
from qtpy.QtGui import QFont
from qfloweditor.alg_conf import register_alg_node
from qfloweditor.alg_node import AlgNode
from qfloweditor.shapes.loop_end import LoopEndGNode
from qnodeeditor.serializable.content_widget import QDMNodeContentWidget
from qnodeeditor.serializable.socket import SocketPosition


class LoopEndContent(QDMNodeContentWidget):
    def initUI(self):
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont('Consolas', 12)
        self.lbl1 = QLabel(f'')
        self.lbl1.setFont(font)
        self.current_value: int = 0;
        self.lbl2 = QLabel(f'{self.current_value}')
        self.lbl2.setFont(font)
        self._layout.addWidget(self.lbl1)
        self._layout.addWidget(self.lbl2)
        self._routine_task = None

    def increment(self) -> int:
        self.current_value += 1
        self.lbl2.setText(f'{self.current_value}')
        return self.current_value

    def refresh(self):
        self.current_value = 0
        self.lbl2.setText(f'{self.current_value}')


@register_alg_node('LOOP_END')
class AlgNode_LoopEnd(AlgNode):
    node_type = 'LOOP_END'
    label = "LoopEnd"
    GraphicsNode_class = LoopEndGNode
    NodeContent_class = LoopEndContent
    def __init__(self, scene,
                 inputs=[(1, SocketPosition.TOP_CENTER)],
                 outputs=[(2, SocketPosition.BOTTOM_CENTER)]):
        super().__init__(scene, inputs, outputs)