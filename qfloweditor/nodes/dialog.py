import asyncio
from qtpy.QtWidgets import QMessageBox, QStyle, QDialog
from qtpy.QtGui import QFont
from qfloweditor.alg_conf import register_alg_node
from qfloweditor.alg_node import AlgNode
from qfloweditor.shapes.trapeze import TrapezeGNode
from qnodeeditor.scene.models import ContentModel
from qnodeeditor.serializable.content_widget import QDMNodeContentWidget, QDMTextEdit
from qnodeeditor.serializable.socket import SocketPosition


class DialogModel(ContentModel):
    message: str


class DialogContent(QDMNodeContentWidget):
    ContentModelClass = DialogModel
    def initUI(self):
        self.text_edit = QDMTextEdit(self)
        self.text_edit.setGeometry(40, 10, 250, 40)

        font = QFont('Consolas', 12)
        self.text_edit.setFont(font)

    def serialize(self, **kwargs) -> DialogModel:  # type: ignore
        return super().serialize(message=self.text_edit.toPlainText(), **kwargs)  # type: ignore

    def deserialize(self, data: dict, hashmap: dict):  # type: ignore
        try:
            model = DialogModel(**data)
            self.text_edit.setText(model.message)
            return True
        except Exception as e:
            print(e)
        return False


def dialog_async_exec(dialog: QDialog):
    future = asyncio.Future()
    dialog.finished.connect(lambda r: future.set_result(r))
    dialog.open()
    return future


async def UserDialog(command_name: str):
    msg = QMessageBox()
    msg_btn = QMessageBox.StandardButton
    msg.setStandardButtons(msg_btn.Ok | msg_btn.Abort)
    msg.setWindowTitle('Инструкция оператору')
    msg.setText(f'{command_name}')
    msg.setIcon(QMessageBox.Icon.Question)
    style = msg.style()
    if style:
        icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        msg.setWindowIcon(icon)

    btn = await dialog_async_exec(msg)
    return btn == msg_btn.Ok


@register_alg_node('DIALOG')
class AlgNode_Dialog(AlgNode):
    node_type = 'DIALOG'
    label = "Dialog"
    GraphicsNode_class = TrapezeGNode
    NodeContent_class = DialogContent
    def __init__(self, scene, inputs=[(1, SocketPosition.TOP_CENTER)],
                 outputs=[(2, SocketPosition.BOTTOM_CENTER)]):
        super().__init__(scene, inputs, outputs)

    def evalOperation(self, input1, input2):
        return input1 + input2

    async def do_routine(self):
        return await UserDialog(self.content.text_edit.toPlainText())  # type: ignore
