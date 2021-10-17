import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from pyzet.constants import MARKDOWN_TITLE, ZET_FILENAME, ZULU_DATETIME_FORMAT


@dataclass
class Zet:
    title: str
    id_: datetime
    text: List[str]


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
        contents = file.readlines()
    title = get_markdown_title(contents[0].strip("\n"), path.name)
    return Zet(title=title, id_=timestamp, text=contents)


def print_zet(zet: Zet) -> None:
    for line in zet.text:
        print(line, end="")


def get_markdown_title(line: str, id_: str) -> str:
    """Extracts Markdown title if it is formatted correctly.

    Otherwise, returns the whole line and logs a warning.
    `line` arg should have newline characters stripped.
    """
    result = re.match(MARKDOWN_TITLE, line)
    if not result:
        logging.warning(f"wrong title formatting: {id_} {line}")
        return line

    return result.groups()[0]
