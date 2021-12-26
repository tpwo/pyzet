from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from pyzet.constants import (
    MARKDOWN_TITLE,
    ZETTEL_FILENAME,
    ZETTEL_WIDTH,
    ZULU_DATETIME_FORMAT,
)


@dataclass
class Zettel:
    title: str
    id_: str
    text: list[str]
    timestamp: datetime | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = _get_timestamp(self.id_)


def get_zettels(path: Path, is_reversed: bool = False) -> list[Zettel]:
    items = []
    for item in sorted(path.iterdir(), reverse=is_reversed):
        if item.is_dir():
            try:
                items.append(get_zettel(item))
            except FileNotFoundError:
                logging.warning(f"empty zet folder {item.name} detected")
            except ValueError:
                pass  # skip dirs with different naming convention
    return items


def get_zettel(path: Path) -> Zettel:
    timestamp = _get_timestamp(path.name)
    with open(Path(path, ZETTEL_FILENAME), "r", encoding="utf-8") as file:
        contents = file.readlines()
    try:
        title_raw = contents[0].strip("\n")
    except IndexError:  # We raise ValueError, so it's intercepted by get_zettels()
        raise ValueError("Empty zettel found, are you in progress of `pyzet add`?")
    title = get_markdown_title(title_raw, path.name)
    tags = get_tags(contents[-1].strip()) if contents[-1].startswith(4 * " ") else []
    return Zettel(
        title=title, id_=path.name, text=contents, timestamp=timestamp, tags=tags
    )


def _get_timestamp(id_: str) -> datetime:
    return datetime.strptime(id_, ZULU_DATETIME_FORMAT)


def print_zettel(zet: Zettel) -> None:
    """Prints zettel text prepended with centered ID as a header."""
    print(f" {zet.id_} ".center(ZETTEL_WIDTH, "="))
    [print(line, end="") for line in zet.text]


def get_markdown_title(line: str, id_: str) -> str:
    """Extracts Markdown title if it is formatted correctly.

    Otherwise, returns the whole line and logs a warning.
    `line` arg should have newline characters stripped.
    """
    result = re.match(MARKDOWN_TITLE, line)
    if not result:
        logging.warning(f'wrong title formatting: {id_} "{line}"')
        return line

    return result.groups()[0]


def get_tags(line: str) -> list[str]:
    tags = []
    for tag in line.split():
        tags.append(tag.lstrip("#"))
    return tags
