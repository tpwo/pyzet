from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import pyzet.constants as C


class Zettel(NamedTuple):
    title: str
    id_: str
    tags: tuple[str, ...]
    path: Path


def get_zettels(path: Path, is_reversed: bool = False) -> list[Zettel]:
    if not path.is_dir():
        raise SystemExit(f"ERROR: folder {path} doesn't exist.")
    items = []
    for item in sorted(path.iterdir(), reverse=is_reversed):
        if item.is_dir():
            try:
                items.append(get_zettel(item))
                logging.debug(
                    f"get_zettels: zettel appended '{item.absolute()}'"
                )
            except FileNotFoundError:
                logging.warning(f"empty zet folder '{item.name}' detected")
            except ValueError:
                # Skips dirs with different naming convention and skips
                # zettels without a text in the first line (i.e. during
                # editing).
                logging.debug(
                    f"get_zettels: ValueError at '{item.absolute()}'"
                )
    if items == []:
        raise SystemExit('ERROR: there are no zettels at given repo.')
    return items


def get_zettel(path: Path) -> Zettel:
    if path.name == C.ZETTEL_FILENAME:
        md_path = path
        id_ = path.parent.name
    else:
        md_path = Path(path, C.ZETTEL_FILENAME)
        id_ = path.name

    title_line, tags_line = _get_first_and_last_line(md_path)
    title = get_markdown_title(title_line.strip(), md_path.name)
    tags = get_tags(tags_line.strip()) if tags_line.startswith(4 * ' ') else ()
    logging.debug(f"get_zettel: '{md_path.name}' with title '{title}'")
    return Zettel(title=title, id_=id_, tags=tags, path=md_path)


def _get_first_and_last_line(path: Path) -> tuple[str, str]:
    """Gets the first and the last line from a given file.

    It uses file.seek() to look from the end of the file. It's fast but
    requires the file to be opened in binary mode.

    Reference:
    https://stackoverflow.com/a/54278929/14458327
    """
    with open(path, 'rb') as file:
        title_line = file.readline().decode('utf-8')
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:  # file has only a single line
            file.seek(0)
        tags_line = file.readline().decode('utf-8')
    return title_line, tags_line


def get_timestamp(id_: str) -> datetime:
    return datetime.strptime(id_, C.ZULU_DATETIME_FORMAT)


def get_markdown_title(title_line: str, id_: str) -> str:
    """Extracts Markdown title if it is formatted correctly.

    Otherwise, returns the whole line and logs a warning. 'title_line'
    arg should have newline characters stripped.

    Raises ValueError if empty or whitespace only title is given as
    input.
    """
    if title_line == '':
        raise ValueError('Empty zettel title found')
    result = re.match(C.MARKDOWN_TITLE, title_line)
    if not result:
        logging.warning(f'wrong title formatting: {id_} "{title_line}"')
        return title_line
    res = result.groups()[0]
    logging.debug(f"get_markdown_title: '{title_line}' -> '{res}'")
    return res


def get_tags(line: str) -> tuple[str, ...]:
    tags = tuple(sorted(tag.lstrip('#') for tag in line.split()))
    logging.debug(f'get_tags: extracted {tags}')
    return tags


def get_printable_tags(zettel: Zettel) -> str:
    if zettel.tags == tuple():
        raise ValueError
    else:
        return '#' + ' #'.join(zettel.tags)
