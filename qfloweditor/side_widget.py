from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfloweditor.alg_conf import ALG_NODES, get_class_from_opcode
from qfloweditor.alg_node import AlgNode
from qfloweditor.drag_listbox import QDMDragListbox
from qcustomwidgets import Button
from qnodeeditor.color_picker import ColorPicker


class SideWidget(QWidget):
    def __init__(self, user_nodes: list[type[AlgNode]] | None = None):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self.buttons_layout = QHBoxLayout()
        self._layout.addLayout(self.buttons_layout)

        self.color_picker = ColorPicker()

        self.colors_btn = Button('', [':/svg/editor'], flat=True,
                                 constant_color=True, tooltip='Open color editor')
        self.colors_btn.clicked.connect(self.on_colors_clicked)
        self.create_btn = Button('', [':/svg/new-file'], flat=True,
                                 tooltip='Create new algorithm ( Ctrl+N )')
        self.open_btn = Button('', [':/svg/open'], flat=True,
                               tooltip='Open algorithm ( Ctrl+O )')
        self.save_btn = Button('', [':/svg/save'], flat=True,
                               tooltip='Save current algorithm ( Ctrl+S )')
        self.align_btn = Button('', [':/svg/content'], flat=True,
                                tooltip='Align selected nodes ( Ctrl+Shift+A )')
        self.edges_btn = Button('', [':/svg/tle_calculate'], flat=True,
                                tooltip='Create edges for selected nodes ( Ctrl+Shift+E )')
        self.buttons_layout.addWidget(self.colors_btn)
        self.buttons_layout.addWidget(self.create_btn)
        self.buttons_layout.addWidget(self.open_btn)
        self.buttons_layout.addWidget(self.save_btn)
        self.buttons_layout.addWidget(self.align_btn)
        self.buttons_layout.addWidget(self.edges_btn)
        nodes: list[type[AlgNode]] = [get_class_from_opcode(op_code) for op_code in ALG_NODES.keys()]
        self.nodes_list = QDMDragListbox(nodes)
        self._layout.addWidget(self.nodes_list)
        if user_nodes:
            self.user_nodes_list = QDMDragListbox([])
            self._layout.addWidget(self.user_nodes_list)

    def on_colors_clicked(self):
        self.color_picker.show()
        self.color_picker.raise_()
