from functools import partial
from typing import Type

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qfloweditor.alg_node import AlgNode


LISTBOX_MIMETYPE = "application/x-item"


ALG_NODES: dict[str, Type['AlgNode']] = {}


class AlgConfException(Exception):
    pass
class AlgInvalidNodeRegistration(AlgConfException):
    pass
class AlgOpCodeNotRegistered(AlgConfException):
    pass


def register_alg_node_now(node_type: str, class_reference: Type['AlgNode']):
    if node_type in ALG_NODES:
        raise AlgInvalidNodeRegistration(f"Duplicate node registration of "
                                         f"{node_type}. There is already {ALG_NODES[node_type]}")
    ALG_NODES[node_type] = class_reference


def register_alg_node(node_type: str):
    def decorator(original_class: Type['AlgNode']):
        register_alg_node_now(node_type, original_class)
        return original_class
    return decorator


def get_class_from_opcode(node_type: str):
    if node_type not in ALG_NODES:
        raise AlgOpCodeNotRegistered(f"OpCode {node_type} is not registered")
    return ALG_NODES[node_type]



# import all nodes and register them
# from qfloweditor.nodes import *
from qfloweditor.nodes import *   # noqa: E402, F403
