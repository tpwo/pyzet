from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import pyzet.constants as C


class Zettel(NamedTuple):
    """Represents a single zettel.

    Zettel contents are skipped for performance reasons.
    """

    title: str
    id: str
    tags: tuple[str, ...]
    path: Path


def get_all(path: Path, is_reversed: bool = False) -> list[Zettel]:
    """Gets all zettels from a given repo."""
    if not path.is_dir():
        raise SystemExit(f"ERROR: folder {path} doesn't exist.")
    items = []
    for item in sorted(path.iterdir(), reverse=is_reversed):
        if item.is_dir():
            try:
                items.append(get_from_dir(item))
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


def get_from_id(id_: str, repo: Path) -> Zettel:
    """Gets zettel from its ID given repo path."""
    try:
        return get_from_dir(Path(repo, C.ZETDIR, id_))
    except FileNotFoundError:
        raise SystemExit(f"ERROR: zettel '{id_}' doesn't exist.")


def get_last(repo: Path) -> Zettel:
    """Gets the last zettel from a given repo."""
    return get_all(Path(repo, C.ZETDIR), is_reversed=True)[0]


def get_from_dir(dirpath: Path) -> Zettel:
    """Gets zettel from a directory named after its ID."""
    return get(Path(dirpath, C.ZETTEL_FILENAME))


def get(path: Path) -> Zettel:
    """Gets zettel from a full path."""
    if path.is_dir():
        raise ValueError

    title_line, tags_line = _get_first_and_last_line(path)
    if title_line == '':
        raise ValueError

    if tags_line.startswith(4 * ' '):
        tags = get_tags(tags_line.strip())
    else:
        tags = tuple()

    id_ = path.parent.name

    return Zettel(
        id=id_,
        title=get_markdown_title(title_line, id_),
        path=path,
        tags=tags,
    )


def get_timestamp(id_: str) -> datetime:
    """Parses zettel ID into a datetime object."""
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
    """Parses tags from a line of text."""
    tags = tuple(sorted(tag.lstrip('#') for tag in line.split()))
    logging.debug(f'get_tags: extracted {tags}')
    return tags


def get_tags_str(zettel: Zettel) -> str:
    """Parses zettel tags into a printable repr."""
    if zettel.tags == tuple():
        raise ValueError
    else:
        return '#' + ' #'.join(zettel.tags)


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
