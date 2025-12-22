import asyncio
import qasync
from qtpy.QtWidgets import QHBoxLayout
from qfloweditor.alg_conf import register_alg_node
from qfloweditor.alg_node import AlgNode
from qfloweditor.nodes.condition import AlgNode_Condition
from qfloweditor.nodes.dialog import AlgNode_Dialog
from qfloweditor.nodes.end import AlgNode_End
from qfloweditor.nodes.loop_end import AlgNode_LoopEnd
from qfloweditor.nodes.loop_start import AlgNode_LoopStart
from qfloweditor.shapes.rounded_rect import RoundedRectangleGNode
from qnodeeditor.serializable.content_widget import QDMNodeContentWidget
from qnodeeditor.serializable.node import Node
from qcustomwidgets import Button


class BeginContent(QDMNodeContentWidget):
    def initUI(self) -> None:
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)
        self.btn = Button('', [':svg/play', ':svg/pause'], flat=True, constant_color=True, iterate_icons=True)
        stop_btn = Button('', [':svg/stop'], flat=True, constant_color=True)
        update_btn = Button('', [':svg/update'], flat=True)
        self._layout.addWidget(self.btn)
        self._layout.addWidget(update_btn)
        self._layout.addWidget(stop_btn)
        self.btn.clicked.connect(self.on_start)
        stop_btn.clicked.connect(self.on_stop)
        self._routine_task = None
        self._need_refresh = set()
        self._loops = []

    def on_stop(self):
        if self._routine_task is not None:
            self._routine_task.cancel()
            self._routine_task = None

    @qasync.asyncSlot()
    async def on_start(self):
        self._routine_task = asyncio.create_task(self.routine())
        await self._routine_task
        self.refresh_nodes()
        self.btn.set_state(0)

    def refresh_nodes(self):
        for node in self._need_refresh:
            node.content.refresh()
        self._need_refresh.clear()
        self._loops.clear()

    async def routine(self):
        if not self.node.getChildrenNodes():
            return
        next_node: Node = self.node.getChildrenNodes()[0]
        while True:
            node: Node = next_node
            print(f'Executing {node}')
            node.doSelect(True)
            try:
                result: bool = await node.do_routine()
            except Exception as err:
                print(err)
                return
            node.doSelect(False)
            try:
                match node:
                    case AlgNode_Condition():
                        branches = node.getChildrenNodes()
                        if len(branches) == 2:
                            if result:
                                next_node = branches[0]
                            else:
                                next_node = branches[1]
                        else:
                            print('Condition incorrect')
                            return
                        continue
                    case AlgNode_LoopStart():
                        if node not in self._loops:
                            self._loops.append(node)
                        next_node = node.getChildrenNodes()[0]
                        continue
                    case AlgNode_LoopEnd():
                        self._need_refresh.add(node)
                        if len(self._loops):
                            parent_loop: Node = self._loops[-1]
                            if node.content.current_value + 1 < parent_loop.content.counter.value():  # type: ignore
                                node.content.increment()  # type: ignore
                                next_node = parent_loop
                                continue
                            else:
                                node.content.refresh()  # type: ignore
                                self._loops.pop()
                        next_node = node.getChildrenNodes()[0]
                        continue
                    case AlgNode_End():
                        print('Finished')
                        return
                    case AlgNode_Dialog():
                        if not result:
                            print('User aborted routine')
                            return
                        continue
                    case _:
                        next_node = node.getChildrenNodes()[0]
            except IndexError:
                print('Finished without End node')
                return


@register_alg_node('BEGIN')
class AlgNode_Begin(AlgNode):
    node_type = 'BEGIN'
    label = "Begin"
    GraphicsNode_class = RoundedRectangleGNode
    NodeContent_class = BeginContent
    def evalOperation(self, input1, input2):
        return input1 + input2
