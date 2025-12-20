
from qfloweditor.alg_conf import register_alg_node
from qfloweditor.alg_node import AlgNode
from qfloweditor.shapes.rombus import RombusGNode
from qnodeeditor.serializable.socket import SocketPosition


@register_alg_node('CONDITION')
class AlgNode_Condition(AlgNode):
    node_type = 'CONDITION'
    label = "IF"
    GraphicsNode_class = RombusGNode
    def __init__(self, scene, inputs=[(1, SocketPosition.TOP_CENTER)],
                 outputs=[(2, SocketPosition.BOTTOM_CENTER),
                          (3, SocketPosition.RIGHT_CENTER)]):
        super().__init__(scene, inputs, outputs)
