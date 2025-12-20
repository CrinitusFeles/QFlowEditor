from qtpy.QtWidgets import QLabel, QSpinBox, QHBoxLayout
from qtpy.QtGui import QFont
from qfloweditor.alg_conf import register_alg_node
from qfloweditor.alg_node import AlgNode
from qfloweditor.shapes.loop_start import LoopStartGNode
from qnodeeditor.scene.models import ContentModel
from qnodeeditor.serializable.content_widget import QDMNodeContentWidget
from qnodeeditor.serializable.socket import SocketPosition


class LoopModel(ContentModel):
    counter: int


class LoopContent(QDMNodeContentWidget):
    ContentModelClass = LoopModel
    def initUI(self):
        self.letter: str = get_letter()
        self._layout = QHBoxLayout()
        self._layout.setSpacing(1)
        self.setLayout(self._layout)
        font = QFont('Consolas', 12)
        self.lbl1 = QLabel(f'for {self.letter} = 0; {self.letter} < ')
        self.lbl1.setFont(font)
        self.counter = QSpinBox()
        self.lbl2 = QLabel(f'; {self.letter} += 1')
        self.lbl2.setFont(font)
        self._layout.addWidget(self.lbl1)
        self._layout.addWidget(self.counter)
        self._layout.addWidget(self.lbl2)
        self._routine_task = None

    def serialize(self, **kwargs) -> LoopModel:  # type: ignore
        return super().serialize(counter=self.counter.value(), **kwargs)  # type: ignore

    def deserialize(self, data: dict, hashmap: dict):  # type: ignore
        try:
            model = LoopModel(**data)
            self.counter.setValue(model.counter)
            return True
        except Exception as e:
            print(e)
        return False


loops_variables = ['i', 'j', 'k', 'x', 'y', 'z', 'm', 'n', 'a']
LOOPS_AMOUNT = 0


def get_letter():
    global LOOPS_AMOUNT
    if LOOPS_AMOUNT < len(loops_variables):
        result = loops_variables[LOOPS_AMOUNT]
    else:
        result = f'i{LOOPS_AMOUNT - len(loops_variables)}'
    LOOPS_AMOUNT += 1
    return result


@register_alg_node('LOOP_START')
class AlgNode_LoopStart(AlgNode):
    node_type = 'LOOP_START'
    label = "LoopStart"
    GraphicsNode_class = LoopStartGNode
    NodeContent_class = LoopContent
    def __init__(self, scene, inputs=[(1, SocketPosition.TOP_CENTER)],
                 outputs=[(2, SocketPosition.BOTTOM_CENTER)]):
        super().__init__(scene, inputs, outputs)

