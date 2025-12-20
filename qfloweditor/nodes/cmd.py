

from qfloweditor.alg_conf import register_alg_node
from qfloweditor.alg_node import AlgNode
from qnodeeditor.serializable.socket import SocketPosition


@register_alg_node('CMD')
class AlgNode_CMD(AlgNode):
    node_type = 'CMD'
    label = "CMD"

    def __init__(self, scene, inputs=[(1, SocketPosition.TOP_CENTER)],
                 outputs=[(2, SocketPosition.BOTTOM_CENTER)]):
        super().__init__(scene, inputs, outputs)
