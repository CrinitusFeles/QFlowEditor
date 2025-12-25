import json
from typing import Callable
from PyQt6.QtGui import QShortcut
from qtpy.QtGui import QIcon, QKeySequence
from qtpy.QtWidgets import QMdiArea, QDockWidget, QFileDialog, QMainWindow, QMessageBox, QVBoxLayout, QSplitter
from qtpy.QtCore import Qt, QEvent

from qnodeeditor.editor_widget import NodeEditorWidget
from qtpy.QtWidgets import QApplication
from qfloweditor.sub_window import AlgorithmsSubWindow
from qfloweditor.side_widget import SideWidget
from qnodeeditor.utils import dumpException

# Enabling edge validators
from qnodeeditor.edge.edge import Edge
from qnodeeditor.edge.validators import (
    edge_validator_debug,
    edge_cannot_connect_two_outputs_or_two_inputs,
    edge_cannot_connect_input_and_output_of_same_node
)
Edge.registerEdgeValidator(edge_validator_debug)
Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)


class AlgorithmsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.empty_icon = QIcon(".")

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.node_class_selector: Callable | None = None

        self.side_widget = SideWidget()
        self.side_widget.create_btn.clicked.connect(self.onFileNew)
        self.side_widget.open_btn.clicked.connect(self.onFileOpen)
        self.side_widget.save_btn.clicked.connect(self.onFileSaveAs)
        self.side_widget.align_btn.clicked.connect(self.onAlign)
        self.side_widget.edges_btn.clicked.connect(self.onEdges)
        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.side_widget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.nodesDock)
        self.createShortcuts()

    def createShortcuts(self):
        save = QShortcut(QKeySequence('Ctrl+S'), self, self.onFileSave)
        new = QShortcut(QKeySequence('Ctrl+N'), self, self.onFileNew)
        save_as = QShortcut(QKeySequence('Ctrl+Shift+S'), self, self.onFileSaveAs)
        openfile = QShortcut(QKeySequence('Ctrl+O'), self, self.onFileOpen)
        close_editor = QShortcut(QKeySequence('Ctrl+W'), self, self.onSubWndClose)
        copy = QShortcut(QKeySequence('Ctrl+C'), self, self.onEditCopy)
        paste = QShortcut(QKeySequence('Ctrl+V'), self, self.onEditPaste)
        undo = QShortcut(QKeySequence('Ctrl+Z'), self, self.onEditUndo)
        redo = QShortcut(QKeySequence('Ctrl+Shift+Z'), self, self.onEditRedo)
        cut = QShortcut(QKeySequence('Ctrl+X'), self, self.onEditCut)
        delete = QShortcut(QKeySequence('Del'), self, self.onEditDelete)
        align = QShortcut(QKeySequence('Ctrl+Shift+A'), self, self.onAlign)
        edge = QShortcut(QKeySequence('Ctrl+Shift+E'), self, self.onEdges)

    def closeEvent(self, a0):
        if not a0:
            return super().closeEvent(a0)
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            a0.ignore()
        else:
            if not self.maybeSave():
                a0.ignore()
        return super().closeEvent(a0)

    def getCurrentNodeEditorWidget(self) -> NodeEditorWidget | None:  # type: ignore
        """ we're returning NodeEditorWidget here... """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()  # type: ignore
        return None

    def onFileNew(self):
        try:
            subwnd = self.createMdiChild()
            subwnd.widget().fileNew()  # type: ignore
            subwnd.show()
        except Exception as e:
            dumpException(e)


    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter())

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # we need to create new subWindow and open the file
                        nodeeditor = AlgorithmsSubWindow()
                        if self.node_class_selector:
                            nodeeditor.setNodeClassSelector(self.node_class_selector)
                        if nodeeditor.fileLoad(fname):
                            nodeeditor.setTitle()
                            subwnd = self.createMdiChild(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()
        except Exception as e:
            dumpException(e)

    def createMdiChild(self, child_widget=None):
        nodeeditor = child_widget if child_widget is not None else AlgorithmsSubWindow()
        if self.node_class_selector is not None:
            nodeeditor.setNodeClassSelector(self.node_class_selector)
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        if not subwnd:
            raise RuntimeError('Subwindow is None')
        subwnd.setWindowIcon(self.empty_icon)
        # nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        # nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        # nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def onSubWndClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def findMdiChild(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:  # type: ignore
                return window
        return None


    def isModified(self) -> bool:
        """Has current :class:`~nodeeditor.node_scene.Scene` been modified?

        :return: ``True`` if current :class:`~nodeeditor.node_scene.Scene` has been modified
        :rtype: ``bool``
        """
        nodeeditor = self.getCurrentNodeEditorWidget()
        return nodeeditor.scene.isModified() if nodeeditor else False


    def maybeSave(self) -> bool:
        """If current `Scene` is modified, ask a dialog to save the changes. Used before
        closing window / mdi child document

        :return: ``True`` if we can continue in the `Close Event` and shutdown. ``False`` if we should cancel
        :rtype: ``bool``
        """
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "About to loose your work?",
                "The document has been modified.\n Do you want to save your changes?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
              )

        if res == QMessageBox.StandardButton.Save:
            return self.onFileSave()
        elif res == QMessageBox.StandardButton.Cancel:
            return False

        return True

    def getFileDialogDirectory(self):
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''

    def getFileDialogFilter(self):
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'Graph (*.json);;All files (*)'

    def onFileSave(self) -> bool:
        """Handle File Save operation"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet():
                return self.onFileSaveAs()

            current_nodeeditor.fileSave()

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()   # type: ignore
            else:
                self.setTitle()
            return True
        return False

    def setTitle(self):
        """Function responsible for setting window title"""
        editor = self.getCurrentNodeEditorWidget()
        if not editor:
            return
        title = "Node Editor - "
        title += editor.getUserFriendlyFilename()

        self.setWindowTitle(title)

    def onFileSaveAs(self) -> bool:
        """Handle File Save As operation"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            # current_nodeeditor.save_svg()
            fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file', self.getFileDialogDirectory(), self.getFileDialogFilter())
            if fname == '':
                return False

            self.onBeforeSaveAs(current_nodeeditor, fname)
            current_nodeeditor.fileSave(fname)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()   # type: ignore
            else:
                self.setTitle()
            return True
        return False

    def onBeforeSaveAs(self, current_nodeeditor: 'NodeEditorWidget', filename: str):
        """
        Event triggered after choosing filename and before actual fileSave(). We are passing current_nodeeditor because
        we will loose focus after asking with QFileDialog and therefore getCurrentNodeEditorWidget will return None
        """
        pass

    def onTabClose(self):
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            self.onSubWndClose(editor, QEvent.Type.Close)

    def onEditUndo(self):
        """Handle Edit Undo operation"""
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            editor.scene.history.undo()

    def onEditRedo(self):
        """Handle Edit Redo operation"""
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            editor.scene.history.redo()

    def onEditDelete(self):
        """Handle Delete Selected operation"""
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            editor.scene.getView().deleteSelected()

    def onAlign(self):
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            editor.scene.verticalAlignSelected()

    def onEdges(self):
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            editor.scene.connectSelected()

    def onEditCut(self):
        """Handle Edit Cut to clipboard operation"""
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            data = editor.scene.clipboard.serializeSelected(delete=True)
            str_data: str = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)  # type: ignore

    def onEditCopy(self):
        """Handle Edit Copy to clipboard operation"""
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            data = editor.scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)   # type: ignore

    def onEditPaste(self):
        """Handle Edit Paste from clipboard operation"""
        editor = self.getCurrentNodeEditorWidget()
        if editor:
            raw_data = QApplication.instance().clipboard().text()   # type: ignore

            try:
                data = json.loads(raw_data)
            except ValueError as e:
                print("Pasting of not valid json data!", e)
                return

            # check if the json data are correct
            if 'nodes' not in data:
                print("JSON does not contain any nodes!")
                return

            return editor.scene.clipboard.deserializeFromClipboard(data)
