
from qfloweditor.alg_conf import register_alg_node
from qfloweditor.alg_node import AlgNode
from qfloweditor.shapes.parallelogram import ParallelogramGNode
from qnodeeditor.serializable.socket import SocketPosition


@register_alg_node('EXTRA')
class AlgNode_Extra(AlgNode):
    node_type = 'EXTRA'
    label = "PrintLog"
    GraphicsNode_class = ParallelogramGNode
    def __init__(self, scene, inputs=[(1, SocketPosition.TOP_CENTER)],
                 outputs=[(2, SocketPosition.BOTTOM_CENTER)]):
        super().__init__(scene, inputs, outputs)