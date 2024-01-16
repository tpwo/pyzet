from __future__ import annotations

import logging
import os
import re
import subprocess
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import pyzet.constants as C
from pyzet.exceptions import CreateNewZettel
from pyzet.grep import parse_grep_patterns
from pyzet.utils import Config
from pyzet.utils import get_git_output


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
    items: list[Zettel] = []
    for item in sorted(path.iterdir(), reverse=is_reversed):
        if item.is_dir():
            try:
                items.append(get_from_dir(item))
                logging.debug('get_all: found %s', items[-1])
            except FileNotFoundError:
                logging.warning("empty zet folder '%s' detected", item.name)
            except ValueError:
                # Skips dirs with different naming convention and skips
                # zettels without a text in the first line (i.e. during
                # editing).
                logging.debug("get_zettels: ValueError '%s'", item.absolute())
    if items == []:
        raise SystemExit('ERROR: there are no zettels at given repo.')
    return items


def get_from_grep(
    args: Namespace, config: Config, create_if_not_found: bool = True
) -> Zettel:
    if _patterns_empty(args.patterns):
        msg = 'ERROR: provided patterns are incorrect (empty or whitespace)'
        raise SystemExit(msg)
    opts = ['-I', '--all-match', '--name-only']
    if args.ignore_case:
        opts.append('--ignore-case')
    opts.extend(
        [*parse_grep_patterns(args.patterns), '--', f'*/{C.ZETTEL_FILENAME}']
    )
    try:
        out = get_git_output(config, 'grep', opts).decode()
    except subprocess.CalledProcessError:
        if create_if_not_found:
            try:
                if input('No zettels found. Create a new one? (y/N) ') != 'y':
                    raise SystemExit('aborting')
            except KeyboardInterrupt:
                raise SystemExit('\naborting')
            else:
                raise CreateNewZettel
        else:
            raise SystemExit('ERROR: no zettels found')

    matches: dict[int, Zettel] = {}
    for idx, filename in enumerate(out.splitlines(), start=1):
        matches[idx] = get(Path(config.repo, filename))

    num_matches = len(matches)
    confirmation_threshold = 50
    if num_matches > confirmation_threshold:
        prompt = f'Found {num_matches} matches. Continue? (y/N): '
        try:
            if input(prompt) != 'y':
                raise SystemExit('aborting')
        except KeyboardInterrupt:
            raise SystemExit('\naborting')

    print(f'Found {num_matches} matches:')
    zero_padding = len(str(num_matches))
    for idx, zet in matches.items():
        print(f'[{str(idx).zfill(zero_padding)}] {get_repr(zet, args)}')

    if num_matches == 1:
        try:
            if input('Continue? (Y/n): ') != 'n':
                return matches[1]
        except KeyboardInterrupt:
            raise SystemExit('\naborting')
        else:
            raise SystemExit('aborting')
    try:
        user_input = input('Open (press enter to cancel): ')
    except KeyboardInterrupt:
        raise SystemExit('\naborting')

    if user_input == '':
        raise SystemExit('aborting')

    try:
        return matches[int(user_input)]
    except KeyError:
        raise SystemExit('ERROR: wrong zettel ID')


def _patterns_empty(patterns: list[str]) -> bool:
    """Returns True if all provided patterns are empty str or whitespace."""
    return all('' == s or s.isspace() for s in patterns)


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

    zettel = Zettel(
        id=id_,
        title=get_markdown_title(title_line.strip(), id_),
        path=path,
        tags=tags,
    )
    logging.debug('zettel.get: %s', zettel)
    return zettel


def get_repr(zet: Zettel, args: Namespace) -> str:
    tags = ''
    if args.tags:
        try:
            tags = f'  [{get_tags_str(zet)}]'
        except ValueError:  # No tags found
            pass
    if args.pretty:
        return f'{get_timestamp(zet.id)} -- {zet.title}{tags}'
    try:
        if args.link:
            return get_md_link(zet)
    except AttributeError:  # 'Namespace' object has no attribute 'link'
        pass
    return f'{zet.id} -- {zet.title}{tags}'


def get_timestamp(id_: str) -> datetime:
    """Parses zettel ID into a datetime object."""
    return datetime.strptime(id_, C.ZULU_DATETIME_FORMAT)


def get_md_link(zet: Zettel) -> str:
    """Returns a representation of a zettel that is a relative Markdown link.

    Asterisk at the beginning is a Markdown syntax for an unordered list,
    as links to zettels are usually just used in references section of a
    zettel.
    """
    return f'* [{zet.id}](../{zet.id}) {zet.title}'


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
        logging.warning('wrong title formatting: %s "%s"', id_, title_line)
        return title_line
    res = result.groups()[0]
    logging.debug("get_markdown_title: '%s' -> '%s'", title_line, res)
    return res


def get_tags(line: str) -> tuple[str, ...]:
    """Parses tags from a line of text."""
    tags = tuple(sorted(tag.lstrip('#') for tag in line.split()))
    logging.debug('get_tags: got %s', tags)
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
