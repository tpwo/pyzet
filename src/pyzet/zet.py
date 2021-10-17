from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from pyzet.constants import ZET_FILENAME, ZULU_DATETIME_FORMAT


@dataclass
class Zet:
    title: str
    timestamp: datetime


def get_zets(path: Path) -> List[Zet]:
    items = []
    for item in path.iterdir():
        if item.is_dir():
            try:
                items.append(get_zet(item))
            except ValueError:
                pass  # skip dirs with different naming convention

    return items


def get_zet(path: Path) -> Zet:
    timestamp = datetime.strptime(path.name, ZULU_DATETIME_FORMAT)
    with open(Path(path, ZET_FILENAME), "r") as file:
        title = _get_markdown_title(file.readline())
    return Zet(title=title, timestamp=timestamp)


def _get_markdown_title(line: str) -> str:
    if line.startswith("#"):
        return line.lstrip("#").strip()

    raise ValueError("Zet doesn't start with Markdown title (`#`)")
