from qtpy.QtCore import QDataStream, QIODevice, Qt
from qtpy.QtWidgets import QAction, QGraphicsProxyWidget, QMenu
from qfloweditor.alg_conf import ALG_NODES, get_class_from_opcode, LISTBOX_MIMETYPE
from qnodeeditor.editor_widget import NodeEditorWidget
from qnodeeditor.edge.edge import EdgeType
from qnodeeditor.graphics.view import MODE_EDGE_DRAG
from qnodeeditor.utils import dumpException
from qnodeeditor.serializable.node import Node


class AlgorithmsSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setTitle()

        self.initNewNodeActions()
        self.view.dragging.edge_type = EdgeType.EDGE_TYPE_SQUARE

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self._close_event_listeners = []

    def getNodeClassFromData(self, data: dict):
        if 'node_type' not in data:
            return Node
        return get_class_from_opcode(data['node_type'])

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(ALG_NODES.keys())
        for key in keys:
            node = ALG_NODES[key]
            self.node_actions[node.node_type] = QAction(node.label)
            self.node_actions[node.node_type].setData(node.node_type)

    def initNodesContextMenu(self):
        context_menu = QMenu(self)
        keys = list(ALG_NODES.keys())
        for key in keys:
            try:
                context_menu.addAction(self.node_actions[key])
            except KeyError:
                ...
        return context_menu

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self._close_event_listeners.append(callback)

    def closeEvent(self, a0):
        for callback in self._close_event_listeners:
            callback(self, a0)

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            # print(" ... denied drag enter event")
            event.setAccepted(False)

    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.OpenModeFlag.ReadOnly)
            node_type: str = dataStream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            try:
                node = get_class_from_opcode(node_type)(self.scene)
                node.setPos(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory(f"Created node {node.__class__.__name__}")
            except Exception as e:
                dumpException(e)


            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()


    def contextMenuEvent(self, a0):
        if not a0:
            return
        try:
            item = self.scene.getItemAt(a0.pos())

            if isinstance(item, QGraphicsProxyWidget):
                item = item.widget()
            #elif item is None:
            else:
                self.handleNewNodeContextMenu(a0)

            return super().contextMenuEvent(a0)
        except Exception as e:
            dumpException(e)

    # helper functions
    def determine_target_socket_of_node(self, was_dragged_flag: bool, new_node):
        target_socket = None
        if was_dragged_flag:
            if len(new_node.inputs) > 0:
                target_socket = new_node.inputs[0]
        else:
            if len(new_node.outputs) > 0:
                target_socket = new_node.outputs[0]
        return target_socket

    def finish_new_node_state(self, new_node):
        self.scene.doDeselectItems()
        new_node.grNode.doSelect(True)
        new_node.grNode.onSelected()

    def handleNewNodeContextMenu(self, event):
        context_menu = self.initNodesContextMenu()
        action = context_menu.exec(self.mapToGlobal(event.pos()))

        if action is not None:
            new_node = get_class_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_node.setPos(scene_pos.x(), scene_pos.y())

            if self.scene.getView().mode == MODE_EDGE_DRAG:
                # if we were dragging an edge...
                flag = self.scene.getView().dragging.drag_start_socket.is_output  # type: ignore
                target_socket = self.determine_target_socket_of_node(flag, new_node)
                if target_socket is not None:
                    self.scene.getView().dragging.edgeDragEnd(target_socket.grSocket)
                    self.finish_new_node_state(new_node)

            else:
                self.scene.history.storeHistory("Created %s" % new_node.__class__.__name__)
