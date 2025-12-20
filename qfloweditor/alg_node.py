from qfloweditor.shapes.rectangle import RectangleGNode
from qnodeeditor.edge.edge import Serializable
from qnodeeditor.serializable.node import Node, NodeModel
from qnodeeditor.serializable.content_widget import QDMNodeContentWidget
from qnodeeditor.serializable.socket import SocketPosition


class AlgContent(QDMNodeContentWidget):
    def initUI(self):
        ...


class AlgNodeModel(NodeModel):
    node_type: str


class AlgNode(Node, Serializable[AlgNodeModel]):
    node_type: str = 'DEFAULT'
    label: str = "Undefined"

    GraphicsNode_class = RectangleGNode
    NodeContent_class = AlgContent
    ModelClass = AlgNodeModel

    def __init__(self, scene, inputs=[], outputs=[(3, SocketPosition.BOTTOM_CENTER)]):
        super().__init__(scene, self.__class__.label, inputs, outputs)
        self.output_multi_edged = False

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = SocketPosition.TOP_CENTER
        self.output_socket_position = SocketPosition.BOTTOM_CENTER

    def serialize(self, **kwargs) -> AlgNodeModel:
        return super().serialize(node_type=self.__class__.node_type, **kwargs)

    def deserialize(self, data: dict, hashmap: dict,  # type: ignore
                    restore_id = True):
        res = super().deserialize(data, hashmap, restore_id)
        return res