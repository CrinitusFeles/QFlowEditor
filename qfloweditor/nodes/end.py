from qfloweditor.alg_conf import register_alg_node
from qfloweditor.alg_node import AlgNode
from qfloweditor.shapes.rounded_rect import RoundedRectangleGNode
from qnodeeditor.serializable.socket import SocketPosition


@register_alg_node('END')
class AlgNode_End(AlgNode):
    node_type = 'END'
    label = "End"
    GraphicsNode_class = RoundedRectangleGNode
    def __init__(self, scene, inputs=[(1, SocketPosition.TOP_CENTER)], outputs=[]):
        super().__init__(scene, inputs, outputs)
