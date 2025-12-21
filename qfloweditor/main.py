import asyncio
import os
import sys
from PyQt6.QtGui import QCloseEvent
from qtpy.QtWidgets import QApplication
from qasync import QEventLoop
import signal
sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

from qfloweditor.window import AlgorithmsWindow
from qmodernwindow import ModernWindow
from qcustomwindow import CustomWindow


class SimpleWindow(CustomWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle('Algorithm editor')
        self.editor = AlgorithmsWindow()
        self.editor.onFileNew()
        self.addWidget(self.editor)


class MainWindow(ModernWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle('Algorithm editor')
        self.editor = AlgorithmsWindow()
        self.editor.onFileNew()
        self.addWidget(self.editor)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.editor.closeEvent(a0)
        return super().closeEvent(a0)

if __name__ == '__main__':
    app = QApplication([])
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    w = SimpleWindow()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    w.show()

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())
