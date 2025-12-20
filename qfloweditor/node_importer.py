


import json
from pathlib import Path
from typing import Protocol


def import_custom_commands(filepath: Path):
    data: list[dict] = []
    with open(filepath, 'r+', encoding='utf-8') as file:
        data = json.load(file)
        if not isinstance(data, list):
            print('Incorrect foramt')
            return []

    for cmd in data:
        if not hasattr(cmd, 'sha256'):
            print('Imported CMD does not have sha256 field')
            return []

class NodeProtocol(Protocol):
    label: str
    sha256: str
    mode: str
    async def write_transaction(self) -> bool:
        ...

    async def read_transaction(self) -> tuple[bool, bytes]:
        ...